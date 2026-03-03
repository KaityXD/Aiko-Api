import asyncio
from aiko_api import Client

TOKEN = "YOUR_TOKEN_HERE"
CHANNEL_ID = "YOUR_CHANNEL_ID_HERE"

client = Client()

@client.event
async def on_ready(user):
    print(f"Logged in as {user.username}")
    print(f"I will now wait for someone to say '!start' in channel {CHANNEL_ID}")

    # This will pause execution until someone says "!start"
    # in the specified channel.
    def check(message):
        return (
            message.channel_id == str(CHANNEL_ID) and 
            message.content == "!start" and
            message.author.id != client.user.id
        )

    try:
        print("Waiting for !start...")
        message = await client.wait_for("message_create", check=check, timeout=60.0)
        print(f"Bot started by {message.author.username}!")
        await client.send_message(CHANNEL_ID, "Ready to go!")
    except asyncio.TimeoutError:
        print("Timed out waiting for !start.")
        await client.send_message(CHANNEL_ID, "No one started me in 60 seconds :(")
    
    # Wait for another message and reply to it
    print("Waiting for any message to reply to...")
    msg = await client.wait_for("message_create", timeout=30)
    await msg.reply("I caught your message!")

    print("Closing...")
    await client.close()

if __name__ == "__main__":
    asyncio.run(client.start(TOKEN))
