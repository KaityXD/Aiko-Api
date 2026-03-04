import asyncio
import os
from aiko_api import Bot, get_logger

# Configure logging
log = get_logger("MultiTokenExample", level="INFO")

def setup_bot(prefix="!"):
    """Creates and configures a bot instance."""
    bot = Bot(command_prefix=prefix)

    @bot.event
    async def on_ready(user):
        log.info(f"Instance logged in as: {user.username} ({user.id})")

    @bot.command()
    async def hello(ctx):
        await ctx.send(f"Hello from {ctx.bot.user.username}!")

    return bot

async def main():
    # A list of your tokens (can be mix of user and official bot tokens)
    TOKENS = [
        "TOKEN_1_HERE",
        "Bot TOKEN_2_HERE",
        # ...
    ]

    tasks = []
    for token in TOKENS:
        # Create a fresh bot instance for each token
        bot = setup_bot()
        # Add the start coroutine to our tasks list
        tasks.append(bot.start(token))

    if not TOKENS or TOKENS[0] == "TOKEN_1_HERE":
        log.error("Please add your tokens to the TOKENS list in the example.")
        return

    log.info(f"Launching {len(TOKENS)} instances...")
    # Run all instances concurrently
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Shutting down all instances...")
