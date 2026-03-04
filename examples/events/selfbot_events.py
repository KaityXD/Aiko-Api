import asyncio
from aiko_api import Client

# This example demonstrates events that are particularly useful for selfbots,
# such as relationships (friends), presence updates, and typing notifications.

TOKEN = "YOUR_TOKEN_HERE"
client = Client()

@client.event
async def on_ready(user):
    print(f"Selfbot ready: {user.username}")

@client.event
async def on_relationship_add(data):
    """
    Called when a friend request is received, accepted, or someone is blocked.
    'type' 1 = Friend, 2 = Blocked, 3 = Incoming Friend Request, 4 = Outgoing Friend Request
    """
    user = data.get('user', {})
    rel_type = data.get('type')
    print(f"Relationship update with {user.get('username')} (Type: {rel_type})")

@client.event
async def on_relationship_remove(data):
    """Called when a friend is removed or a user is unblocked."""
    print(f"Relationship removed for user ID: {data.get('id')}")

@client.event
async def on_presence_update(data):
    """Called when a friend or guild member changes their status or activity."""
    user = data.get('user', {})
    status = data.get('status')
    activities = data.get('activities', [])
    
    # We only care about friends for this example (id is present in 'user')
    if 'username' in user:
        print(f"Presence: {user['username']} is now {status}")
        if activities:
            print(f"  Activity: {activities[0].get('name')}")

@client.event
async def on_typing_start(data):
    """Called when someone starts typing in a channel."""
    channel_id = data.get('channel_id')
    user_id = data.get('user_id')
    print(f"User {user_id} is typing in channel {channel_id}...")

@client.event
async def on_user_update(data):
    """Called when the current user's profile is updated."""
    print(f"Profile updated: {data.get('username')}#{data.get('discriminator')}")

async def main():
    try:
        await client.start(TOKEN)
    except KeyboardInterrupt:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
