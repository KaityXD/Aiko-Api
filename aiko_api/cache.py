from typing import Dict, Optional
from .models import User, Guild, Message, Channel

class Cache:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.guilds: Dict[str, Guild] = {}
        self.channels: Dict[str, Channel] = {}
        self.messages: Dict[str, Message] = {}
        
    def store_user(self, data) -> User:
        user = User(
            id=data['id'],
            username=data['username'],
            discriminator=data['discriminator'],
            avatar=data.get('avatar'),
            bot=data.get('bot', False)
        )
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def store_guild(self, data) -> Guild:
        guild = Guild(
            id=data['id'],
            name=data['name'],
            icon=data.get('icon'),
            owner_id=data['owner_id']
        )
        return guild

    def get_guild(self, guild_id: str) -> Optional[Guild]:
        return self.guilds.get(guild_id)
        
    def clear(self):
        self.users.clear()
        self.guilds.clear()
        self.channels.clear()
        self.messages.clear()
