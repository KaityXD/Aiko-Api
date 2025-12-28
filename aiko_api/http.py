import aiohttp
import asyncio
import json
import sys
from .errors import HTTPException, Forbidden, NotFound, DiscordServerError, LoginFailure
from . import __version__
from .utils import get_super_properties, get_user_agent

class HTTPClient:
    """Represents an HTTP client sending HTTP requests to the Discord API."""

    def __init__(self, token=None):
        self.token = token
        self.base_url = "https://discord.com/api/v10"
        self.user_agent = get_user_agent()
        self._session = None
        self.super_properties = get_super_properties()

    async def close(self):
        if self._session:
            await self._session.close()

    async def request(self, method, endpoint, **kwargs):
        if not self._session:
            self._session = aiohttp.ClientSession(json_serialize=lambda x: json.dumps(x, separators=(',', ':')))

        headers = {
            "User-Agent": self.user_agent,
            "X-Super-Properties": self.super_properties,
            "Content-Type": "application/json"
        }

        if self.token:
            headers["Authorization"] = self.token

        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))

        url = self.base_url + endpoint
        
        # JSON handling
        if "json" in kwargs:
            kwargs["data"] = json.dumps(kwargs.pop("json"), separators=(',', ':'))

        async with self._session.request(method, url, headers=headers, **kwargs) as response:
            data = None
            text = await response.text(encoding='utf-8')
            try:
                if response.headers['content-type'] == 'application/json':
                    data = json.loads(text)
                else:
                    data = text
            except KeyError:
                pass

            if 200 <= response.status < 300:
                return data

            if response.status == 429:
                # Simple rate limit handling
                retry_after = data['retry_after']
                await asyncio.sleep(retry_after)
                return await self.request(method, endpoint, **kwargs)

            if response.status == 403:
                raise Forbidden(response, data)
            elif response.status == 404:
                raise NotFound(response, data)
            elif response.status >= 500:
                raise DiscordServerError(response, data)
            else:
                raise HTTPException(response, data)

    async def static_login(self, token):
        self.token = token
        try:
            return await self.request("GET", "/users/@me")
        except HTTPException as e:
            if e.status == 401:
                raise LoginFailure("Invalid token passed")
            raise

    async def send_message(self, channel_id, content):
        payload = {"content": content}
        return await self.request("POST", f"/channels/{channel_id}/messages", json=payload)
    
    async def get_gateway(self):
        return await self.request("GET", "/gateway")
    
    async def get_bot_gateway(self):
        return await self.request("GET", "/gateway/bot")
