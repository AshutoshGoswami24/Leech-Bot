import re
import subprocess
import logging
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from config import *

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define a command handler
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Send me a URL and I will download and send you the file.")

# Define a message handler for URLs
@app.on_message(filters.regex(r'(https?://\S+)'))
async def url_handler(client, message: Message):
    url = message.matches[0].group(1)
    await download_and_upload(url, message)

# Define a function to download the file using aria2c
async def download_file(url: str) -> str:
    file_path = f"/path/to/save/{datetime.now().strftime('%Y%m%d%H%M%S')}.torrent"
    command = ["aria2c", "-x16", "--seed-time=0", "--summary-interval=1", "--max-tries=3", url, "-o", file_path]
    proc = await asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    _, _ = await proc.communicate()
    return file_path

# Define a function to upload the downloaded file
async def upload_file(file_path: str, chat_id: int):
    await app.send_document(chat_id=chat_id, document=file_path)

# Define a function to download and upload the file
async def download_and_upload(url: str, message: Message):
    try:
        # Download the file
        file_path = await download_file(url)

        # Upload the file
        await upload_file(file_path, message.chat.id)

        # Send a confirmation message
        await message.reply_text("File uploaded successfully!")
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await download_and_upload(url, message)
    except Exception as e:
        await message.reply_text(f"Error: {e}")

# Start the bot
app.run()

