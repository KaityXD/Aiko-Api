import asyncio
from aiko_api import Client, Forbidden, NotFound, HTTPException

# This example demonstrates how to handle common Discord API errors.

TOKEN = "YOUR_TOKEN_HERE"
INVALID_CHANNEL_ID = "123456789"  # A non-existent channel

client = Client()


@client.event
async def on_ready(user):
    print(f"Logged in as {user.username}")

    try:
        # 1. Handling Forbidden (e.g. not in the guild or lacks permission)
        print("Attempting to send message to a forbidden channel...")
        await client.send_message(INVALID_CHANNEL_ID, "This will fail.")

    except Forbidden:
        print("Caught Forbidden error: I don't have access to this channel!")

    except NotFound:
        print("Caught NotFound error: This channel doesn't exist!")

    except HTTPException as e:
        print(f"Caught a generic HTTP error: {e}")

    # 2. Handling a message delete that fails
    try:
        print("Attempting to delete a non-existent message...")
        await client.messages.delete(INVALID_CHANNEL_ID, "000000000")
    except (NotFound, HTTPException) as e:
        print(f"Failed to delete message: {e}")

    print("Done! Closing...")
    await client.close()


if __name__ == "__main__":
    if TOKEN == "YOUR_TOKEN_HERE":
        print("Please replace 'YOUR_TOKEN_HERE' with your actual Discord token!")
    else:
        asyncio.run(client.start(TOKEN))
