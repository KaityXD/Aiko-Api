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

## Advanced Usage: Plugins and Cogs

`aiko_api` features a powerful plugin system with built-in hot-reloading. It automatically detects and registers Cogs and standalone commands in a directory.

### 1. Create a Plugin (`plugins/moderation.py`)

```python
from aiko_api import Cog, command

class Moderation(Cog):
    # Root Command (No 'self' needed!)
    @command()
    async def config(ctx):
        await ctx.send("Main config menu.")

    # Sub-command: !config prefix
    @config
    async def prefix(ctx, new_prefix: str):
        await ctx.send(f"Prefix updated to {new_prefix}")

    # Deep Nesting: !config prefix reset
    @prefix
    async def reset(ctx):
        await ctx.send("Prefix reset to default.")
```

### 2. Load and Hot-Reload

```python
import asyncio
from aiko_api import Bot

async def main():
    bot = Bot(command_prefix="!")
    
    # Automatically load all Cogs and commands from a directory
    bot.load_plugins("plugins")
    
    # Start the hot-reloader in the background
    asyncio.create_task(bot.watch_plugins("plugins"))

    await bot.start("YOUR_TOKEN")

if __name__ == "__main__":
    asyncio.run(main())
```

## License

This project is licensed under the MIT License.
