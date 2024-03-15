import os
import logging
import subprocess
from datetime import datetime
from pyrogram import Client, filters
from config import *
# Initialize the bot
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define a command handler
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Send me a URL and I will download and upload the file for you.")

# Define a message handler for URLs
@app.on_message(filters.regex(r'(https?://\S+)'))
async def url_handler(client, message):
    url = message.matches[0].group(1)
    await download_and_upload(url, message)

# Define the function to download the file using aria2c and upload it
async def download_and_upload(url, message):
    task_start = datetime.now()
    command = [
        "aria2c",
        "-x16",
        "--seed-time=0",
        "--summary-interval=1",
        "--max-tries=3",
        "--console-log-level=notice",
        "--disable-ipv6",  # Disable IPv6 to avoid binding errors
        "-d",
        "/path/to/save",  # Specify the path where you want to save the downloaded file
        url,
    ]

    proc = subprocess.Popen(
        command, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    while True:
        output = proc.stdout.readline()
        if output == b"" and proc.poll() is not None:
            break
        if output:
            await message.reply_text(output.decode("utf-8").strip())

    exit_code = proc.wait()
    if exit_code == 0:
        await upload_file("/path/to/save", message)
    else:
        await message.reply_text("Download failed.")

# Define a function to upload the downloaded file
async def upload_file(file_path, message):
    await message.reply_text("Uploading file...")
    try:
        await app.send_document(
            chat_id=message.chat.id,
            document=file_path,
        )
        await message.reply_text("File uploaded successfully!")
    except Exception as e:
        await message.reply_text(f"Error uploading file: {e}")

# Start the bot
app.run()

