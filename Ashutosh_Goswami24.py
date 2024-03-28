from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import os
from config import API_ID, API_HASH, BOT_TOKEN
from tqdm import tqdm

# Initialize the Pyrogram Client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to handle /start command
@app.on_message(filters.private & filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Welcome! Please enter the video URL:")

# Function to handle messages containing URLs
@app.on_message(filters.private)
async def handle_message(client, message):
    if message.text.startswith("http"):
        url = message.text
        try:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            file_name = url.split('/')[-1]
            file_path = f'./{file_name}'
            with open(file_path, 'wb') as file, tqdm(
                desc=file_name,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                ascii=True
            ) as progress_bar:
                for data in response.iter_content(chunk_size=1024):
                    file.write(data)
                    progress_bar.update(len(data))
            # Ask user for file name
            await message.reply_text("Downloaded! Please enter the desired file name:")
            await app.ask(message.chat.id, "new_file_name")
        except Exception as e:
            await message.reply_text(f'An error occurred: {e}')

# Function to handle the new file name
@app.on_message(filters.private & filters.regex(r'^[\w\-. ]+$'))
async def handle_new_file_name(client, message):
    new_file_name = message.text
    file_path = f'./{message.reply_to_message.document.file_name}'
    try:
        with open(file_path, 'rb') as file:
            # Upload the file with the new name
            await message.reply_document(document=file, file_name=new_file_name)
    except Exception as e:
        await message.reply_text(f'An error occurred while uploading the file: {e}')
    finally:
        # Clean up: delete the downloaded file
        os.remove(file_path)

# Run the bot
app.run()
