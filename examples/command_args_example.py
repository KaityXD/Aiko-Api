import asyncio
from aiko_api import Bot, command, Context

# This example demonstrates the powerful automatic argument parsing in aiko_api.
# The library uses your function's type hints to convert user input automatically.

@command()
async def roll(ctx, sides: int = 6):
    """
    Rolls a die. 
    'sides' is automatically converted to an integer.
    It also has a default value of 6 if the user doesn't provide one!
    Usage: !roll 20
    """
    import random
    result = random.randint(1, sides)
    await ctx.send(f"🎲 You rolled a {result} (1-{sides})")

@command()
async def toggle(ctx, feature: str, enabled: bool):
    """
    Demonstrates boolean conversion.
    'enabled' accepts: yes/no, y/n, true/false, t/f, 1/0, on/off.
    Usage: !toggle notifications off
    """
    status = "ENABLED" if enabled else "DISABLED"
    await ctx.send(f"Feature `{feature}` is now {status}!")

@command()
async def announce(ctx, channel_id: int, *, message: str):
    """
    The '*' means 'consume the rest of the message'.
    Without it, 'message' would only be the first word after the ID.
    Usage: !announce 123456789 Hello everyone, this is a long announcement!
    """
    await ctx.send(f"Announcing to <#{channel_id}>: {message}")

async def main():
    TOKEN = "YOUR_TOKEN_HERE"
    bot = Bot(command_prefix="!")
    
    # Register the commands
    bot.command()(roll)
    bot.command()(toggle)
    bot.command()(announce)

    @bot.event
    async def on_ready(user):
        print(f"Logged in as {user.username}. Argument parsing examples ready!")
        print("Try these commands:")
        print("1. !roll 20")
        print("2. !toggle gravity off")
        print("3. !announce 123 This is a long message that won't be cut off.")

    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    asyncio.run(main())
