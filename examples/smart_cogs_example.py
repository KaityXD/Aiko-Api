import asyncio
from aiko_api import Bot, Cog, command, cog

# This example demonstrates "Smart Signatures" and clean Cog Event handling.
# 1. You don't have to define `self` if you don't need it.
# 2. You can use `@cog.event` or automatic naming (`on_...`) for Cog events.


class SmartCog(Cog):
    # --- SMART SIGNATURES ---

    @command()
    async def ping(ctx):
        # Look ma, no 'self'!
        # The library detects this and skips passing the Cog instance.
        await ctx.send("Pong! (I didn't need `self`!)")

    @command()
    async def stats(self, ctx):
        # Here we requested 'self', so the library provides it.
        await ctx.send(f"I am a Cog attached to bot user: {self.bot.user.username}")

    # --- CLEAN COG EVENTS ---

    @cog.event
    async def on_message_create(message):
        # We can also drop 'self' here!
        if message.content == "hello":
            await message.reply("Hi there! (Caught via explicit `@cog.event`)")

    # Alternative (Automatic Detection)
    async def on_ready(self, user):
        # Any method starting with `on_` inside a Cog is automatically registered
        # as an event listener, even without the `@cog.event` decorator!
        print(
            f"[SmartCog] Automatically detected ready event. Logged in as {user.username}"
        )


async def main():
    TOKEN = "YOUR_TOKEN_HERE"

    if TOKEN == "YOUR_TOKEN_HERE":
        print("Please replace 'YOUR_TOKEN_HERE' with your actual Discord token!")
        return

    bot = Bot(command_prefix="!")
    bot.add_cog(SmartCog(bot))

    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())
