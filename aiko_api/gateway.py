import aiohttp
import asyncio
import json
import json
import sys
import time
import logging
from .errors import AikoException

log = logging.getLogger(__name__)

class ConnectionClosed(AikoException):
    pass

class DiscordWebSocket:
    """Implements the websocket connection to Discord's gateway."""
    
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

    async def connect(self):
        
        try:
            self.socket = await self.client.http._session.ws_connect(self.GATEWAY)
        except Exception as e:
            log.error(f"Failed to connect to gateway: {e}")
            raise

        self._closed = False
        await self.identify()
        self._keep_alive = asyncio.create_task(self.run())

    async def identify(self):
        payload = {
            "op": 2,
            "d": {
                "token": self.client.http.token,
                "properties": {
                    "os": sys.platform,
                    "browser": "Chrome",
                    "device": ""
                },
                "compress": False,
                "large_threshold": 250
            }
        }
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
                msg = await self.socket.receive()
            except Exception as e:
                log.error(f"Socket receive error: {e}")
                break

            if msg.type == aiohttp.WSMsgType.TEXT:
                await self.received_message(msg.data)
            elif msg.type == aiohttp.WSMsgType.BINARY:
                pass # Compression disabled
            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                log.info("WebSocket closed or error")
                break
        
        await self.close()

    async def received_message(self, data):
        if not data:
            return
            
        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            log.error(f"Received invalid JSON: {data}")
            return

        op = payload.get('op')
        data = payload.get('d')
        seq = payload.get('s')
        event = payload.get('t')

        if seq is not None:
            self.sequence = seq

        if op == 10: # Hello
            self.heartbeat_interval = data['heartbeat_interval']
            self._heartbeat_task = asyncio.create_task(self.heartbeat())
        elif op == 11: # Heartbeat ACK
            pass # TODO: Check for zombie connections
        elif op == 0: # Dispatch
            if event == "READY":
                self.session_id = data['session_id']
                self.client.user = self.client.cache.store_user(data['user'])
                log.info(f"Connected to Gateway: {self.client.user.username}#{self.client.user.discriminator}")
            
            elif event == "GUILD_CREATE":
                self.client.cache.store_guild(data)
                
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

    async def voice_state_update(self, guild_id, channel_id, self_mute=False, self_deaf=False):
        payload = {
            "op": 4,
            "d": {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "self_mute": self_mute,
                "self_deaf": self_deaf
            }
        }
        await self.send_json(payload)
