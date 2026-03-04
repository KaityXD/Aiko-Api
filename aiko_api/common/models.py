# aiko_api/common/models.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import datetime


@dataclass(kw_only=True)
class Base:
    _state: Any = field(default=None, repr=False, compare=False)


@dataclass
class Snowflake(Base):
    id: str

    @property
    def created_at(self):
        timestamp = ((int(self.id) >> 22) + 1420070400000) / 1000
        return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)


@dataclass
class User(Snowflake):
    username: str
    discriminator: str
    avatar: Optional[str]
    bot: bool = False

    @property
    def mention(self):
        return f"<@{self.id}>"

    def __str__(self):
        return self.mention

    @property
    def display_name(self):
        return self.username

    async def send(self, content, **kwargs):
        if self._state:
            dm = await self._state.user.create_dm(self.id)
            return await self._state.messages.send(dm["id"], content, **kwargs)
        raise NotImplementedError("State not initialized")


@dataclass
class Member(User):
    nick: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    joined_at: Optional[str] = None

    @property
    def display_name(self):
        return self.nick if self.nick else self.username


@dataclass
class Role(Snowflake):
    name: str
    color: int = 0
    hoist: bool = False
    icon: Optional[str] = None
    unicode_emoji: Optional[str] = None
    position: int = 0
    permissions: str = "0"
    managed: bool = False
    mentionable: bool = False
    tags: Dict[str, Any] = field(default_factory=dict)

    @property
    def mention(self):
        return f"<@&{self.id}>"

    def __str__(self):
        return self.mention

    @property
    def created_timestamp(self):
        return self.created_at

    def has_permission(self, permission: int) -> bool:
        """Check if role has specific permission."""
        perms = int(self.permissions)
        return (perms & permission) == permission or (
            perms & 0x8
        ) == 0x8  # Administrator

    def is_bot_managed(self) -> bool:
        """Check if role is managed by a bot/application."""
        return self.tags.get("bot_id") is not None

    def is_integration(self) -> bool:
        """Check if role is managed by an integration."""
        return self.tags.get("integration_id") is not None

    def is_premium_subscriber(self) -> bool:
        """Check if role is for nitro boosters."""
        return self.tags.get("premium_subscriber") is not None


@dataclass
class PermissionOverwrite:
    id: str
    type: int  # 0 for role, 1 for member
    allow: str = "0"
    deny: str = "0"

    @property
    def allow_permissions(self) -> int:
        return int(self.allow)

    @property
    def deny_permissions(self) -> int:
        return int(self.deny)


class ChannelType:
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_ANNOUNCEMENT = 5
    ANNOUNCEMENT_THREAD = 10
    PUBLIC_THREAD = 11
    PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13
    GUILD_DIRECTORY = 14
    GUILD_FORUM = 15
    GUILD_MEDIA = 16


@dataclass
class Emoji:
    id: str
    name: str
    roles: List[str] = field(default_factory=list)
    user: Optional[Dict[str, Any]] = None
    require_colons: bool = True
    managed: bool = False
    animated: bool = False
    available: bool = True
    _state: Any = field(default=None, repr=False, compare=False)

    @property
    def mention(self) -> str:
        """Get the emoji mention string."""
        if self.animated:
            return f"<a:{self.name}:{self.id}>"
        return f"<{self.name}:{self.id}>"

    def __str__(self) -> str:
        return self.mention

    def is_usable(self) -> bool:
        """Check if emoji is available for use."""
        return self.available and not self.managed

    def requires_colons(self) -> bool:
        """Check if emoji requires colons."""
        return self.require_colons

    def is_animated(self) -> bool:
        """Check if emoji is animated."""
        return self.animated

    def url(self, size: int = 64) -> str:
        """Get emoji image URL."""
        extension = "gif" if self.animated else "png"
        return f"https://cdn.discordapp.com/emojis/{self.id}.{extension}?size={size}"


@dataclass
class Guild(Snowflake):
    name: str
    icon: Optional[str]
    owner_id: str
    roles: Dict[str, Any] = field(default_factory=dict)
    members: Dict[str, Member] = field(default_factory=dict)
    channels: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Channel(Snowflake):
    name: str
    type: int
    guild_id: Optional[str] = None
    position: int = 0
    parent_id: Optional[str] = None
    permission_overwrites: List[Dict[str, Any]] = field(default_factory=list)
    nsfw: bool = False
    topic: Optional[str] = None
    rate_limit_per_user: Optional[int] = None
    bitrate: Optional[int] = None
    user_limit: Optional[int] = None

    @property
    @property
    def mention(self):
        return f"<#{self.id}>"

    def __str__(self):
        return self.mention

    @property
    def is_text_channel(self) -> bool:
        """Check if this is a text channel."""
        return self.type in [ChannelType.GUILD_TEXT, ChannelType.GUILD_ANNOUNCEMENT]

    @property
    def is_voice_channel(self) -> bool:
        """Check if this is a voice channel."""
        return self.type in [ChannelType.GUILD_VOICE, ChannelType.GUILD_STAGE_VOICE]

    @property
    def is_category(self) -> bool:
        """Check if this is a category channel."""
        return self.type == ChannelType.GUILD_CATEGORY

    @property
    def is_thread(self) -> bool:
        """Check if this is a thread channel."""
        return self.type in [
            ChannelType.ANNOUNCEMENT_THREAD,
            ChannelType.PUBLIC_THREAD,
            ChannelType.PRIVATE_THREAD,
        ]

    def has_permission(self, user_permissions: int, permission: int) -> bool:
        """Check if user has specific permission in this channel."""
        return (user_permissions & permission) == permission or (
            user_permissions & 0x8
        ) == 0x8

    async def set_permissions(
        self, target_id: str, allow: int = 0, deny: int = 0, type: int = 0
    ) -> bool:
        """Set permissions for a role or member in this channel."""
        if self._state:
            return await self._state.channels.edit_permissions(
                self.id, target_id, allow, deny, type
            )
        return False

    async def send(self, content, **kwargs):
        if self._state:
            return await self._state.messages.send(self.id, content, **kwargs)


