import asyncio
import io
from aiko_api import Client

# This example demonstrates how to send files using the asynchronous Client.
# You can send files by providing a path string or a tuple of (filename, file_pointer).

TOKEN = "YOUR_TOKEN_HERE"
CHANNEL_ID = "YOUR_CHANNEL_ID_HERE"

client = Client()

@client.event
async def on_ready(user):
    print(f"Logged in as {user.username}")
    
    # 1. Sending a file using a file path
    # Ensure 'example_file.txt' exists or replace with a real path.
    # We'll create a dummy file for this example.
    with open("example_file.txt", "w") as f:
        f.write("This is a test file sent via aiko_api async client.")

    print("Sending file via path...")
    await client.send_message(
        CHANNEL_ID, 
        "Here is a file sent via path:", 
        files=["example_file.txt"]
    )

    # 2. Sending a file using a file-like object (io.BytesIO)
    print("Sending file via BytesIO...")
    file_content = b"Hello! This file was created in memory."
    fp = io.BytesIO(file_content)
    
    await client.send_message(
        CHANNEL_ID,
        "Here is a file sent via BytesIO:",
        files=[("memory_file.txt", fp)]
    )

    # 3. Sending multiple files at once
    print("Sending multiple files...")
    await client.send_message(
        CHANNEL_ID,
        "Here are multiple files:",
        files=[
            "example_file.txt",
            ("another_memory_file.txt", io.BytesIO(b"Another one!"))
        ]
    )

    print("Done! Closing...")
    await client.close()

if __name__ == "__main__":
    asyncio.run(client.start(TOKEN))
