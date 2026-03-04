# aiko_api/actions/emojis.py
import json
from typing import Optional, List, Dict, Any
from urllib.parse import quote
from ..common.models import Emoji


class EmojiActions:
    def __init__(self, state):
        self._state = state
        self._http = state.http

    async def get(self, guild_id: str, emoji_id: str) -> Optional[Emoji]:
        """Get a specific emoji by ID."""
        data = await self._http.get(f"/guilds/{guild_id}/emojis/{emoji_id}")
        return Emoji(
            id=data["id"],
            name=data["name"],
            roles=data.get("roles", []),
            user=data.get("user"),
            require_colons=data.get("require_colons", True),
            managed=data.get("managed", False),
            animated=data.get("animated", False),
            available=data.get("available", True),
            _state=self._state,
        )

    async def list(self, guild_id: str) -> List[Emoji]:
        """Get all emojis in a guild."""
        data = await self._http.get(f"/guilds/{guild_id}/emojis")
        emojis = []
        for emoji_data in data:
            emoji = Emoji(
                id=emoji_data["id"],
                name=emoji_data["name"],
                roles=emoji_data.get("roles", []),
                user=emoji_data.get("user"),
                require_colons=emoji_data.get("require_colons", True),
                managed=emoji_data.get("managed", False),
                animated=emoji_data.get("animated", False),
                available=emoji_data.get("available", True),
                _state=self._state,
            )
            emojis.append(emoji)
        return emojis

    async def create(
        self,
        guild_id: str,
        name: str,
        image: str,  # Base64 encoded image data
        roles: Optional[List[str]] = None,
        reason: Optional[str] = None,
    ) -> Emoji:
        """Create a new emoji."""
        payload = {"name": name, "image": image}

        if roles is not None:
            payload["roles"] = roles

        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason

        data = await self._http.post(
            f"/guilds/{guild_id}/emojis", json=payload, headers=headers
        )
        return Emoji(
            id=data["id"],
            name=data["name"],
            roles=data.get("roles", []),
            user=data.get("user"),
            require_colons=data.get("require_colons", True),
            managed=data.get("managed", False),
            animated=data.get("animated", False),
            available=data.get("available", True),
            _state=self._state,
        )

    async def edit(
        self,
        guild_id: str,
        emoji_id: str,
        name: Optional[str] = None,
        roles: Optional[List[str]] = None,
        reason: Optional[str] = None,
    ) -> Emoji:
        """Edit an existing emoji."""
        payload = {}

        if name is not None:
            payload["name"] = name
        if roles is not None:
            payload["roles"] = roles

        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason

        data = await self._http.patch(
            f"/guilds/{guild_id}/emojis/{emoji_id}", json=payload, headers=headers
        )
        return Emoji(
            id=data["id"],
            name=data["name"],
            roles=data.get("roles", []),
            user=data.get("user"),
            require_colons=data.get("require_colons", True),
            managed=data.get("managed", False),
            animated=data.get("animated", False),
            available=data.get("available", True),
            _state=self._state,
        )

    async def delete(
        self, guild_id: str, emoji_id: str, reason: Optional[str] = None
    ) -> bool:
        """Delete an emoji."""
        headers = {}
        if reason:
            headers["X-Audit-Log-Reason"] = reason

        await self._http.delete(
            f"/guilds/{guild_id}/emojis/{emoji_id}", headers=headers
        )
        return True

    async def add_reaction(self, channel_id: str, message_id: str, emoji: str) -> bool:
        """Add a reaction to a message."""
        encoded_emoji = quote(emoji.encode("utf-8"))
        await self._http.put(
            f"/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me"
        )
        return True

    async def remove_reaction(
        self,
        channel_id: str,
        message_id: str,
        emoji: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """Remove a reaction from a message."""
        encoded_emoji = quote(emoji.encode("utf-8"))
        if user_id:
            await self._http.delete(
                f"/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/{user_id}"
            )
        else:
            await self._http.delete(
                f"/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me"
            )
        return True

    async def get_reactions(
        self,
        channel_id: str,
        message_id: str,
        emoji: str,
        limit: int = 25,
        after: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get users who reacted with a specific emoji."""
        encoded_emoji = quote(emoji.encode("utf-8"))
        params = {"limit": limit}
        if after:
            params["after"] = after

        return await self._http.get(
            f"/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}",
            params=params,
        )

    async def remove_all_reactions(self, channel_id: str, message_id: str) -> bool:
        """Remove all reactions from a message."""
        await self._http.delete(
            f"/channels/{channel_id}/messages/{message_id}/reactions"
        )
        return True

    async def remove_all_reactions_for_emoji(
        self, channel_id: str, message_id: str, emoji: str
    ) -> bool:
        """Remove all reactions of a specific emoji from a message."""
        encoded_emoji = quote(emoji.encode("utf-8"))
        await self._http.delete(
            f"/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}"
        )
        return True

    def is_custom_emoji(self, emoji: str) -> bool:
        """Check if emoji is a custom emoji (has ID)."""
        return ":" in emoji and emoji.count(":") >= 2

    def parse_emoji(self, emoji: str) -> Dict[str, Any]:
        """Parse emoji string into components."""
        if self.is_custom_emoji(emoji):
            # Format: <:name:id> or <a:name:id> for animated
            parts = emoji.strip("<>").split(":")
            if len(parts) == 3:
                return {"name": parts[1], "id": parts[2], "animated": parts[0] == "a"}
        return {"name": emoji, "id": None, "animated": False}

    def format_emoji(self, name: str, emoji_id: str, animated: bool = False) -> str:
        """Format emoji components into string."""
        if emoji_id:
            prefix = "a" if animated else ""
            return f"<{prefix}:{name}:{emoji_id}>"
        return name

    async def create_from_url(
        self,
        guild_id: str,
        name: str,
        image_url: str,
        roles: Optional[List[str]] = None,
    ) -> Emoji:
        """Create emoji from image URL."""
        import base64
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    image_b64 = base64.b64encode(image_data).decode("utf-8")
                    content_type = resp.headers.get("content-type", "image/png")
                    extension = content_type.split("/")[-1] if content_type else "png"
                    image_data_uri = f"data:image/{extension};base64,{image_b64}"
                    return await self.create(guild_id, name, image_data_uri, roles)
                else:
                    raise Exception(f"Failed to download image: {resp.status}")

    def get_emoji_unicode(self, emoji: str) -> str:
        """Get unicode representation of emoji."""
        if self.is_custom_emoji(emoji):
            return emoji
        # For unicode emojis, return as-is
        return emoji
