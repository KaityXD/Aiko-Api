import asyncio
import os
from aiko_api import Bot

# This example demonstrates the powerful plugin system in aiko_api.
# 1. It loads all .py files in a directory.
# 2. It automatically registers both standalone @command functions AND Cog classes.
# 3. It starts a hot-reloader that watches for file changes.

async def main():
    TOKEN = "YOUR_TOKEN_HERE"
    bot = Bot(command_prefix="!")
    
    # Define a directory for our plugins
    PLUGIN_DIR = "plugins"
    
    # Ensure the directory exists
    if not os.path.exists(PLUGIN_DIR):
        os.makedirs(PLUGIN_DIR)

    # 1. Initial load of all plugins in the folder
    # This will find any Cog classes and standalone @command functions
    print(f"Loading initial plugins from /{PLUGIN_DIR}...")
    bot.load_plugins(PLUGIN_DIR)
    
    # 2. Start the hot-reloader
    # This runs as a background task and reloads files when you save them!
    print("Starting hot-reloader. Edit any .py file in /plugins to see the magic!")
    asyncio.create_task(bot.watch_plugins(PLUGIN_DIR))

    @bot.event
    async def on_ready(user):
        print(f"Logged in as {user.username}. Plugin system is active!")
        print(f"Currently loaded cogs: {list(bot._cogs.keys())}")
        print(f"Currently loaded commands: {list(bot._commands.keys())}")

    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    asyncio.run(main())
