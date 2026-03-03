import asyncio
import datetime
from aiko_api import Bot, Activity, ActivityType

# This example demonstrates SELFBOT Rich Presence (RPC) spoofing.
# Rich Presence assets (images, buttons, timestamps) are a user-only feature.
# Official bots can only set basic activities.

TOKEN = "YOUR_USER_TOKEN_HERE"
PREFIX = "!"

async def main():
    bot = Bot(command_prefix=PREFIX)

    @bot.event
    async def on_ready(user):
        print(f"Selfbot Logged in as: {user.username} ({user.id})")
        
        # --- SELFBOT RICH PRESENCE (RPC) SPOOFING ---
        # We can pretend to be playing a game like VALORANT.
        
        # Set a start time (e.g., March 1st, 2026)
        start_time = datetime.datetime(2026, 3, 1, tzinfo=datetime.timezone.utc)
        start_timestamp = int(start_time.timestamp() * 1000)

        activity = Activity(
            name="VALORANT", # The "game" name
            type=ActivityType.playing,
            details="Ranked Match", # Shown on profile
            state="In-game (5-2)", # Shown on profile
            application_id="700136079562375258", # VALORANT's real App ID
            timestamps={"start": start_timestamp},
            assets={
                # You can use direct URLs for assets on selfbots!
                "large_image": "https://cdn.discordapp.com/attachments/1466402750286921822/1478115538705317989/Arcane_Logo_Drawing.jpg?ex=69a739de&is=69a5e85e&hm=28709d66ca6ee4eac435c4c12865808322328bb6b7c15891ca0f03faed0f1304&",
                "large_text": "VALORANT",
                "small_image": "https://cdn.discordapp.com/emojis/1041440237584384000.png",
                "small_text": "Radiant"
            },
        )

        # Update presence to DND with our custom activity
        # This will show up as a "Rich" activity on your profile.
        await bot.change_presence(activity=activity, status="dnd")
        print(f"RPC Spoofing set to 'Playing VALORANT' for {user.username}!")

    @bot.command()
    async def ping(ctx):
        await ctx.reply("Pong! 🏓 (I am a selfbot with RPC)")

    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    asyncio.run(main())
