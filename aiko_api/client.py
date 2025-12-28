import asyncio
try:
    import uvloop
except ImportError:
    uvloop = None
import logging
from .http import HTTPClient
from .gateway import DiscordWebSocket
from .models import User, Message
from .cache import Cache

log = logging.getLogger(__name__)

class Client:
    def __init__(self, loop=None):
        self.loop = loop
        self.http = HTTPClient()
        self.ws = None
        self._events = {}
        self._event_map = {
            "READY": "on_ready",
            "MESSAGE_CREATE": "on_message_create",
            "GUILD_CREATE": "on_guild_create"
        }
        self.user = None
        self.cache = Cache()

    def event(self, coro):
        """A decorator that registers an event to listen to."""
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError('event registered must be a coroutine function')

        self._events[coro.__name__] = coro
        return coro

    async def dispatch(self, event, data):
        method_name = self._event_map.get(event)
        if not method_name:
            # Fallback for unknown events
            method_name = f"on_{event.lower()}"
        
        # Internal handling
        if method_name == "on_ready":
            pass # User is already set in gateway

        # User handling
        if method_name in self._events:
            event_arg = data
            if event == "MESSAGE_CREATE":
                author = self.cache.store_user(data['author'])
                event_arg = Message(
                    id=data['id'],
                    channel_id=data['channel_id'],
                    guild_id=data.get('guild_id'),
                    author=author,
                    content=data.get('content', ''),
                    timestamp=data['timestamp'],
                    tts=data.get('tts', False),
                    mention_everyone=data.get('mention_everyone', False),
                    attachments=data.get('attachments', []),
                    embeds=data.get('embeds', []),
                    reactions=data.get('reactions', [])
                )
            
            try:
                await self._events[method_name](event_arg)
            except Exception as e:
                log.error(f"Error in event {method_name}: {e}")

    async def start(self, token):
        print("Client.start called", flush=True)
        if self.loop is None:
            self.loop = asyncio.get_running_loop()
            
        self.http.token = token
        print("Logging in via HTTP...", flush=True)
        await self.http.static_login(token)
        print("HTTP login successful. Connecting to Gateway...", flush=True)
        self.ws = DiscordWebSocket(self, self.loop)
        await self.ws.connect()
        print("Gateway connected.", flush=True)
        # The ws.connect() method spawns a task, so we need to keep the loop running
        # In a real app, we might want to wait on something specific or just sleep forever
        while True:
            await asyncio.sleep(3600)

    def run(self, token):
        print("Client.run called", flush=True)
        if self.loop is None:
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
        
        if uvloop:
            print("Using uvloop policy", flush=True)
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        
        print(f"Using loop: {self.loop}", flush=True)
        try:
            print("Calling run_until_complete...", flush=True)
            self.loop.run_until_complete(self.start(token))
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.close())
        finally:
            self.loop.close()

    async def close(self):
        if self.ws:
            await self.ws.close()
        await self.http.close()

    async def send_message(self, channel_id, content):
        """Sends a message to a channel."""
        return await self.http.send_message(channel_id, content)

    async def join_voice_channel(self, guild_id, channel_id, self_mute=False, self_deaf=False):
        """Joins a voice channel."""
        if self.ws:
            await self.ws.voice_state_update(guild_id, channel_id, self_mute, self_deaf)
