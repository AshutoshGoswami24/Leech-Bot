import os
import requests
from pyrogram import Client, filters
from config import *

# Initialize the bot
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define a command handler
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Send me a direct download link and I will send you the file.")

# Define a message handler for direct download links
@app.on_message(filters.regex(r'(https?://\S+)'))
async def direct_download_handler(client, message):
    url = message.matches[0].group(1)
    file_name = url.split("/")[-1]
    try:
        file_path = download_file(url, file_name)
        sent_message = await app.send_document(message.chat.id, document=file_path)
        await sent_message.delete()  # Delete the message after sending
        os.remove(file_path)  # Delete the file after sending
    except Exception as e:
        await message.reply_text(f"Error: {e}")

# Function to download the file from the direct link
def download_file(url: str, file_name: str) -> str:
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    file_path = f"/path/to/save/{file_name}"  # Change this to the desired save path
    with open(file_path, "wb") as file:
        file.write(response.content)
    return file_path

# Start the bot
app.run()
