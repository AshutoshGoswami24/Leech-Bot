from pyrogram import Client, filters
from pyrogram.types import Message
import requests
from config import api_id, api_hash, bot_token

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Function to download file from URL
def download_file(url: str) -> bytes:
    try:
        message = app.send_message("me", "Downloading file... 📥")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            bytes_downloaded = 0
            file_data = b""
            for chunk in response.iter_content(chunk_size=1024):
                bytes_downloaded += len(chunk)
                message.edit_text(f"Downloading file... 📥\nProgress: {bytes_downloaded}/{total_size} bytes")
                file_data += chunk
            message.edit_text("Download complete! ✅")
            return file_data
        else:
            message.edit_text("Failed to download file. ❌")
            return None
    except Exception as e:
        print("Error downloading file:", e)
        message.edit_text("Failed to download file. ❌")
        return None

# Function to upload file
def upload_file(chat_id: int, file_data: bytes, file_name: str) -> Message:
    try:
        message = app.send_message(chat_id, "Uploading file... 📤")
        uploaded_message = app.send_document(chat_id, document=file_data, filename=file_name)
        if uploaded_message:
            message.edit_text(f"File uploaded successfully as {uploaded_message.document.file_name}! ✅")
            return uploaded_message
        else:
            message.edit_text("Failed to upload file. ❌")
            return None
    except Exception as e:
        print("Error uploading file:", e)
        message.edit_text("Failed to upload file. ❌")
        return None

# Custom filter to check if message is a URL
def is_url(msg: Message) -> bool:
    return msg.text is not None and msg.text.startswith("http")

# Handler for /start command
@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Hello! Send me a URL and I'll download the file for you.")

# Handler for messages containing a URL
@app.on_message(filters.text & ~filters.command & filters.create(is_url))

def handle_message(client, message):
    url = message.text.strip()
    file_data = download_file(url)
    if file_data:
        uploaded_message = upload_file(message.chat.id, file_data, url.split('/')[-1])
        if not uploaded_message:
            message.reply_text("Failed to upload file.")
    else:
        message.reply_text("Failed to download file from provided URL.")

# Run the bot
app.run()
