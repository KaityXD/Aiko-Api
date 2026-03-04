# aiko_api/actions/user.py
import re
import io
from typing import Optional
from curl_cffi import requests

class UserActions:
    def __init__(self, state):
        self._state = state
        self._http = state.http

    async def static_login(self, token):
        return await self._http.get("/users/@me")

    async def edit_profile(self, payload):
        return await self._http.patch("/users/@me", json=payload)

    async def edit_settings(self, payload):
        return await self._http.patch("/users/@me/settings", json=payload)

    async def create_dm(self, recipient_id):
        return await self._http.post("/users/@me/channels", json={"recipient_id": recipient_id})

    async def get_relationships(self):
        return await self._http.get("/users/@me/relationships")

    async def add_friend(self, user_id):
        return await self._http.put(f"/users/@me/relationships/{user_id}", json={})

    async def remove_relationship(self, user_id):
        return await self._http.delete(f"/users/@me/relationships/{user_id}")

    async def block_user(self, user_id):
        return await self._http.put(f"/users/@me/relationships/{user_id}", json={"type": 2})

    async def change_presence(self, activity=None, status="online", since=0, afk=False):
        if activity and activity.assets:
            for key in ("large_image", "small_image"):
                if activity.assets.get(key) and activity.assets[key].startswith("http"):
                    new_asset = await self.upload_asset(activity.assets[key])
                    if new_asset: activity.assets[key] = new_asset
        
        if self._state.ws:
            await self._state.ws.change_presence(activity, status, since, afk)

    async def upload_asset(self, image_url: str) -> Optional[str]:
        discord_cdn_pattern = r"https?://(?:cdn\.discordapp\.com|media\.discordapp\.net)/attachments/(\d+)/(\d+)/(.+)"
        match = re.search(discord_cdn_pattern, image_url)
        if match:
            channel_id, attachment_id, filename = match.groups()
            return f"mp:attachments/{channel_id}/{attachment_id}/{filename}"

        try:
            async with requests.AsyncSession() as session:
                r = await session.get(image_url, proxies={"http": self._http.proxy, "https": self._http.proxy} if self._http.proxy else None)
                if r.status_code != 200: return None
                image_bytes = r.content
                filename = image_url.split("/")[-1].split("?")[0] or "asset.png"

                dm_channel = await self.create_dm(self._state.user.id)
                message = await self._state.messages.send(dm_channel["id"], "", files=[(filename, io.BytesIO(image_bytes))])
                
                if not message.get("attachments"): return None
                new_url = message["attachments"][0]["url"]
                new_match = re.search(discord_cdn_pattern, new_url)
                if not new_match: return None
                
                cid, aid, fname = new_match.groups()
                return f"mp:attachments/{cid}/{aid}/{fname}"
        except Exception:
            return None
