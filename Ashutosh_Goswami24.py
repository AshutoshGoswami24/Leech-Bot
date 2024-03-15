import re
import subprocess
import logging
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from config import *

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
app = Client("my_bot")

# Define a command handler
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Send me a URL and I will download and send you the file.")

# Define a message handler for URLs
@app.on_message(filters.regex(r'(https?://\S+)'))
async def url_handler(client, message):
    url = message.matches[0].group(1)
    await aria2_download(url, message)

# Define the function to download the file using aria2c
async def aria2_download(url: str, message: Message):
    task_start = datetime.now()
    status_head = f"<b>📥 DOWNLOADING FROM » </b><i>🔗 Link</i>\n\n<b>🏷️ Name » </b><code>Downloading File</code>\n"

    # Create a command to run aria2c with the link
    command = [
        "aria2c",
        "-x16",
        "--seed-time=0",
        "--summary-interval=1",
        "--max-tries=3",
        "--console-log-level=notice",
        "-d",
        "/path/to/save",  # Specify the path where you want to save the downloaded file
        url,
    ]

    # Run the command using subprocess.Popen
    proc = subprocess.Popen(
        command, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Read and print output in real-time
    while True:
        output = proc.stdout.readline()  # type: ignore
        if output == b"" and proc.poll() is not None:
            break
        if output:
            await message.reply_text(status_head + output.decode("utf-8").strip())

    # Wait for the process to finish
    proc.wait()

    # Check if download was successful
    if proc.returncode == 0:
        await upload_file("/path/to/save", message)
    else:
        await message.reply_text("Download failed.")

# Define a function to upload the downloaded file
async def upload_file(file_path: str, message: Message):
    await message.reply_text("Uploading file...")
    try:
        async with app.send_document(
            chat_id=message.chat.id,
            document=file_path,
            progress=progress_bar_upload,
        ) as progress:
            while progress < 100:
                await asyncio.sleep(5)
    except FloodWait as e:
        await asyncio.sleep(e.x)  # Wait for the suggested time before retrying
        await upload_file(file_path, message)
    except Exception as e:
        logging.error(f"Error uploading file: {e}")

# Define a function to track the progress of the file upload
async def progress_bar_upload(current, total):
    progress = (current / total) * 100
    return int(progress)

# Start the bot
app.run()
