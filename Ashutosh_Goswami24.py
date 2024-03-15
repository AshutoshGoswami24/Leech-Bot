import os
import logging
import subprocess
from datetime import datetime
from pyrogram import Client, filters
from config import *
# Initialize the bot
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define a progress bar function for upload
async def progress_bar_upload(current, total):
    # Your upload progress bar implementation here
    pass

# Define a progress bar function for download
async def progress_bar_download(current, total):
    # Your download progress bar implementation here
    pass

# Define a function to download the file
async def download_file(url):
    try:
        # Generate a unique filename based on the current timestamp
        filename = f"download_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        command = ["aria2c", url, "-o", filename]
        subprocess.run(command)
        return filename
    except Exception as e:
        logging.error(f"Error downloading file: {e}")

# Define a function to upload the file
async def upload_file(file_path, message):
    try:
        await message.reply_text("Uploading file...")
        sent_message = await app.send_document(
            chat_id=message.chat.id,
            document=file_path,
            progress=progress_bar_upload,
        )
        await message.reply_text("File uploaded successfully!")
        return sent_message
    except Exception as e:
        logging.error(f"Error uploading file: {e}")

# Define a message handler for URLs
@app.on_message(filters.regex(r'(https?://\S+)'))
async def url_handler(client, message):
    url = message.matches[0].group(1)
    await download_and_upload(url, message)

# Define a function to download and upload the file
async def download_and_upload(url, message):
    try:
        # Download the file
        file_path = await download_file(url)
        if file_path:
            # Upload the file
            sent_message = await upload_file(file_path, message)
            # Clean up: delete the downloaded file
            os.remove(file_path)
            return sent_message
    except Exception as e:
        logging.error(f"Error: {e}")

# Start the bot
app.run()
