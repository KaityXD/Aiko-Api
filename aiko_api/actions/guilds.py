# aiko_api/actions/guilds.py
from typing import Union, Optional
import datetime

class GuildActions:
    def __init__(self, state):
        self._state = state
        self._http = state.http

    async def leave(self, guild_id: Union[int, str]):
        """Leaves a guild."""
        return await self._http.delete(f"/users/@me/guilds/{guild_id}")

    async def get_guild(self, guild_id: Union[int, str]):
        """Fetches guild information."""
        return await self._http.get(f"/guilds/{guild_id}")

    async def get_channels(self, guild_id: Union[int, str]):
        """Fetches channels in a guild."""
        return await self._http.get(f"/guilds/{guild_id}/channels")

    async def kick(self, guild_id: Union[int, str], user_id: Union[int, str], reason: Optional[str] = None):
        """Kicks a member from the guild."""
        headers = {}
        if reason:
            from urllib.parse import quote
            headers["X-Audit-Log-Reason"] = quote(reason)
        return await self._http.delete(f"/guilds/{guild_id}/members/{user_id}", headers=headers)

    async def ban(self, guild_id: Union[int, str], user_id: Union[int, str], delete_message_days: int = 0, reason: Optional[str] = None):
        """Bans a member from the guild."""
        headers = {}
        if reason:
            from urllib.parse import quote
            headers["X-Audit-Log-Reason"] = quote(reason)
        
        payload = {"delete_message_days": delete_message_days}
        return await self._http.put(f"/guilds/{guild_id}/bans/{user_id}", json=payload, headers=headers)

    async def unban(self, guild_id: Union[int, str], user_id: Union[int, str], reason: Optional[str] = None):
        """Unbans a member from the guild."""
        headers = {}
        if reason:
            from urllib.parse import quote
            headers["X-Audit-Log-Reason"] = quote(reason)
        return await self._http.delete(f"/guilds/{guild_id}/bans/{user_id}", headers=headers)

    async def edit_member(self, guild_id: Union[int, str], user_id: Union[int, str], payload: dict, reason: Optional[str] = None):
        """Edits a member (nick, roles, mute, deaf, communication_disabled_until)."""
        headers = {}
        if reason:
            from urllib.parse import quote
            headers["X-Audit-Log-Reason"] = quote(reason)
        return await self._http.patch(f"/guilds/{guild_id}/members/{user_id}", json=payload, headers=headers)

    async def timeout(self, guild_id: Union[int, str], user_id: Union[int, str], until: Optional[datetime.datetime], reason: Optional[str] = None):
        """Timeouts a member until a specific datetime (ISO8601). Set until to None to remove timeout."""
        payload = {
            "communication_disabled_until": until.isoformat() if until else None
        }
        return await self.edit_member(guild_id, user_id, payload, reason=reason)
