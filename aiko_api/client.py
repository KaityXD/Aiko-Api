# aiko_api/client.py
import asyncio
from typing import Optional

try:
    import uvloop
except ImportError:
    uvloop = None

from .katlog import get_logger
from .core.http import HTTPClient
from .gateway import DiscordWebSocket
from .cache import Cache
from .actions.messages import MessageActions
from .actions.user import UserActions
from .actions.guilds import GuildActions
from .actions.roles import RoleActions
from .actions.channels import ChannelActions
from .actions.emojis import EmojiActions

log = get_logger("aiko_api", level="DEBUG")


class Client:
    def __init__(self, loop=None, proxy=None, bot=False, intents=None):
        self.loop = loop
        self.proxy = proxy
        self.bot = bot
        self.intents = intents
        self.http = HTTPClient(proxy=proxy, bot=bot)

        # Action components
        self.messages = MessageActions(self)
        self.user_actions = UserActions(self)
        self.guilds = GuildActions(self)
        self.roles = RoleActions(self)
        self.channels = ChannelActions(self)
        self.emojis = EmojiActions(self)

        self.ws = None
        self._event_map = {
            "READY": "on_ready",
            "MESSAGE_CREATE": "on_message_create",
            "GUILD_CREATE": "on_guild_create",
        }
        self._events = {}
        self.user = None
        self.cache = Cache(self)
        self._waiters = {}
        self._stop_event = asyncio.Event()

    def event(self, coro):
        if not asyncio.iscoroutinefunction(coro):
            raise TypeError("event registered must be a coroutine function")
        name = coro.__name__
        if name == "on_message":
            name = "on_message_create"

        if name not in self._events:
            self._events[name] = []
        self._events[name].append(coro)
        return coro

    async def dispatch(self, event, data):
        method_name = self._event_map.get(event, f"on_{event.lower()}")

        event_arg = data
        if event == "MESSAGE_CREATE":
            event_arg = self.cache.store_message(data)
        elif event == "READY":
            event_arg = self.user

        # Handle waiters
        if event.lower() in self._waiters:
            for future, check in self._waiters[event.lower()][:]:
                if not future.cancelled():
                    try:
                        if check(event_arg):
                            future.set_result(event_arg)
                            self._waiters[event.lower()].remove((future, check))
                    except Exception as e:
                        future.set_exception(e)
                        self._waiters[event.lower()].remove((future, check))

        if method_name in self._events:
            for coro in self._events[method_name]:
                try:
                    await coro(event_arg)
                except Exception as e:
                    log.error(f"Error in event {method_name}: {e}")

    async def wait_for(self, event, check=None, timeout=None):
        if not check:
            check = lambda *args: True
        future = self.loop.create_future()
        event = event.lower()
        if event not in self._waiters:
            self._waiters[event] = []
        self._waiters[event].append((future, check))
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            if event in self._waiters:
                self._waiters[event].remove((future, check))
            raise

    async def start(self, token, bot: Optional[bool] = None):
        if bot is not None:
            self.bot = bot
            self.http.bot = bot
            self.http.headers.bot = bot
        elif token.startswith("Bot "):
            self.bot = True
            self.http.bot = True
            self.http.headers.bot = True

        if self.loop is None:
            self.loop = asyncio.get_running_loop()
        self.http.token = token
        self.http.headers.token = token
        await self.user_actions.static_login(token)
        self.ws = DiscordWebSocket(self, self.loop)
        await self.ws.connect()
        await self._stop_event.wait()

    def run(self, token, bot: Optional[bool] = None):
        if self.loop is None:
            try:
                self.loop = asyncio.get_event_loop()
            except RuntimeError:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
        if uvloop:
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        try:
            self.loop.run_until_complete(self.start(token, bot=bot))
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self.loop.run_until_complete(self.close())
            self.loop.close()

    async def close(self):
        self._stop_event.set()
        if self.ws:
            await self.ws.close()
        await self.http.close()

    # Legacy/Shortcut methods
    async def send_message(self, *args, **kwargs):
        return await self.messages.send(*args, **kwargs)

    async def send_image(self, *args, **kwargs):
        return await self.messages.send_image(*args, **kwargs)

    def send_message_bg(self, *args, **kwargs):
        task = asyncio.create_task(self.send_message(*args, **kwargs))
        task.add_done_callback(
            lambda t: t.exception() and log.error(f"BG send failed: {t.exception()}")
        )
        return task

    async def change_presence(self, *args, **kwargs):
        return await self.user_actions.change_presence(*args, **kwargs)
