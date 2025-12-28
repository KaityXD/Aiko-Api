from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import datetime

@dataclass
@dataclass(slots=True)
class Snowflake:
    id: str

    @property
    def created_at(self):
        timestamp = ((int(self.id) >> 22) + 1420070400000) / 1000
        return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)

@dataclass
@dataclass(slots=True)
class User(Snowflake):
    username: str
    discriminator: str
    avatar: Optional[str]
    bot: bool = False
    
    @property
    def mention(self):
        return f"<@{self.id}>"
    
    @property
    def display_name(self):
        return self.username # TODO: Handle global names

@dataclass
@dataclass(slots=True)
class Member(User):
    nick: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    joined_at: Optional[str] = None
    
    @property
    def display_name(self):
        return self.nick if self.nick else self.username

@dataclass
@dataclass(slots=True)
class Guild(Snowflake):
    name: str
    icon: Optional[str]
    owner_id: str
    roles: Dict[str, Any] = field(default_factory=dict)
    members: Dict[str, Member] = field(default_factory=dict)
    channels: Dict[str, Any] = field(default_factory=dict)

@dataclass
@dataclass(slots=True)
class Channel(Snowflake):
    name: str
    type: int
    guild_id: Optional[str] = None

@dataclass
@dataclass(slots=True)
class Message(Snowflake):
    channel_id: str
    guild_id: Optional[str]
    author: User
    content: str
    timestamp: str
    tts: bool
    mention_everyone: bool
    attachments: List[Any] = field(default_factory=list)
    embeds: List[Any] = field(default_factory=list)
    reactions: List[Any] = field(default_factory=list)
