from pyrogram import Client, filters
import subprocess
from datetime import datetime
import os
from config import *

# Initialize the bot
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define a command handler
@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Send me a URL and I will download and send you the file.")

# Define a message handler for URLs
@app.on_message(filters.regex(r'(https?://\S+)'))
async def url_handler(client, message):
    url = message.matches[0].group(1)
    await aria2_download(url, message)

# Define the function to download the file using aria2c
async def aria2_download(url, message):
    task_start = datetime.now()
    status_head = f"<b>📥 DOWNLOADING FROM » </b><i>🔗 Link</i>\n\n<b>🏷️ Name » </b><code>Downloading File</code>\n"

    # Specify the directory where you want to save the downloaded file
    download_dir = "./downloads"

    # Create the directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)

    # Create a command to run aria2c with the link
    command = [
        "aria2c",
        "-x16",
        "--seed-time=0",
        "--summary-interval=1",
        "--max-tries=3",
        "--console-log-level=notice",
        "-d",
        download_dir,
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
            await message.reply_text(status_head + output.decode("utf-8").strip())

    # Wait for the process to finish
    proc.wait()

    # Check if download was successful
    if proc.returncode == 0:
        await upload_file(download_dir, message)
    else:
        await message.reply_text("Download failed.")

# Define a function to upload the downloaded file
async def upload_file(download_dir, message):
    try:
        file_name = os.listdir(download_dir)[0]  # Get the downloaded file name
        file_path = os.path.join(download_dir, file_name)

        # Upload the file with progress
        async with app.send_document(
            chat_id=message.chat.id,
            document=file_path,
            progress=progress_callback,
            progress_args=(message,)
        ) as sent:
            await sent.reply_text("File uploaded successfully!")
    except Exception as e:
        await message.reply_text(f"Error uploading file: {str(e)}")

# Define a progress callback function
async def progress_callback(current, total, message):
    # Calculate progress percentage
    progress = current / total * 100
    await message.edit_text(f"Uploading... {progress:.2f}%")

print("𝐁𝐨𝐭 𝐒𝐭𝐚𝐫𝐭𝐞𝐝😁......")

# Start the bot
app.run()
