import asyncio
import json
import sys
import time
from curl_cffi import CurlWsFlag
from .katlog import get_logger
from .common.errors import AikoException

log = get_logger("aiko_api", level="DEBUG")


class ConnectionClosed(AikoException):
    pass


class DiscordWebSocket:
    """Implements the websocket connection to Discord's gateway using curl_cffi."""

    GATEWAY = "wss://gateway.discord.gg/?v=10&encoding=json"

    def __init__(self, client, loop=None):
        self.client = client
        self.loop = loop or asyncio.get_event_loop()
        self.socket = None
        self.heartbeat_interval = None
        self._heartbeat_task = None
        self.session_id = None
        self.sequence = None
        self._keep_alive = None
        self._closed = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 10
        self._base_delay = 1
        self._max_delay = 60
        self._ready = False

    async def connect(self):
        try:
            session = self.client.http._get_session()
            self.socket = await session.ws_connect(self.GATEWAY, headers=self.client.http.headers.build())
        except Exception as e:
            log.error(f"Failed to connect to gateway: {e}")
            raise

        self._closed = False
        self._ready = False
        await self.identify()
        await self._wait_for_ready()
        self._keep_alive = asyncio.create_task(self.run())

    async def identify(self):
        token = self.client.http.token
        if token.startswith("Bot "):
            token = token.split(" ", 1)[1]

        if getattr(self.client, "bot", False):
            properties = {"os": sys.platform, "browser": "aiko_api", "device": "aiko_api"}
        else:
            properties = {"os": "Windows", "browser": "Chrome", "device": ""}

        payload = {
            "op": 2,
            "d": {
                "token": token,
                "properties": properties,
                "compress": False,
                "large_threshold": 250,
            },
        }

        if getattr(self.client, "bot", False):
            payload["d"]["intents"] = getattr(self.client, "intents", 32767) or 32767

        await self.send_json(payload)

    async def send_json(self, data):
        if self.socket:
            await self.socket.send_str(json.dumps(data))

    async def heartbeat(self):
        while not self._closed:
            await asyncio.sleep(self.heartbeat_interval / 1000.0)
            if self._closed:
                break
            await self.send_json({"op": 1, "d": self.sequence})

    async def run(self):
        while not self._closed:
            try:
                data, msg_type = await self.socket.recv()
            except Exception as e:
                log.error(f"Socket receive error: {e}")
                break

            if msg_type == CurlWsFlag.TEXT:
                await self.received_message(data.decode() if data else "")
            elif msg_type == CurlWsFlag.BINARY:
                pass  # Compression disabled
            elif msg_type == CurlWsFlag.CLOSE:
                log.info("WebSocket closed")
                break

        if not self._closed:
            log.info("Connection lost, attempting to reconnect...")
            await self.reconnect()

    async def received_message(self, data):
        if not data:
            return

        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            log.error(f"Received invalid JSON: {data}")
            return

        op = payload.get("op")
        data = payload.get("d")
        seq = payload.get("s")
        event = payload.get("t")

        if seq is not None:
            self.sequence = seq

        if op == 10:  # Hello
            self.heartbeat_interval = data["heartbeat_interval"]
            self._heartbeat_task = asyncio.create_task(self.heartbeat())
        elif op == 11:  # Heartbeat ACK
            pass  # TODO: Check for zombie connections
        elif op == 7:  # Reconnect
            log.info("Gateway requested reconnect")
            await self.reconnect()
        elif op == 9:  # Invalid Session
            log.info("Invalid session, will retry with fresh connection")
            self.session_id = None
            self.sequence = None
            await asyncio.sleep(5)
            await self.reconnect()
        elif op == 0:  # Dispatch
            if event == "READY":
                self.session_id = data["session_id"]
                self._reconnect_attempts = 0
                self._ready = True
                self.client.user = self.client.cache.store_user(data["user"])
                log.info(
                    f"Connected to Gateway: {self.client.user.username}#{self.client.user.discriminator}"
                )

            elif event == "RESUMED":
                self._reconnect_attempts = 0
                self._ready = True
                log.info("Successfully resumed session")

            elif event == "GUILD_CREATE":
                self.client.cache.store_guild(data)

            elif event == "GUILD_MEMBER_ADD":
                self.client.cache.store_member(data['guild_id'], data)

            elif event == "GUILD_MEMBER_UPDATE":
                self.client.cache.store_member(data['guild_id'], data)

            elif event == "GUILD_MEMBER_REMOVE":
                guild = self.client.cache.get_guild(data['guild_id'])
                if guild:
                    guild.members.pop(data['user']['id'], None)

            elif event == "MESSAGE_CREATE":
                # We don't store messages in cache yet, but we could
                pass

            await self.client.dispatch(event, data)

    async def close(self):
        self._closed = True
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self.socket:
            await self.socket.close()

    async def reconnect(self):
        if self._keep_alive:
            self._keep_alive.cancel()

        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        self._closed = True
        if self.socket:
            try:
                await self.socket.close()
            except Exception:
                pass

        self._reconnect_attempts += 1

        if self._reconnect_attempts > self._max_reconnect_attempts:
            log.error(
                f"Max reconnection attempts ({self._max_reconnect_attempts}) reached. Giving up."
            )
            raise Exception("Max reconnection attempts reached")

        delay = min(
            self._base_delay * (2 ** (self._reconnect_attempts - 1)), self._max_delay
        )
        log.info(
            f"Reconnecting in {delay} seconds... (attempt {self._reconnect_attempts})"
        )

        await asyncio.sleep(delay)

        self._closed = False
        self._ready = False
        self.socket = None

        try:
            session = self.client.http._get_session()
            self.socket = await session.ws_connect(self.GATEWAY, headers=self.client.http.headers.build())
        except Exception as e:
            log.error(f"Failed to reconnect to gateway: {e}")
            await self.reconnect()
            return

        if self.session_id and self.sequence:
            log.info(f"Attempting to resume session {self.session_id}")
            await self.resume()
            await self._wait_for_ready()
        else:
            log.info("No session to resume, creating new connection")
            await self.identify()
            await self._wait_for_ready()

        self._keep_alive = asyncio.create_task(self.run())

    async def _wait_for_ready(self):
        while not hasattr(self, "_ready") or not self._ready:
            try:
                data, msg_type = await asyncio.wait_for(self.socket.recv(), timeout=30)
            except asyncio.TimeoutError:
                log.error("Timeout waiting for ready/hello")
                raise Exception("Failed to reconnect: timeout")
            except Exception as e:
                log.error(f"Error waiting for ready: {e}")
                raise

            if msg_type == CurlWsFlag.TEXT:
                await self.received_message(data.decode() if data else "")

    async def resume(self):
        token = self.client.http.token
        if token.startswith("Bot "):
            token = token.split(" ", 1)[1]

        payload = {
            "op": 6,
            "d": {
                "token": token,
                "session_id": self.session_id,
                "seq": self.sequence,
            },
        }
        await self.send_json(payload)

    async def voice_state_update(
        self, guild_id, channel_id, self_mute=False, self_deaf=False
    ):
        payload = {
            "op": 4,
            "d": {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "self_mute": self_mute,
                "self_deaf": self_deaf,
            },
        }
        await self.send_json(payload)

    async def change_presence(self, activity=None, status="online", since=0, afk=False):
        if not self._ready:
            log.warn("change_presence called before ready, waiting...")
            await self._wait_for_ready()

        payload = {
            "op": 3,
            "d": {
                "since": since,
                "activities": [activity.to_dict()] if activity else [],
                "status": status,
                "afk": afk,
            },
        }
        await self.send_json(payload)
