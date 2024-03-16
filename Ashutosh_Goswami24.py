from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import os

# Load API credentials and bot token from the config file
from config import api_id, api_hash, bot_token

# Initialize the Pyrogram client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define the command handler
@app.on_message(filters.private & filters.command("download"))
async def download_command_handler(client, message):
    try:
        # Get the URL from the command message
        url = message.text.split(maxsplit=1)[1]

        # Download the file
        response = requests.get(url)
        if response.status_code == 200:
            file_name = url.split("/")[-1]
            file_path = f"./downloads/{file_name}"
            with open(file_path, "wb") as file:
                file.write(response.content)

            # Upload the file
            await message.reply_document(document=file_path)

            # Delete the downloaded file
            os.remove(file_path)
        else:
            await message.reply_text("Failed to download the file.")
    except IndexError:
        await message.reply_text("Please provide a URL after the /download command.")

# Start the bot
app.run()
