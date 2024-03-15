import os
import subprocess
from datetime import datetime
from pyrogram import Client, filters
from config import *
# Initialize the bot
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Function to delete the DHT cache file
def delete_dht_cache():
    dht_cache_file = "/root/.cache/aria2/dht.dat"
    if os.path.exists(dht_cache_file):
        os.remove(dht_cache_file)

# Function to show download progress
async def show_download_progress(current, total, message):
    percentage = (current / total) * 100
    await message.reply_text(f"Download Progress: {percentage:.2f}%")

# Function to show upload progress
async def show_upload_progress(current, total, message):
    percentage = (current / total) * 100
    await message.reply_text(f"Upload Progress: {percentage:.2f}%")

# Function to download and upload the file
async def download_and_upload(url, message):
    task_start = datetime.now()

    # Delete the DHT cache file
    delete_dht_cache()

    # Create a command to run aria2c with the link
    command = [
        "aria2c",
        "-x16",
        "--seed-time=0",
        "--summary-interval=1",
        "--max-tries=3",
        "--console-log-level=notice",
        "-d",
        "/path/to/save",  # Specify the path where you want to save the downloaded file
        url,
    ]

    # Run the command using subprocess.Popen
    proc = subprocess.Popen(
        command, bufsize=0, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    # Read and print output in real-time
    while True:
        output = proc.stdout.readline()  # type: ignore
        if output == b"" and proc.poll() is not None:
            break
        if output:
            await show_download_progress(proc.stdout.tell(), total_file_size, message)

    # Wait for the process to finish
    proc.wait()

    # Check if download was successful
    if proc.returncode == 0:
        await upload_file("/path/to/save", message)
    else:
        await message.reply_text("Download failed.")

# Function to upload the downloaded file
async def upload_file(file_path, message):
    await message.reply_text("Uploading file...")
    # Add your code to upload the file here
    # Make sure to handle the upload process appropriately

# Command handler for the start command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Send me a URL and I will download and send you the file.")

# Message handler for URLs
@app.on_message(filters.regex(r'(https?://\S+)'))
async def url_handler(client, message):
    url = message.matches[0].group(1)
    await download_and_upload(url, message)

# Start the bot
app.run()
