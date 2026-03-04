import asyncio
from aiko_api import Bot

TOKEN = "YOUR_TOKEN_HERE"
PREFIX = "!"


async def main():
    # Initialize the bot with a command prefix
    bot = Bot(command_prefix=PREFIX)

    # Load plugins from the plugins folder
    # This assumes a 'plugins' folder exists (like in the project root)
    try:
        bot.load_plugins("plugins")
    except FileNotFoundError:
        print("Plugins folder not found. Create one to use plugins.")

    @bot.event
    async def on_ready(user):
        print(f"Bot logged in as {user.username} (ID: {user.id})")
        print(f"Prefix: {PREFIX}")

    # Example of a command registered directly on the bot
    @bot.command()
    async def hello(ctx):
        await ctx.send(f"Hello, {ctx.author.username}!")

    if TOKEN == "YOUR_TOKEN_HERE":
        print("Please replace 'YOUR_TOKEN_HERE' with your actual Discord token!")
        return

    # Connect to Discord
    await bot.start(TOKEN)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
