# aiko_api

A clean, efficient, and modern Discord API wrapper for Python.

`aiko_api` is designed to be a lightweight and easy-to-use alternative for building Discord bots and selfbots. It features a flat command hierarchy, smart signatures, and a powerful plugin system with hot-reloading.

## Features

- **Flat Sub-command Hierarchy:** Decorate commands with their parent commands for clean nesting.
- **Smart Signatures:** `self` is optional in Cogs; the library detects if it's needed.
- **Clean Cog Events:** Automatically register `on_` methods as event listeners.
- **Advanced Plugin System:** Load Cogs and standalone commands from directories with built-in hot-reloading.
- **Optimized HTTP:** Built on top of `curl_cffi` for high performance and better impersonation.

## Installation

```bash
pip install aiko-api
```

## Quick Start

```python
import asyncio
from aiko_api import Bot

bot = Bot(command_prefix="!")

@bot.command()
async def ping(ctx):
    await ctx.reply("Pong! 🏓")

@bot.event
async def on_ready(user):
    print(f"Logged in as {user.username}")

if __name__ == "__main__":
    asyncio.run(bot.start("YOUR_TOKEN"))
```

## Advanced Usage: Cogs and Sub-commands

```python
from aiko_api import Cog, command

class Moderation(Cog):
    @command()
    async def config(self, ctx):
        await ctx.send("Main config menu.")

    @config
    async def prefix(self, ctx, new_prefix: str):
        await ctx.send(f"Prefix updated to {new_prefix}")

bot.add_cog(Moderation(bot))
```

## License

This project is licensed under the MIT License.
