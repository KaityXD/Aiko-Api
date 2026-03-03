# aiko_api Examples

This folder contains various examples demonstrating how to use the `aiko_api` library.

## Getting Started

Before running any example, replace `"YOUR_TOKEN_HERE"` with your actual Discord token.
Some examples also require a `"YOUR_CHANNEL_ID_HERE"`.

## Examples Overview

### Basic Usage
- `basic_client.py`: Demonstrates the `Client` class with event handlers (`on_ready`, `on_message_create`).
- `basic_bot.py`: Shows how to use the `Bot` class for command-based bot development.
- `cog_example.py`: Shows how to organize commands using `Cog` classes.
- `sync_http.py`: Shows how to use the synchronous `HTTP` client for scripts that don't use `asyncio`.

### Advanced Commands & Cogs
- `subcommands_example.py`: Demonstrates nested sub-commands using decorators (e.g., `!config prefix reset`).
- `smart_cogs_example.py`: Shows how to use the optional `self` parameters (Smart Signatures) and the clean `@cog.event` syntax for Cogs.
- `command_args_example.py`: Highlights automatic type conversion (int, bool) and keyword-only argument parsing for commands.
- `plugin_system_example.py`: Demonstrates the advanced plugin loader that can automatically register both Cogs and standalone functions from a directory, including hot-reloading.
- `selfbot_rpc.py`: Demonstrates how to spoof a detailed "Rich Presence" activity (like VALORANT) on a user account, including images and timestamps.

### Actions
- `message_actions.py`: Demonstrates sending, replying to, editing, deleting messages, and adding reactions.
- `user_actions.py`: Demonstrates changing presence, creating DM channels, and fetching relationships.
- `guild_actions.py`: Demonstrates guild-related actions like leaving a guild.
- `send_files_async.py`: Detailed examples for sending files with the async Client.
- `send_files_sync.py`: Detailed examples for sending files with the sync HTTP client.

### Advanced
- `hot_reload.py`: Shows how to use the bot's hot-reloader for plugins.
- `wait_for_example.py`: Demonstrates using `client.wait_for()` to wait for specific events.
- `error_handling.py`: Demonstrates catching and handling specific Discord API errors.
- `proxy_example.py`: Demonstrates using HTTP/SOCKS5 proxies with both async and sync clients.

### Legacy Examples (Originals)
- `bot_v1.py`: Original bot example.
- `curl_v1.py`: Original synchronous example.
- `loop_v1.py`: Original message loop example.

## Running Examples

Ensure you have the required dependencies installed:
```bash
pip install -r requirements.txt
```
Then run an example using Python:
```bash
python examples/basic_client.py
```
