# aiko_api/actions/messages.py
import json
import os
from typing import Optional, List, Any, Union, Tuple

class MessageActions:
    def __init__(self, state):
        self._state = state
        self._http = state.http

    async def send(
        self, 
        channel_id: Union[int, str], 
        content: str, 
        files: Optional[List[Union[str, Tuple[str, Any]]]] = None, 
        message_reference: Optional[dict] = None
    ):
        payload = {"content": content}
        if message_reference:
            payload["message_reference"] = message_reference

        if files:
            file_data = {}
            for i, item in enumerate(files):
                if isinstance(item, tuple):
                    filename, fp = item
                    file_data[f"file{i}"] = (filename, fp)
                else:
                    file_data[f"file{i}"] = item
            
            return await self._http.post(
                f"/channels/{channel_id}/messages", 
                json=payload, 
                files=file_data
            )

        return await self._http.post(f"/channels/{channel_id}/messages", json=payload)

    async def send_image(self, channel_id, url_or_path, content="", **kwargs):
        if url_or_path.startswith("http"):
            # Download and upload
            session = self._http._get_session()
            resp = await session.get(url_or_path)
            if resp.status_code == 200:
                filename = url_or_path.split("/")[-1].split("?")[0] or "image.png"
                if "." not in filename: filename += ".png"
                return await self.send(channel_id, content, files=[(filename, resp.content)], **kwargs)
        return await self.send(channel_id, content, files=[url_or_path], **kwargs)

    async def reply(self, channel_id, message_id, content, **kwargs):
        return await self.send(
            channel_id, 
            content, 
            message_reference={"message_id": str(message_id)}, 
            **kwargs
        )

    async def edit(self, channel_id, message_id, content):
        return await self._http.patch(
            f"/channels/{channel_id}/messages/{message_id}", 
            json={"content": content}
        )

    async def delete(self, channel_id, message_id):
        return await self._http.delete(f"/channels/{channel_id}/messages/{message_id}")

    async def add_reaction(self, channel_id, message_id, emoji):
        from urllib.parse import quote
        return await self._http.put(
            f"/channels/{channel_id}/messages/{message_id}/reactions/{quote(emoji)}/@me"
        )
