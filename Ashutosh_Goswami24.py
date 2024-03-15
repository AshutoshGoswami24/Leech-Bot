import re
import logging
import subprocess
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from config import *
# Initialize the bot
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define a command handler
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Send me a URL and I will download the file.")

# Define a message handler for URLs
@app.on_message(filters.regex(r'(https?://\S+)'))
async def url_handler(client, message: Message):
    url = message.matches[0].group(1)
    await aria2_download(url, message)

# Function to download the file using aria2c
async def aria2_download(url: str, message: Message):
    try:
        name_d = get_aria2c_name(url)
        task_start = datetime.now()
        status_head = f"<b>📥 DOWNLOADING FROM URL:</b> <i>{url}</i>\n\n<b>🏷️ Name:</b> <code>{name_d}</code>\n"

        # Create a command to run aria2p with the link
        command = [
            "aria2c",
            "-x16",
            "--seed-time=0",
            "--summary-interval=1",
            "--max-tries=3",
            "--console-log-level=notice",
            "-d",
            "/path/to/save",
            url,
        ]

        # Run the command using subprocess.Popen
        proc = subprocess.Popen(command, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Read and print output in real-time
        while True:
            output = proc.stdout.readline()
            if output == b"" and proc.poll() is not None:
                break
            if output:
                await on_output(output.decode("utf-8"), message, task_start, status_head)

        # Retrieve exit code and any error output
        exit_code = proc.wait()
        error_output = proc.stderr.read()
        if exit_code != 0:
            if exit_code == 3:
                logging.error(f"The Resource was Not Found in {url}")
            elif exit_code == 9:
                logging.error(f"Not enough disk space available")
            elif exit_code == 24:
                logging.error(f"HTTP authorization failed.")
            else:
                logging.error(f"aria2c download failed with return code {exit_code} for {url}.\nError: {error_output}")

        # Upload the downloaded file
        await upload_file("/path/to/save", message.chat.id)

    except Exception as e:
        logging.error(f"Error downloading file: {e}")

# Function to get the name of the file being downloaded
def get_aria2c_name(url: str):
    # Logic to extract and return the file name from the URL
    return "Unknown"

# Function to handle output from aria2c
async def on_output(output: str, message: Message, task_start: datetime, status_head: str):
    # Process and send the output message
    pass  # Implement your logic here

# Function to upload the downloaded file
async def upload_file(file_path: str, chat_id: int):
    await app.send_document(chat_id=chat_id, document=file_path)

# Start the bot
app.run()
