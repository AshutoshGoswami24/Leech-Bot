from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import os
import random
from config import *
# Load API credentials and bot token from the config file
from config import api_id, api_hash, bot_token

# Initialize the Pyrogram client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define the download function
def download_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return None

# Define the start command handler
START_TXT = """<b>𝐇𝐞𝐥𝐥𝐨 {}, ɪ ᴀᴍ {}, ɪ ᴀᴍ ᴀ ᴄʜᴀᴛʙᴏᴛ ᴄʀᴇᴀᴛᴇᴅ ʙʏ ᴘᴀɴᴅᴀᴡᴇʙ. ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴀɴʏ ɢʀᴏᴜᴘ ᴀɴᴅ ᴍᴀᴋᴇ ᴍᴇ ᴀɴ ᴀᴅᴍɪɴ, ᴛʜᴇɴ ᴄʜᴀᴛ ᴡɪᴛʜ ᴍᴇ ᴀs ᴀ ғʀɪᴇɴᴅ. 😊 [𝙈𝙮 𝘾𝙝𝙖𝙣𝙣𝙖𝙡](https://t.me/Pandawep)</b>"""

@app.on_message(filters.command("start") & filters.incoming)
async def start_command(client, message):
    buttons = [
        [
            InlineKeyboardButton('😎 Main Channel 😎', url='https://t.me/pandawep')
        ],
        [
            InlineKeyboardButton('❤️ Chat Family ❤️', url='https://t.me/PandaWepChat')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    me_mention = (await client.get_me()).mention
    await message.reply_photo(
        photo=random.choice(PICS),  # Assuming PICS is defined somewhere in your code
        caption=START_TXT.format(message.from_user.mention, me_mention),
        reply_markup=reply_markup,
        parse_mode="html"
    )

# Define the download command handler
@app.on_message(filters.command("download") & filters.incoming)
async def download_command(client, message):
    try:
        # Get the URL from the command message
        url = message.text.split(maxsplit=1)[1]

        # Download the file
        file_bytes = download_file(url)
        if file_bytes:
            # Save the file
            file_name = url.split("/")[-1]
            file_path = f"./downloads/{file_name}"
            with open(file_path, "wb") as file:
                file.write(file_bytes)

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
