from pyrogram import Client, filters
import subprocess
from datetime import datetime
from config import *

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
            await on_output(output.decode("utf-8"), message, status_head, task_start)

# Define a function to handle output from aria2c
async def on_output(output: str, message, status_head, task_start):
    # Process output from aria2c as needed
    # You can send status updates back to the user here
    pass

# Start the bot
app.run()
