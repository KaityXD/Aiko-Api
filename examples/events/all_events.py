import asyncio
from aiko_api import Client

# This example shows how to listen to various events supported by aiko_api.

TOKEN = "YOUR_TOKEN_HERE"
client = Client()

@client.event
async def on_ready(user):
    """Called when the client is logged in and ready."""
    print(f"Logged in as {user.username} (ID: {user.id})")
    print("Gateway is connected and initial data is cached.")

@client.event
async def on_message_create(message):
    """Called when a message is created in a channel the client can see."""
    print(f"New message from {message.author.username}: {message.content}")

@client.event
async def on_guild_create(guild):
    """
    Called when the client joins a guild or during initial startup 
    for each guild the client is in.
    """
    print(f"Joined/Cached Guild: {guild.name} (ID: {guild.id})")
    print(f"Member count: {len(guild.members)}")

@client.event
async def on_resumed():
    """Called when the client successfully resumes a lost session."""
    print("Session resumed successfully!")

@client.event
async def on_message_update(data):
    """
    Called when a message is edited. 
    Note: Currently, aiko_api passes raw data for events not explicitly mapped to models.
    """
    print(f"Message updated: {data.get('id')}")

@client.event
async def on_message_delete(data):
    """Called when a message is deleted."""
    print(f"Message deleted: {data.get('id')} in channel {data.get('channel_id')}")

async def main():
    try:
        await client.start(TOKEN)
    except KeyboardInterrupt:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
