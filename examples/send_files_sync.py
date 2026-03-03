import io
from aiko_api.http_curl import HTTP

# This example demonstrates how to send files using the synchronous HTTP client.
# You can send files by providing a path string or a tuple of (filename, file_pointer).

TOKEN = "YOUR_TOKEN_HERE"
CHANNEL_ID = "YOUR_CHANNEL_ID_HERE"

# Initialize the synchronous HTTP client
http = HTTP(token=TOKEN)

try:
    # 1. Sending a file using a file path
    # Ensure 'example_file.txt' exists or replace with a real path.
    # We'll create a dummy file for this example.
    with open("example_file.txt", "w") as f:
        f.write("This is a test file sent via aiko_api sync HTTP client.")

    print("Sending file via path...")
    msg = http.send_message(
        CHANNEL_ID, 
        "Sent via synchronous HTTP path:", 
        files=["example_file.txt"]
    )
    print(f"Sent message ID: {msg['id']}")

    # 2. Sending a file using a file-like object (io.BytesIO)
    print("Sending file via BytesIO...")
    file_content = b"Synchronous hello from memory!"
    fp = io.BytesIO(file_content)
    
    http.send_message(
        CHANNEL_ID,
        "Sent via synchronous HTTP BytesIO:",
        files=[("sync_memory_file.txt", fp)]
    )

    # 3. Sending multiple files at once
    print("Sending multiple files...")
    http.send_message(
        CHANNEL_ID,
        "Multiple synchronous files:",
        files=[
            "example_file.txt",
            ("sync_memory_2.txt", io.BytesIO(b"Sync memory two!"))
        ]
    )

    print("All files sent successfully!")

except Exception as e:
    print(f"An error occurred: {e}")
