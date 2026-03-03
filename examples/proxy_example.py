import asyncio
from aiko_api import Client
from aiko_api.http_curl import HTTP

# This example demonstrates how to use proxies with both async and sync clients.

TOKEN = "YOUR_TOKEN_HERE"

# Format: "http://user:pass@host:port" or "socks5://host:port"
PROXY = "http://127.0.0.1:8080" # Replace with your actual proxy URL

# --- 1. Async Client Proxy ---
async def run_async_with_proxy():
    print("Initializing async client with proxy...")
    client = Client(proxy=PROXY)

    @client.event
    async def on_ready(user):
        print(f"Async: Logged in as {user.username} via proxy.")
        await client.close()

    try:
        await client.start(TOKEN)
    except Exception as e:
        print(f"Async proxy error: {e}")

# --- 2. Sync HTTP Proxy ---
def run_sync_with_proxy():
    print("Initializing sync HTTP client with proxy...")
    try:
        http = HTTP(token=TOKEN, proxy=PROXY)
        user = http.login()
        print(f"Sync: Logged in as: {user['username']} via proxy.")
    except Exception as e:
        print(f"Sync proxy error: {e}")

if __name__ == "__main__":
    # Note: These are for demonstration and may fail if the proxy is not valid.
    print("Trying sync HTTP first...")
    run_sync_with_proxy()

    print("
Trying async client...")
    try:
        asyncio.run(run_async_with_proxy())
    except KeyboardInterrupt:
        pass
