import asyncio
from aiko_api import Client

# Replace with your actual token
TOKEN = "YOUR_TOKEN_HERE"

client = Client()


@client.event
async def on_ready(user):
    print(f"Logged in as {user.username} (ID: {user.id})")
    print(f"I am in {len(client.cache.guilds)} guilds.")


@client.event
async def on_message_create(message):
    print(
        f"Message from {message.author.username} in {message.channel_id}: {message.content}"
    )

    # Ignore messages from ourselves
    if client.user and message.author.id == client.user.id:
        return

    if message.content.startswith("!ping"):
        await client.send_message(message.channel_id, "Pong!")


async def main():
    if TOKEN == "YOUR_TOKEN_HERE":
        print("Please replace 'YOUR_TOKEN_HERE' with your actual Discord token!")
        return

    try:
        await client.start(TOKEN)
    except KeyboardInterrupt:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
