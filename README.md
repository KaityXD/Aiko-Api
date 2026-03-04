# 🚀 aiko_api

> A modern, efficient Discord API wrapper for Python with intelligent features and blazing-fast performance.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org/downloads)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/aiko-api.svg)](https://pypi.org/project/aiko-api/)
[![Downloads](https://pepy.tech/badge/aiko-api)](https://pepy.tech/project/aiko-api)

## ✨ Why aiko_api?

**aiko_api** is a cutting-edge Discord API wrapper designed for developers who want power, simplicity, and performance. Built on `curl_cffi` for superior HTTP performance and better impersonation capabilities.

### 🌟 Key Features

- **🧠 Smart Command System** - Intelligent argument parsing with type hints
- **🏗️ Flat Sub-command Hierarchy** - Clean, decorator-based command nesting
- **🔥 Hot-reloading Plugins** - Live code updates without restarts
- **🤖 Self & Bot Support** - Works with both user accounts and bot tokens
- **⚡ Blazing Fast** - Built on `curl_cffi` for optimal performance
- **🎯 Smart Signatures** - Optional `self` parameters in Cogs
- **📦 Advanced Plugin System** - Auto-discovery and loading

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install aiko-api
```

### From Source
```bash
git clone https://github.com/yourusername/aiko_api.git
cd aiko_api
pip install -e .
```

## 🚀 Quick Start

### Basic Bot
```python
import asyncio
from aiko_api import Bot

bot = Bot(command_prefix="!")

@bot.command()
async def ping(ctx):
    """A simple ping command"""
    await ctx.reply("Pong! 🏓")

@bot.event
async def on_ready(user):
    print(f"✅ Bot ready! Logged in as {user.username}")

if __name__ == "__main__":
    asyncio.run(bot.start("YOUR_TOKEN"))
```

### Client (Event-Only)
```python
import asyncio
from aiko_api import Client

client = Client()

@client.event
async def on_ready(user):
    print(f"✅ Client ready! Logged in as {user.username}")

@client.event
async def on_message_create(message):
    if message.content == "hello":
        await client.send_message(message.channel_id, "Hi there! 👋")

if __name__ == "__main__":
    asyncio.run(client.start("YOUR_TOKEN"))
```

## 🏗️ Advanced Features

### Smart Sub-commands

Create nested commands effortlessly:

```python
from aiko_api import Bot, Cog, command

class ConfigCog(Cog):
    @command()
    async def config(ctx):
        """Root command"""
        await ctx.send("Configuration menu")
    
    @config  # Sub-command decorator
    async def prefix(ctx, new_prefix: str):
        """!config prefix ?"""
        await ctx.send(f"Prefix set to: {new_prefix}")
    
    @prefix  # Deep nesting
    async def reset(ctx):
        """!config prefix reset"""
        await ctx.send("Prefix reset to default!")
```

### Intelligent Argument Parsing

Automatic type conversion and validation:

```python
@command()
async def roll(ctx, sides: int = 6):
    """Rolls a dice - !roll 20"""
    import random
    result = random.randint(1, sides)
    await ctx.send(f"🎲 Rolled: {result}")

@command()
async def toggle(ctx, feature: str, enabled: bool):
    """!toggle notifications on"""
    status = "✅ Enabled" if enabled else "❌ Disabled"
    await ctx.send(f"{feature}: {status}")
```

### 🔄 Hot-reloading Plugin System

#### 1. Create Plugin Directory
```
plugins/
├── moderation.py
├── fun.py
└── utils.py
```

#### 2. Create a Plugin (`plugins/moderation.py`)
```python
from aiko_api import Cog, command

class Moderation(Cog):
    @command()
    async def ban(ctx, user: str, *, reason: str = "No reason provided"):
        await ctx.send(f"🔨 Banned {user} for: {reason}")
    
    @command()
    async def kick(ctx, user: str):
        await ctx.send(f"👢 Kicked {user}")

# Auto-registration happens automatically!
```

#### 3. Load with Hot-reloading
```python
import asyncio
from aiko_api import Bot

async def main():
    bot = Bot(command_prefix="!")
    
    # Load all plugins from directory
    bot.load_plugins("plugins")
    
    # Enable hot-reloading (edit files without restart)
    asyncio.create_task(bot.watch_plugins("plugins"))
    
    await bot.start("YOUR_TOKEN")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📋 Examples

Check out the [`examples/`](examples/) directory for comprehensive examples:

- **[`basic_bot.py`](examples/basic_bot.py)** - Simple command bot
- **[`basic_client.py`](examples/basic_client.py)** - Event-only client
- **[`cog_example.py`](examples/cog_example.py)** - Cog organization
- **[`command_args_example.py`](examples/command_args_example.py)** - Argument parsing
- **[`subcommands_example.py`](examples/subcommands_example.py)** - Nested commands
- **[`hot_reload.py`](examples/hot_reload.py)** - Plugin hot-reloading
- **[`message_actions.py`](examples/message_actions.py)** - Message operations
- **[`user_actions.py`](examples/user_actions.py)** - User operations
- **[`wait_for_example.py`](examples/wait_for_example.py)** - Event waiting

## 🔧 Configuration

### Environment Variables
```bash
export DISCORD_TOKEN="your_token_here"
```

### Proxy Support
```python
# HTTP/SOCKS5 proxy support
client = Client(proxy="http://user:pass@proxy:8080")
```

## 🛠️ API Reference

### Bot Class
```python
from aiko_api import Bot

bot = Bot(
    command_prefix="!",      # Command prefix
    case_insensitive=True,   # Case-insensitive commands
    strip_after_prefix=True # Strip whitespace after prefix
)
```

### Client Class
```python
from aiko_api import Client

client = Client(
    proxy=None,     # Proxy URL (optional)
    bot=False       # Bot vs user account
)
```

### Decorators
```python
from aiko_api import command, Cog

@command(name="custom_name", aliases=["alt"])
async def my_command(ctx, arg: str):
    pass

class MyCog(Cog):
    @command()
    async def cog_command(self, ctx):
        pass
```

## 🚀 Performance

- **HTTP Client**: Built on `curl_cffi` for superior performance
- **Connection Pooling**: Automatic connection reuse
- **Async/Await**: Full async support for non-blocking operations
- **Memory Efficient**: Optimized memory usage for large bots

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
```bash
git clone https://github.com/yourusername/aiko_api.git
cd aiko_api
pip install -e .[dev]
```

### Running Tests
```bash
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for the Discord community
- Powered by [curl_cffi](https://github.com/yifeikong/curl_cffi) for HTTP excellence
- Inspired by discord.py and other amazing libraries

## 📞 Support

- 💬 **Discord Server**: [Join our community](https://discord.gg/yourserver)
- 🐛 **Issues**: [Report bugs](https://github.com/yourusername/aiko_api/issues)
- 📧 **Email**: support@aiko-api.com

---

**⭐ Star this repo if you find it helpful!**