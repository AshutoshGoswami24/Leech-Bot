from pyrogram import Client, filters
import requests

# Initialize the Pyrogram client
app = Client("my_bot")

# Function to download file from URL
def download_file(url: str) -> bytes:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception as e:
        print("Error downloading file:", e)
        return None

# Function to upload file
def upload_file(chat_id: int, file_data: bytes, file_name: str):
    try:
        app.send_document(chat_id, document=file_data, file_name=file_name)
    except Exception as e:
        print("Error uploading file:", e)

# Custom filter to check if message is a URL
def is_url(text: str) -> bool:
    return text.startswith("http")

# Handler for /start command
@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Hello! Send me a URL and I'll download the file for you.")

# Handler for messages containing a URL
@app.on_message(filters.text & ~filters.command)
def handle_message(client, message):
    url = message.text.strip()
    if is_url(url):
        file_data = download_file(url)
        if file_data:
            upload_file(message.chat.id, file_data, url.split('/')[-1])
            message.reply_text("File downloaded and uploaded successfully!")
        else:
            message.reply_text("Failed to download file from provided URL.")
    else:
        message.reply_text("Please provide a valid URL.")

# Run the bot
app.run()
