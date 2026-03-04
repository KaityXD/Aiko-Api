from aiko_api.http_curl import HTTP

# This class uses curl_cffi for synchronous requests.
# It is useful for simple scripts or when you don't want to use asyncio.

TOKEN = "YOUR_TOKEN_HERE"
CHANNEL_ID = "YOUR_CHANNEL_ID_HERE"

# Initialize the synchronous HTTP client
http = HTTP(token=TOKEN)

try:
    # 1. Login and get user info
    user = http.login()
    print(f"Logged in as: {user['username']}#{user['discriminator']}")

    # 2. Send a message
    print("Sending message...")
    msg = http.send_message(CHANNEL_ID, "Hello from synchronous aiko_api!")
    msg_id = msg['id']
    print(f"Sent message ID: {msg_id}")

    # 3. Get recent messages in the channel
    print("Fetching last 5 messages...")
    messages = http.get_messages(CHANNEL_ID, limit=5)
    for m in messages:
        print(f"[{m['author']['username']}]: {m['content'][:50]}")

    # 4. Add a reaction
    print("Adding reaction...")
    http.add_reaction(CHANNEL_ID, msg_id, "🚀")

    # 5. Edit the message
    print("Editing message...")
    http.edit_message(CHANNEL_ID, msg_id, "I am now a synchronous edit!")

    # 6. Delete the message
    print("Deleting message...")
    http.delete_message(CHANNEL_ID, msg_id)
    print("Done!")

except Exception as e:
    print(f"An error occurred: {e}")
