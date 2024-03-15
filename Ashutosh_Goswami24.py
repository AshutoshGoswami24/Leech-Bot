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
        file_path = await download_file(url, file_name)
        await app.send_document(message.chat.id, document=file_path)
        os.remove(file_path)  # Delete the file after sending
    except Exception as e:
        await message.reply_text(f"Error: {e}")

# Function to download the file from the direct link
async def download_file(url: str, file_name: str) -> str:
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raise an exception for HTTP errors
    os.makedirs("./downloads", exist_ok=True)  # Create a downloads directory if it doesn't exist
    file_path = f"./downloads/{file_name}"  # Save the file in the downloads directory
    with open(file_path, "wb") as file:
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
            downloaded += len(chunk)
            await update_progress_bar(downloaded, total_size)
    return file_path

# Function to update the progress bar
async def update_progress_bar(downloaded, total_size):
    progress = min(int(downloaded / total_size * 100), 100)
    await app.edit_message_text(
        chat_id=await app.get_me().id,
        text=f"Downloading... {progress}%"
    )

# Start the bot
app.run()
