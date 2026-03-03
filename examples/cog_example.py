import asyncio
from aiko_api import Bot, Cog, command, Context

# Cogs allow you to group commands together in a class.
# This is the recommended way to organize large bots.

class UtilityCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="ping")
    async def ping_command(self, ctx: Context):
        """A simple ping command inside a Cog."""
        await ctx.send("Pong from UtilityCog!")

    @command()
    async def echo(self, ctx: Context, *, message: str):
        """
        Echoes the message back. 
        The '*' in the arguments means 'consume the rest of the message'.
        """
        await ctx.send(f"You said: {message}")

    @command()
    async def add(self, ctx: Context, a: int, b: int):
        """
        Adds two numbers. 
        Type hinting (a: int) automatically converts the arguments!
        """
        await ctx.send(f"{a} + {b} = {a + b}")

async def main():
    TOKEN = "YOUR_TOKEN_HERE"
    bot = Bot(command_prefix="!")

    # Add the cog to the bot
    bot.add_cog(UtilityCog(bot))

    @bot.event
    async def on_ready(user):
        print(f"Bot is ready and Cog is loaded. Logged in as {user.username}")

    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
