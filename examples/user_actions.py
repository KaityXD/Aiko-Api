import asyncio
from aiko_api import Client, Activity

TOKEN = "YOUR_TOKEN_HERE"

client = Client()


@client.event
async def on_ready(user):
    print(f"Logged in as {user.username}")

    # 1. Change Presence
    print("Changing presence...")
    activity = Activity(
        name="Playing around with aiko_api",
        type=0,  # Game
        details="Developing examples",
        state="Working hard",
    )
    await client.user_actions.change_presence(activity=activity, status="dnd")
    print("Presence changed to DND - Playing around with aiko_api")

    # 2. Get Relationships (Friends, Blocks)
    print("Fetching relationships...")
    relationships = await client.user_actions.get_relationships()
    print(f"You have {len(relationships)} relationships.")

    # 3. Create a DM (Send message to yourself as an example)
    print("Creating DM with yourself...")
    dm = await client.user_actions.create_dm(user.id)
    print(f"DM Channel ID: {dm['id']}")
    await client.send_message(dm["id"], "Self-test DM from aiko_api examples")

    print("Example finished. Closing in 10 seconds...")
    await asyncio.sleep(10)
    await client.close()


if __name__ == "__main__":
    if TOKEN == "YOUR_TOKEN_HERE":
        print("Please replace 'YOUR_TOKEN_HERE' with your actual Discord token!")
    else:
        asyncio.run(client.start(TOKEN))