@dataclass
class Attachment(Snowflake):
    filename: str
    url: str
    proxy_url: str
    size: int
    height: Optional[int] = None
    width: Optional[int] = None
    content_type: Optional[str] = None
    ephemeral: bool = False

    @property
    def is_image(self):
        if self.content_type:
            return self.content_type.startswith("image/")
        return any(
            self.filename.lower().endswith(ext)
            for ext in (".png", ".jpg", ".jpeg", ".gif", ".webp")
        )

    def to_dict(self):
        data = {"name": self.name, "type": self.type}
        for attr in (
            "url",
            "state",
            "details",
            "application_id",
            "timestamps",
            "assets",
            "party",
            "buttons",
        ):
            val = getattr(self, attr)
            if val is not None:
                data[attr] = val
        return data


@dataclass
class Embed:
    title: Optional[str] = None
    type: str = "rich"
    description: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[str] = None
    color: Optional[int] = None
    footer: Optional[Dict[str, Any]] = None
    image: Optional[Dict[str, Any]] = None
    thumbnail: Optional[Dict[str, Any]] = None
    video: Optional[Dict[str, Any]] = None
    provider: Optional[Dict[str, Any]] = None
    author: Optional[Dict[str, Any]] = None
    fields: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def builder(cls) -> "EmbedBuilder":
        """Create a new embed builder."""
        from ..utils import EmbedBuilder

        return EmbedBuilder()

    def add_field(self, name: str, value: str, inline: bool = True) -> "Embed":
        """Add a field to the embed."""
        self.fields.append({"name": name, "value": value, "inline": inline})
        return self

    def set_author(
        self, name: str, url: Optional[str] = None, icon_url: Optional[str] = None
    ) -> "Embed":
        """Set the author of the embed."""
        self.author = {"name": name}
        if url:
            self.author["url"] = url
        if icon_url:
            self.author["icon_url"] = icon_url
        return self

    def set_footer(self, text: str, icon_url: Optional[str] = None) -> "Embed":
        """Set the footer of the embed."""
        self.footer = {"text": text}
        if icon_url:
            self.footer["icon_url"] = icon_url
        return self

    def set_image(self, url: str) -> "Embed":
        """Set the image of the embed."""
        self.image = {"url": url}
        return self

    def set_thumbnail(self, url: str) -> "Embed":
        """Set the thumbnail of the embed."""
        self.thumbnail = {"url": url}
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert embed to dictionary."""
        data = {}
        for key in ["title", "type", "description", "url", "timestamp", "color"]:
            value = getattr(self, key)
            if value is not None:
                data[key] = value

        for key in [
            "footer",
            "image",
            "thumbnail",
            "video",
            "provider",
            "author",
            "fields",
        ]:
            value = getattr(self, key)
            if value:
                data[key] = value

        return data


@dataclass
class Message(Snowflake):
    channel_id: str
    guild_id: Optional[str]
    author: User
    content: str
    timestamp: str
    tts: bool
    mention_everyone: bool
    attachments: List[Attachment] = field(default_factory=list)
    embeds: List[Embed] = field(default_factory=list)
    reactions: List[Any] = field(default_factory=list)

    @property
    def image_url(self) -> Optional[str]:
        """Returns the first image URL found in attachments or embeds."""
        for attachment in self.attachments:
            if attachment.is_image:
                return attachment.url
        for embed in self.embeds:
            if embed.image:
                return embed.image.get("url")
            if embed.thumbnail:
                return embed.thumbnail.get("url")
        return None

    @property
    def gif_url(self) -> Optional[str]:
        """Returns the first GIF URL found in attachments or embeds."""
        for attachment in self.attachments:
            if attachment.filename.lower().endswith(".gif") or (
                attachment.content_type == "image/gif"
            ):
                return attachment.url
        for embed in self.embeds:
            if embed.url and embed.url.lower().endswith(".gif"):
                return embed.url
            if embed.image and embed.image.get("url", "").lower().endswith(".gif"):
                return embed.image.get("url")
        return None

    async def reply(self, content, **kwargs):
        if self._state:
            return await self._state.messages.reply(
                self.channel_id, self.id, content, **kwargs
            )

    async def delete(self):
        if self._state:
            return await self._state.messages.delete(self.channel_id, self.id)

    async def edit(self, content, **kwargs):
        if self._state:
            return await self._state.messages.edit(
                self.channel_id, self.id, content, **kwargs
            )

    async def add_reaction(self, emoji):
        if self._state:
            await self._state.messages.add_reaction(self.channel_id, self.id, emoji)


@dataclass(kw_only=True)
class Activity:
    name: str
    type: int = 0
    url: Optional[str] = None
    state: Optional[str] = None
    details: Optional[str] = None
    application_id: Optional[str] = None
    timestamps: Optional[Dict[str, int]] = None
    assets: Optional[Dict[str, str]] = None
    party: Optional[Dict[str, Any]] = None
    buttons: Optional[List[str]] = None

    def to_dict(self):
        data = {"name": self.name, "type": self.type}
        for attr in (
            "url",
            "state",
            "details",
            "application_id",
            "timestamps",
            "assets",
            "party",
            "buttons",
        ):
            val = getattr(self, attr)
            if val is not None:
                data[attr] = val
        return data
