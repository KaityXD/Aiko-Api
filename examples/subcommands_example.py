import asyncio
from aiko_api import Bot, Cog, command, Context

# This example demonstrates the clean, flat hierarchy for creating nested sub-commands.
# The parent command acts as a decorator for its child commands.

class Moderation(Cog):
    # Root Command: !config
    @command()
    async def config(self, ctx: Context):
        await ctx.send("Main config menu. Try `!config prefix`")

    # Sub-command: !config prefix
    # Notice we use `@config` (the parent function's name) as the decorator
    @config
    async def prefix(self, ctx: Context, new_prefix: str):
        await ctx.send(f"Prefix updated to `{new_prefix}`")

    # Deep Nesting: !config prefix reset
    # We use `@prefix` to nest this under the `prefix` sub-command
    @prefix
    async def reset(self, ctx: Context):
        await ctx.send("Prefix reset to default `!`")


async def main():
    TOKEN = "YOUR_TOKEN_HERE"
    bot = Bot(command_prefix="!")
    
    # Add the cog to the bot
    bot.add_cog(Moderation(bot))

    @bot.event
    async def on_ready(user):
        print(f"Logged in as {user.username}.")
        print("Try sending these commands in Discord:")
        print("1. !config")
        print("2. !config prefix ?")
        print("3. !config prefix reset")

    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    asyncio.run(main())
