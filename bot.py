import asyncio
import os
import pyrogram
from pyrogram import Client, filters
import httpx
from moviepy.editor import VideoFileClip
from natsort import natsorted
import cv2
from PIL import Image
import psutil
import pytz
import requests
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.types import CallbackQuery
import uvloop
import GPUtil
from config import *


# Initialize asyncio loop with uvloop for better performance
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()

# Initialize Pyrogram client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


async def download_file(url):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        filename = url.split("/")[-1]
        with open(filename, 'wb') as f:
            f.write(r.content)
    return filename


async def rename_file(old_name, new_name):
    os.rename(old_name, new_name)
    return new_name


async def upload_file(file_path, real_name, message):
    caption = f"<{BOT.Options.caption}>{BOT.Setting.prefix} {real_name} {BOT.Setting.suffix}</{BOT.Options.caption}>"
    type_ = fileType(file_path)

    f_type = type_ if BOT.Options.stream_upload else "document"

    # Upload the file
    try:
        if f_type == "video":
            # For Renaming to mp4
            if not BOT.Options.stream_upload:
                file_path = videoExtFix(file_path)
            # Generate Thumbnail and Get Duration
            thmb_path, seconds = thumbMaintainer(file_path)
            with Image.open(thmb_path) as img:
                width, height = img.size

            sent_msg = await message.reply_video(
                video=file_path,
                supports_streaming=True,
                width=width,
                height=height,
                caption=caption,
                thumb=thmb_path,
                duration=int(seconds),
                progress=progress_bar,
                reply_to_message_id=message.id,
            )

        elif f_type == "audio":
            thmb_path = None if not ospath.exists(Paths.THMB_PATH) else Paths.THMB_PATH
            sent_msg = await message.reply_audio(
                audio=file_path,
                caption=caption,
                thumb=thmb_path,
                progress=progress_bar,
                reply_to_message_id=message.id,
            )

        elif f_type == "document":
            if ospath.exists(Paths.THMB_PATH):
                thmb_path = Paths.THMB_PATH
            elif type_ == "video":
                thmb_path, _ = thumbMaintainer(file_path)
            else:
                thmb_path = None

            sent_msg = await message.reply_document(
                document=file_path,
                caption=caption,
                thumb=thmb_path,
                progress=progress_bar,
                reply_to_message_id=message.id,
            )

        elif f_type == "photo":
            sent_msg = await message.reply_photo(
                photo=file_path,
                caption=caption,
                progress=progress_bar,
                reply_to_message_id=message.id,
            )

        return sent_msg

    except Exception as e:
        print("Error uploading file:", e)


@app.on_message(filters.command("run"))
async def run_command(client, message):
    chat_id = message.chat.id
    msg = await message.reply_text("Please send the URL of the file you want to download.")
    await app.send_chat_action(chat_id, "typing")

    @app.on_message(filters.text)
    async def process_url(client, message):
        url = message.text
        await message.delete()
        await msg.delete()
        await app.send_chat_action(chat_id, "typing")
        filename = await download_file(url)
        await app.send_message(chat_id, f"Downloaded file: {filename}")

        # Show inline keyboard with options to change name or upload
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Change Name", callback_data="change_name")],
                [InlineKeyboardButton("Upload", callback_data="upload")]
            ]
        )
        await app.send_message(chat_id, "Choose an action:", reply_markup=keyboard)

    @app.on_callback_query()
    async def button(client, callback: CallbackQuery):
        message = callback.message
        chat_id = message.chat.id
        data = callback.data
        await message.delete()
        if data == "change_name":
            await app.send_message(chat_id, "Please enter the new file name.")
            await app.send_chat_action(chat_id, "typing")

            @app.on_message(filters.text)
            async def process_new_name(client, message):
                new_name = message.text
                await message.delete()
                await app.send_chat_action(chat_id, "typing")
                new_filename = await rename_file(filename, new_name)
                await app.send_message(chat_id, f"File renamed to: {new_filename}")
                sent_msg = await upload_file(new_filename, new_name, message)
                # Cleanup
                os.remove(new_filename)
                await app.stop()
                
        elif data == "upload":
            await app.send_chat_action(chat_id, "typing")
            sent_msg = await upload_file(filename, filename, message)
            # Cleanup
            os.remove(filename)
            await app.stop()

# Start the bot
app.run()
