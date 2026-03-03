import asyncio
from aiko_api import Client

# This example demonstrates how to manage guilds, 
# specifically how to leave a guild.

TOKEN = "YOUR_TOKEN_HERE"
GUILD_ID = "YOUR_GUILD_ID_HERE"

client = Client()

@client.event
async def on_ready(user):
    print(f"Logged in as {user.username}")
    
    # 1. Leave a guild
    print(f"Attempting to leave guild with ID: {GUILD_ID}")
    try:
        await client.guilds.leave(GUILD_ID)
        print("Successfully left the guild!")
    except Exception as e:
        print(f"Failed to leave guild: {e}")

    # 2. Synchronous way (using HTTP client directly)
    # from aiko_api.http_curl import HTTP
    # http = HTTP(token=TOKEN)
    # http.leave_guild(GUILD_ID)

    await client.close()

if __name__ == "__main__":
    asyncio.run(client.start(TOKEN))
