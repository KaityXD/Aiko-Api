import asyncio
from aiko_api import Client

# This script listens to every event dispatched from the Gateway.
# It is extremely useful for discovering new events or debugging
# the exact payload data Discord sends.

TOKEN = "YOUR_TOKEN_HERE"
client = Client()

# The internal dispatching system uses the 'dispatch' method.
# We can override it slightly to log every event name before 
# it gets dispatched to our handlers.

original_dispatch = client.dispatch

async def logging_dispatch(event, data):
    """Logs every event name from the Gateway."""
    print(f"[EVENT] {event}")
    # Call the original dispatch to handle existing listeners
    await original_dispatch(event, data)

# Hook the logger into the client
client.dispatch = logging_dispatch

@client.event
async def on_ready(user):
    print(f"Ready! Logged in as {user.username}")
    print("Now watching for ALL gateway events...")

async def main():
    try:
        await client.start(TOKEN)
    except KeyboardInterrupt:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
