import asyncio
from aiko_api import Client

TOKEN = "YOUR_TOKEN_HERE"
CHANNEL_ID = "YOUR_CHANNEL_ID_HERE"

client = Client()

@client.event
async def on_ready(user):
    print(f"Logged in as {user.username}")
    
    # 1. Send a simple message
    print("Sending message...")
    msg = await client.send_message(CHANNEL_ID, "Hello from aiko_api examples!")
    msg_id = msg['id']
    print(f"Sent message ID: {msg_id}")

    # 2. Reply to that message
    print("Replying to message...")
    await client.messages.reply(CHANNEL_ID, msg_id, "This is a reply!")

    # 3. Edit the original message
    print("Editing message...")
    await client.messages.edit(CHANNEL_ID, msg_id, "I've been edited!")

    # 4. Add a reaction
    print("Adding reaction...")
    await client.messages.add_reaction(CHANNEL_ID, msg_id, "🔥")

    # 5. Delete the message after a short delay
    print("Deleting message in 5 seconds...")
    await asyncio.sleep(5)
    await client.messages.delete(CHANNEL_ID, msg_id)
    print("Deleted!")

    await client.close()

if __name__ == "__main__":
    asyncio.run(client.start(TOKEN))
