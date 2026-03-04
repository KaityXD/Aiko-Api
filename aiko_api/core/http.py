import json
import asyncio
import time
import re
from typing import Any, Optional, Dict
from curl_cffi import requests
from ..katlog import get_logger
from ..common.errors import (
    HTTPException,
    Forbidden,
    NotFound,
    DiscordServerError,
    LoginFailure,
)
from ..common.constants import DISCORD_API
from .headers import HeaderBuilder
from ..common.errors import (
    HTTPException,
    Forbidden,
    NotFound,
    DiscordServerError,
    LoginFailure,
    RateLimited,
    get_discord_error,
)

log = get_logger("aiko_api", level="DEBUG")


class Bucket:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.limit: int = 1
        self.remaining: int = 1
        self.reset_at: float = 0.0

    async def __aenter__(self):
        await self.lock.acquire()
        now = time.time()
        if self.remaining <= 0 and now < self.reset_at:
            delta = self.reset_at - now
            log.warn(f"Bucket exhausted. Waiting {delta:.2f}s")
            await asyncio.sleep(delta)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.lock.release()

    def update(self, response):
        headers = response.headers
        self.limit = int(headers.get("X-RateLimit-Limit", self.limit))
        self.remaining = int(headers.get("X-RateLimit-Remaining", self.remaining))
        self.reset_at = float(
            headers.get(
                "X-RateLimit-Reset",
                time.time() + float(headers.get("X-RateLimit-Reset-After", 0)),
            )
        )


class HTTPClient:
    def __init__(self, token=None, proxy=None, impersonate="chrome120", bot=False):
        self.token = token
        self.proxy = proxy
        self.impersonate = impersonate if not bot else None
        self.bot = bot
        self.base_url = DISCORD_API
        self.headers = HeaderBuilder(token, bot=bot)
        self._session = None
        self._global_over = asyncio.Event()
        self._global_over.set()
        self._buckets: Dict[str, Bucket] = {}

    def _get_route(self, method: str, endpoint: str) -> str:
        # Major parameters: channel_id, guild_id, webhook_id
        # We simplify to the endpoint itself but group by major ID
        route = f"{method} {endpoint}"
        match = re.search(r"/(channels|guilds|webhooks)/(\d+)", endpoint)
        if match:
            # Group by major parameter (e.g. /channels/123/messages -> /channels/123)
            return f"{method} /{match.group(1)}/{match.group(2)}"
        return route

    async def close(self):
        if self._session:
            await self._session.close()

    def _get_session(self):
        if not self._session:
            self._session = requests.AsyncSession(
                impersonate=self.impersonate,
                proxies={"http": self.proxy, "https": self.proxy}
                if self.proxy
                else None,
                headers=self.headers.build(),
            )
        return self._session

    async def request(self, method: str, endpoint: str, **kwargs):
        route = self._get_route(method, endpoint)
        bucket = self._buckets.get(route)
        if bucket is None:
            bucket = Bucket()
            self._buckets[route] = bucket

        await self._global_over.wait()

        async with bucket:
            session = self._get_session()
            url = self.base_url + endpoint

            context = kwargs.pop("context", None)
            headers = self.headers.build(context=context)
            if "headers" in kwargs:
                headers.update(kwargs.pop("headers"))

            files = kwargs.pop("files", None)
            data = kwargs.pop("data", None)
            json_payload = kwargs.pop("json", None)

            if files and "Content-Type" in headers:
                headers.pop("Content-Type")

            tries = 0
            max_retries = 5

            while tries < max_retries:
                mp = None
                attempt_kwargs = kwargs.copy()

                if files:
                    from curl_cffi import CurlMime

                    mp = CurlMime()
                    if data:
                        if isinstance(data, dict):
                            for k, v in data.items():
                                mp.addpart(name=k, data=str(v))
                        else:
                            mp.addpart(name="data", data=str(data))

                    if json_payload and not data:
                        mp.addpart(
                            name="payload_json",
                            data=json.dumps(json_payload, separators=(",", ":")),
                        )
                    elif json_payload:
                        mp.addpart(
                            name="json",
                            data=json.dumps(json_payload, separators=(",", ":")),
                        )

                    for name, file_info in files.items():
                        filename = None
                        if isinstance(file_info, tuple):
                            filename, fp = file_info
                        else:
                            fp = file_info

                        if isinstance(fp, str):
                            mp.addpart(name=name, filename=filename, local_path=fp)
                        elif hasattr(fp, "read"):
                            if hasattr(fp, "seek"):
                                fp.seek(0)
                            content = fp.read()
                            if not isinstance(content, bytes):
                                content = str(content).encode()
                            mp.addpart(name=name, filename=filename, data=content)
                        else:
                            content = fp
                            if not isinstance(content, bytes):
                                content = str(content).encode()
                            mp.addpart(name=name, filename=filename, data=content)
                    attempt_kwargs["multipart"] = mp
                else:
                    if data:
                        attempt_kwargs["data"] = data
                    if json_payload:
                        attempt_kwargs["json"] = json_payload

                try:
                    resp = await session.request(
                        method, url, headers=headers, **attempt_kwargs
                    )

                    # Update bucket limits
                    bucket.update(resp)

                    try:
                        data_resp = resp.json()
                    except:
                        data_resp = resp.text

                    # Global rate limit check
                    if resp.headers.get("X-RateLimit-Global") == "true":
                        self._global_over.clear()
                        retry_after = float(data_resp.get("retry_after", 1))
                        log.error(f"GLOBAL RATE LIMIT. Waiting {retry_after}s")
                        await asyncio.sleep(retry_after)
                        self._global_over.set()
                        continue

                    if resp.status_code == 429:
                        retry_after = (
                            data_resp.get("retry_after", 1)
                            if isinstance(data_resp, dict)
                            else 1
                        )
                        log.warn(f"Rate limited (429). Retrying after {retry_after}s")
                        await asyncio.sleep(retry_after)
                        continue

                    if 200 <= resp.status_code < 300:
                        return data_resp

                    if resp.status_code >= 500:
                        await asyncio.sleep(1 + tries * 2)
                        tries += 1
                        continue

                    class Dummy:
                        def __init__(self, status, text):
                            self.status = status
                            self.text = text

                    dummy = Dummy(resp.status_code, data_resp)

                    if resp.status_code == 403:
                        raise Forbidden(dummy, data_resp)
                    elif resp.status_code == 404:
                        raise NotFound(dummy, data_resp)
                    elif resp.status_code == 429:
                        raise RateLimited(dummy, data_resp)
                    else:
                        # Try to get Discord-specific error
                        raise get_discord_error(dummy, data_resp)

                except Exception as e:
                    if isinstance(e, (Forbidden, NotFound, HTTPException, RateLimited)):
                        raise
                    log.error(f"Request failed: {type(e).__name__}: {e}")
                    await asyncio.sleep(1 + tries * 2)
                    tries += 1
                    continue
                finally:
                    if mp:
                        mp.close()

            raise HTTPException(None, "Max retries exceeded")

    async def get(self, endpoint, **kwargs):
        return await self.request("GET", endpoint, **kwargs)

    async def post(self, endpoint, **kwargs):
        return await self.request("POST", endpoint, **kwargs)

    async def patch(self, endpoint, **kwargs):
        return await self.request("PATCH", endpoint, **kwargs)

    async def put(self, endpoint, **kwargs):
        return await self.request("PUT", endpoint, **kwargs)

    async def delete(self, endpoint, **kwargs):
        return await self.request("DELETE", endpoint, **kwargs)
