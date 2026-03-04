# aiko_api/actions/roles.py
import json
from typing import Optional, List, Dict, Any
from ..common.models import Role


class RoleActions:
    def __init__(self, state):
        self._state = state
        self._http = state.http

    async def create(
        self,
        guild_id: str,
        name: str,
        permissions: int = 0,
        color: int = 0,
        hoist: bool = False,
        icon: Optional[str] = None,
        unicode_emoji: Optional[str] = None,
        mentionable: bool = False,
    ) -> Role:
        """Create a new role in a guild."""
        payload = {
            "name": name,
            "permissions": str(permissions),
            "color": color,
            "hoist": hoist,
            "mentionable": mentionable,
        }

        if icon is not None:
            payload["icon"] = icon
        if unicode_emoji is not None:
            payload["unicode_emoji"] = unicode_emoji

        data = await self._http.post(f"/guilds/{guild_id}/roles", json=payload)
        return Role(
            id=data["id"],
            name=data["name"],
            color=data.get("color", 0),
            hoist=data.get("hoist", False),
            icon=data.get("icon"),
            unicode_emoji=data.get("unicode_emoji"),
            position=data.get("position", 0),
            permissions=data.get("permissions", "0"),
            managed=data.get("managed", False),
            mentionable=data.get("mentionable", False),
            tags=data.get("tags", {}),
            _state=self._state,
        )

    async def edit(
        self,
        guild_id: str,
        role_id: str,
        name: Optional[str] = None,
        permissions: Optional[int] = None,
        color: Optional[int] = None,
        hoist: Optional[bool] = None,
        icon: Optional[str] = None,
        unicode_emoji: Optional[str] = None,
        mentionable: Optional[bool] = None,
    ) -> Role:
        """Edit an existing role."""
        payload = {}

        if name is not None:
            payload["name"] = name
        if permissions is not None:
            payload["permissions"] = str(permissions)
        if color is not None:
            payload["color"] = color
        if hoist is not None:
            payload["hoist"] = hoist
        if icon is not None:
            payload["icon"] = icon
        if unicode_emoji is not None:
            payload["unicode_emoji"] = unicode_emoji
        if mentionable is not None:
            payload["mentionable"] = mentionable

        data = await self._http.patch(
            f"/guilds/{guild_id}/roles/{role_id}", json=payload
        )
        return Role(
            id=data["id"],
            name=data["name"],
            color=data.get("color", 0),
            hoist=data.get("hoist", False),
            icon=data.get("icon"),
            unicode_emoji=data.get("unicode_emoji"),
            position=data.get("position", 0),
            permissions=data.get("permissions", "0"),
            managed=data.get("managed", False),
            mentionable=data.get("mentionable", False),
            tags=data.get("tags", {}),
            _state=self._state,
        )

    async def delete(self, guild_id: str, role_id: str) -> bool:
        """Delete a role from a guild."""
        await self._http.delete(f"/guilds/{guild_id}/roles/{role_id}")
        return True

    async def get(self, guild_id: str, role_id: str) -> Optional[Role]:
        """Get a specific role by ID."""
        roles = await self.list(guild_id)
        for role in roles:
            if role.id == role_id:
                return role
        return None

    async def list(self, guild_id: str) -> List[Role]:
        """Get all roles in a guild."""
        data = await self._http.get(f"/guilds/{guild_id}/roles")
        roles = []
        for role_data in data:
            role = Role(
                id=role_data["id"],
                name=role_data["name"],
                color=role_data.get("color", 0),
                hoist=role_data.get("hoist", False),
                icon=role_data.get("icon"),
                unicode_emoji=role_data.get("unicode_emoji"),
                position=role_data.get("position", 0),
                permissions=role_data.get("permissions", "0"),
                managed=role_data.get("managed", False),
                mentionable=role_data.get("mentionable", False),
                tags=role_data.get("tags", {}),
                _state=self._state,
            )
            roles.append(role)
        return roles

    async def add_member_role(self, guild_id: str, user_id: str, role_id: str) -> bool:
        """Add a role to a guild member."""
        await self._http.put(f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}")
        return True

    async def remove_member_role(
        self, guild_id: str, user_id: str, role_id: str
    ) -> bool:
        """Remove a role from a guild member."""
        await self._http.delete(f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}")
        return True

    async def move_role(self, guild_id: str, role_id: str, position: int) -> bool:
        """Move a role to a specific position."""
        payload = {"id": role_id, "position": position}
        await self._http.patch(f"/guilds/{guild_id}/roles", json=[payload])
        return True

    def calculate_permissions(
        self, base_permissions: int, overwrite_allow: int = 0, overwrite_deny: int = 0
    ) -> int:
        """Calculate effective permissions considering role overwrites."""
        # Remove denied permissions
        effective = base_permissions & ~overwrite_deny
        # Add allowed permissions
        effective |= overwrite_allow
        return effective

    def has_permission(self, permissions: int, permission: int) -> bool:
        """Check if specific permission is granted."""
        return (permissions & permission) == permission
