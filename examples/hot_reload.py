import asyncio
from aiko_api import Bot

TOKEN = "YOUR_TOKEN_HERE"
PREFIX = "!"

async def main():
    bot = Bot(command_prefix=PREFIX)
    
    # Just point it at the directory and you're done.
    # It will recursively load all .py files as plugins.
    bot.load_plugins("plugins")
    
    # Start the hot-reloader in the background.
    # Now you can edit files in /plugins and they'll live-reload!
    # No need to restart the bot to see changes.
    print("Starting hot-reloader for /plugins...")
    asyncio.create_task(bot.watch_plugins("plugins"))

    @bot.event
    async def on_ready(user):
        print(f"Logged in as {user.username} (ID: {user.id})")
        print("Hot-reloader is active. Edit /plugins/utility.py to see the magic.")

    await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
