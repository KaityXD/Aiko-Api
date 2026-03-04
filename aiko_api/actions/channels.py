# aiko_api/actions/channels.py
import json
from typing import Optional, List, Dict, Any, Union
from ..common.models import Channel, ChannelType, PermissionOverwrite


class ChannelActions:
    def __init__(self, state):
        self._state = state
        self._http = state.http

    async def create(
        self,
        guild_id: str,
        name: str,
        type: int = 0,  # GUILD_TEXT
        topic: Optional[str] = None,
        nsfw: bool = False,
        rate_limit_per_user: Optional[int] = None,
        position: Optional[int] = None,
        permission_overwrites: Optional[List[Dict]] = None,
        parent_id: Optional[str] = None,
        default_auto_archive_duration: Optional[int] = None,
    ) -> Channel:
        """Create a new channel in a guild."""
        payload = {"name": name, "type": type}

        if topic is not None:
            payload["topic"] = topic
        if nsfw is not None:
            payload["nsfw"] = nsfw
        if rate_limit_per_user is not None:
            payload["rate_limit_per_user"] = rate_limit_per_user
        if position is not None:
            payload["position"] = position
        if permission_overwrites is not None:
            payload["permission_overwrites"] = permission_overwrites
        if parent_id is not None:
            payload["parent_id"] = parent_id
        if default_auto_archive_duration is not None:
            payload["default_auto_archive_duration"] = default_auto_archive_duration

        data = await self._http.post(f"/guilds/{guild_id}/channels", json=payload)
        return Channel(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            guild_id=data.get("guild_id"),
            position=data.get("position", 0),
            parent_id=data.get("parent_id"),
            permission_overwrites=data.get("permission_overwrites", []),
            nsfw=data.get("nsfw", False),
            topic=data.get("topic"),
            _state=self._state,
        )

    async def edit(
        self,
        channel_id: str,
        name: Optional[str] = None,
        type: Optional[int] = None,
        position: Optional[int] = None,
        topic: Optional[str] = None,
        nsfw: Optional[bool] = None,
        rate_limit_per_user: Optional[int] = None,
        permission_overwrites: Optional[List[Dict]] = None,
        parent_id: Optional[str] = None,
        default_auto_archive_duration: Optional[int] = None,
    ) -> Channel:
        """Edit an existing channel."""
        payload = {}

        if name is not None:
            payload["name"] = name
        if type is not None:
            payload["type"] = type
        if position is not None:
            payload["position"] = position
        if topic is not None:
            payload["topic"] = topic
        if nsfw is not None:
            payload["nsfw"] = nsfw
        if rate_limit_per_user is not None:
            payload["rate_limit_per_user"] = rate_limit_per_user
        if permission_overwrites is not None:
            payload["permission_overwrites"] = permission_overwrites
        if parent_id is not None:
            payload["parent_id"] = parent_id
        if default_auto_archive_duration is not None:
            payload["default_auto_archive_duration"] = default_auto_archive_duration

        data = await self._http.patch(f"/channels/{channel_id}", json=payload)
        return Channel(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            guild_id=data.get("guild_id"),
            position=data.get("position", 0),
            parent_id=data.get("parent_id"),
            permission_overwrites=data.get("permission_overwrites", []),
            nsfw=data.get("nsfw", False),
            topic=data.get("topic"),
            _state=self._state,
        )

    async def delete(self, channel_id: str) -> bool:
        """Delete a channel."""
        await self._http.delete(f"/channels/{channel_id}")
        return True

    async def get(self, channel_id: str) -> Optional[Channel]:
        """Get a specific channel by ID."""
        data = await self._http.get(f"/channels/{channel_id}")
        return Channel(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            guild_id=data.get("guild_id"),
            position=data.get("position", 0),
            parent_id=data.get("parent_id"),
            permission_overwrites=data.get("permission_overwrites", []),
            nsfw=data.get("nsfw", False),
            topic=data.get("topic"),
            _state=self._state,
        )

    async def list_guild_channels(self, guild_id: str) -> List[Channel]:
        """Get all channels in a guild."""
        data = await self._http.get(f"/guilds/{guild_id}/channels")
        channels = []
        for channel_data in data:
            channel = Channel(
                id=channel_data["id"],
                name=channel_data["name"],
                type=channel_data["type"],
                guild_id=channel_data.get("guild_id"),
                position=channel_data.get("position", 0),
                parent_id=channel_data.get("parent_id"),
                permission_overwrites=channel_data.get("permission_overwrites", []),
                nsfw=channel_data.get("nsfw", False),
                topic=channel_data.get("topic"),
                _state=self._state,
            )
            channels.append(channel)
        return channels

    async def edit_permissions(
        self,
        channel_id: str,
        overwrite_id: str,
        allow: int = 0,
        deny: int = 0,
        type: int = 0,  # 0 for role, 1 for member
    ) -> bool:
        """Edit channel permissions for a role or member."""
        payload = {"allow": str(allow), "deny": str(deny), "type": type}

        await self._http.put(
            f"/channels/{channel_id}/permissions/{overwrite_id}", json=payload
        )
        return True

    async def delete_permissions(self, channel_id: str, overwrite_id: str) -> bool:
        """Delete channel permissions for a role or member."""
        await self._http.delete(f"/channels/{channel_id}/permissions/{overwrite_id}")
        return True

    async def create_invite(
        self,
        channel_id: str,
        max_age: int = 86400,
        max_uses: int = 0,
        temporary: bool = False,
        unique: bool = True,
    ) -> Dict[str, Any]:
        """Create an invite for a channel."""
        payload = {
            "max_age": max_age,
            "max_uses": max_uses,
            "temporary": temporary,
            "unique": unique,
        }

        return await self._http.post(f"/channels/{channel_id}/invites", json=payload)

    async def get_invites(self, channel_id: str) -> List[Dict[str, Any]]:
        """Get all invites for a channel."""
        return await self._http.get(f"/channels/{channel_id}/invites")

    async def create_category(
        self,
        guild_id: str,
        name: str,
        position: Optional[int] = None,
        permission_overwrites: Optional[List[Dict]] = None,
    ) -> Channel:
        """Create a category channel."""
        return await self.create(
            guild_id=guild_id,
            name=name,
            type=4,  # GUILD_CATEGORY
            position=position,
            permission_overwrites=permission_overwrites,
        )

    async def create_text_channel(
        self,
        guild_id: str,
        name: str,
        topic: Optional[str] = None,
        nsfw: bool = False,
        rate_limit_per_user: Optional[int] = None,
        position: Optional[int] = None,
        permission_overwrites: Optional[List[Dict]] = None,
        parent_id: Optional[str] = None,
    ) -> Channel:
        """Create a text channel."""
        return await self.create(
            guild_id=guild_id,
            name=name,
            type=0,  # GUILD_TEXT
            topic=topic,
            nsfw=nsfw,
            rate_limit_per_user=rate_limit_per_user,
            position=position,
            permission_overwrites=permission_overwrites,
            parent_id=parent_id,
        )

    async def create_voice_channel(
        self,
        guild_id: str,
        name: str,
        bitrate: Optional[int] = None,
        user_limit: Optional[int] = None,
        position: Optional[int] = None,
        permission_overwrites: Optional[List[Dict]] = None,
        parent_id: Optional[str] = None,
        nsfw: bool = False,
    ) -> Channel:
        """Create a voice channel."""
        payload = {
            "name": name,
            "type": 2,  # GUILD_VOICE
            "nsfw": nsfw,
        }

        if bitrate is not None:
            payload["bitrate"] = bitrate
        if user_limit is not None:
            payload["user_limit"] = user_limit
        if position is not None:
            payload["position"] = position
        if permission_overwrites is not None:
            payload["permission_overwrites"] = permission_overwrites
        if parent_id is not None:
            payload["parent_id"] = parent_id

        data = await self._http.post(f"/guilds/{guild_id}/channels", json=payload)
        return Channel(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            guild_id=data.get("guild_id"),
            position=data.get("position", 0),
            parent_id=data.get("parent_id"),
            permission_overwrites=data.get("permission_overwrites", []),
            nsfw=data.get("nsfw", False),
            topic=data.get("topic"),
            _state=self._state,
        )
