import base64
import json
import sys
import re
import requests
import datetime
from typing import Optional, Dict, Any, List
from .katlog import get_logger

log = get_logger("aiko_api", level="DEBUG")


# Discord permissions constants
class Permissions:
    CREATE_INSTANT_INVITE = 0x1
    KICK_MEMBERS = 0x2
    BAN_MEMBERS = 0x4
    ADMINISTRATOR = 0x8
    MANAGE_CHANNELS = 0x10
    MANAGE_GUILD = 0x20
    ADD_REACTIONS = 0x40
    VIEW_AUDIT_LOG = 0x80
    PRIORITY_SPEAKER = 0x100
    STREAM = 0x200
    VIEW_CHANNEL = 0x400
    SEND_MESSAGES = 0x800
    SEND_TTS_MESSAGES = 0x1000
    MANAGE_MESSAGES = 0x2000
    EMBED_LINKS = 0x4000
    ATTACH_FILES = 0x8000
    READ_MESSAGE_HISTORY = 0x10000
    MENTION_EVERYONE = 0x20000
    USE_EXTERNAL_EMOJIS = 0x40000
    VIEW_GUILD_INSIGHTS = 0x80000
    CONNECT = 0x100000
    SPEAK = 0x200000
    MUTE_MEMBERS = 0x400000
    DEAFEN_MEMBERS = 0x800000
    MOVE_MEMBERS = 0x1000000
    USE_VAD = 0x2000000
    CHANGE_NICKNAME = 0x4000000
    MANAGE_NICKNAMES = 0x8000000
    MANAGE_ROLES = 0x10000000
    MANAGE_WEBHOOKS = 0x20000000
    MANAGE_EMOJIS_AND_STICKERS = 0x40000000
    USE_APPLICATION_COMMANDS = 0x80000000
    REQUEST_TO_SPEAK = 0x100000000
    MANAGE_EVENTS = 0x200000000
    MANAGE_THREADS = 0x40000000
    CREATE_PUBLIC_THREADS = 0x80000000
    CREATE_PRIVATE_THREADS = 0x100000000
    USE_EXTERNAL_STICKERS = 0x200000000
    SEND_MESSAGES_IN_THREADS = 0x400000000
    USE_EMBEDDED_ACTIVITIES = 0x800000000
    MODERATE_MEMBERS = 0x1000000000


# Permission names for display
PERMISSION_NAMES = {
    Permissions.CREATE_INSTANT_INVITE: "Create Instant Invite",
    Permissions.KICK_MEMBERS: "Kick Members",
    Permissions.BAN_MEMBERS: "Ban Members",
    Permissions.ADMINISTRATOR: "Administrator",
    Permissions.MANAGE_CHANNELS: "Manage Channels",
    Permissions.MANAGE_GUILD: "Manage Guild",
    Permissions.ADD_REACTIONS: "Add Reactions",
    Permissions.VIEW_AUDIT_LOG: "View Audit Log",
    Permissions.PRIORITY_SPEAKER: "Priority Speaker",
    Permissions.STREAM: "Stream",
    Permissions.VIEW_CHANNEL: "View Channel",
    Permissions.SEND_MESSAGES: "Send Messages",
    Permissions.SEND_TTS_MESSAGES: "Send TTS Messages",
    Permissions.MANAGE_MESSAGES: "Manage Messages",
    Permissions.EMBED_LINKS: "Embed Links",
    Permissions.ATTACH_FILES: "Attach Files",
    Permissions.READ_MESSAGE_HISTORY: "Read Message History",
    Permissions.MENTION_EVERYONE: "Mention Everyone",
    Permissions.USE_EXTERNAL_EMOJIS: "Use External Emojis",
    Permissions.VIEW_GUILD_INSIGHTS: "View Guild Insights",
    Permissions.CONNECT: "Connect",
    Permissions.SPEAK: "Speak",
    Permissions.MUTE_MEMBERS: "Mute Members",
    Permissions.DEAFEN_MEMBERS: "Deafen Members",
    Permissions.MOVE_MEMBERS: "Move Members",
    Permissions.USE_VAD: "Use Voice Activity",
    Permissions.CHANGE_NICKNAME: "Change Nickname",
    Permissions.MANAGE_NICKNAMES: "Manage Nicknames",
    Permissions.MANAGE_ROLES: "Manage Roles",
    Permissions.MANAGE_WEBHOOKS: "Manage Webhooks",
    Permissions.MANAGE_EMOJIS_AND_STICKERS: "Manage Emojis and Stickers",
    Permissions.USE_APPLICATION_COMMANDS: "Use Application Commands",
    Permissions.REQUEST_TO_SPEAK: "Request to Speak",
    Permissions.MANAGE_EVENTS: "Manage Events",
    Permissions.MANAGE_THREADS: "Manage Threads",
    Permissions.CREATE_PUBLIC_THREADS: "Create Public Threads",
    Permissions.CREATE_PRIVATE_THREADS: "Create Private Threads",
    Permissions.USE_EXTERNAL_STICKERS: "Use External Stickers",
    Permissions.SEND_MESSAGES_IN_THREADS: "Send Messages in Threads",
    Permissions.USE_EMBEDDED_ACTIVITIES: "Use Embedded Activities",
    Permissions.MODERATE_MEMBERS: "Moderate Members",
}


def get_build_number():
    """Fetches the latest Discord client build number."""
    try:
        page = requests.get("https://discord.com/app", timeout=10).text
        assets = re.findall(r'src="/assets/([^"]+)"', page)

        for asset in reversed(assets):
            js = requests.get(f"https://discord.com/assets/{asset}", timeout=10).text
            if "buildNumber:" in js:
                return int(js.split('buildNumber:"')[1].split('"')[0])
    except Exception as e:
        log.error(f"Failed to fetch build number: {e}")
        return 254000  # Fallback


def get_super_properties():
    """Generates a valid X-Super-Properties header value."""
    build_num = get_build_number()
    properties = {
        "os": "Windows",
        "browser": "Chrome",
        "device": "",
        "system_locale": "en-US",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "browser_version": "120.0.0.0",
        "os_version": "10",
        "referrer": "",
        "referring_domain": "",
        "referrer_current": "",
        "referring_domain_current": "",
        "release_channel": "stable",
        "client_build_number": build_num,
        "client_event_source": None,
    }

    return base64.b64encode(json.dumps(properties).encode()).decode("utf-8")


def get_user_agent():
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


# Permission utilities
def calculate_permissions(
    base_permissions: int, overwrite_allow: int = 0, overwrite_deny: int = 0
) -> int:
    """Calculate effective permissions considering role overwrites."""
    # Remove denied permissions
    effective = base_permissions & ~overwrite_deny
    # Add allowed permissions
    effective |= overwrite_allow
    return effective


def has_permission(permissions: int, permission: int) -> bool:
    """Check if specific permission is granted."""
    return (permissions & permission) == permission or (
        permissions & Permissions.ADMINISTRATOR
    ) == Permissions.ADMINISTRATOR


def list_permissions(permissions: int) -> List[str]:
    """List all permissions that are granted."""
    granted = []
    for perm, name in PERMISSION_NAMES.items():
        if has_permission(permissions, perm):
            granted.append(name)
    return granted


def permission_names(permissions: int) -> str:
    """Get human-readable permission names."""
    perms = list_permissions(permissions)
    return ", ".join(perms)


# Snowflake utilities
def snowflake_to_timestamp(snowflake: str) -> datetime.datetime:
    """Convert Discord snowflake to timestamp."""
    timestamp = ((int(snowflake) >> 22) + 1420070400000) / 1000
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)


def timestamp_to_snowflake(timestamp: datetime.datetime) -> str:
    """Convert timestamp to Discord snowflake."""
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)

    milliseconds = int(timestamp.timestamp() * 1000)
    discord_timestamp = milliseconds - 1420070400000
    return str(discord_timestamp << 22)


def snowflake_to_worker_id(snowflake: str) -> int:
    """Extract worker ID from snowflake."""
    return (int(snowflake) & 0x3E0000) >> 17


def snowflake_to_process_id(snowflake: str) -> int:
    """Extract process ID from snowflake."""
    return (int(snowflake) & 0x1F000) >> 12


def snowflake_to_increment(snowflake: str) -> int:
    """Extract increment from snowflake."""
    return int(snowflake) & 0xFFF


# Embed builder
class EmbedBuilder:
    """Helper class for building embeds."""

    def __init__(self):
        self.embed = {"type": "rich", "fields": []}

    def set_title(self, title: str) -> "EmbedBuilder":
        """Set embed title."""
        self.embed["title"] = title
        return self

    def set_description(self, description: str) -> "EmbedBuilder":
        """Set embed description."""
        self.embed["description"] = description
        return self

    def set_color(self, color: int) -> "EmbedBuilder":
        """Set embed color."""
        self.embed["color"] = color
        return self

    def set_url(self, url: str) -> "EmbedBuilder":
        """Set embed URL."""
        self.embed["url"] = url
        return self

    def set_timestamp(
        self, timestamp: Optional[datetime.datetime] = None
    ) -> "EmbedBuilder":
        """Set embed timestamp."""
        if timestamp is None:
            timestamp = datetime.datetime.now(datetime.timezone.utc)
        self.embed["timestamp"] = timestamp.isoformat()
        return self

    def set_footer(self, text: str, icon_url: Optional[str] = None) -> "EmbedBuilder":
        """Set embed footer."""
        self.embed["footer"] = {"text": text}
        if icon_url:
            self.embed["footer"]["icon_url"] = icon_url
        return self

    def set_image(self, url: str) -> "EmbedBuilder":
        """Set embed image."""
        self.embed["image"] = {"url": url}
        return self

    def set_thumbnail(self, url: str) -> "EmbedBuilder":
        """Set embed thumbnail."""
        self.embed["thumbnail"] = {"url": url}
        return self

    def set_author(
        self, name: str, url: Optional[str] = None, icon_url: Optional[str] = None
    ) -> "EmbedBuilder":
        """Set embed author."""
        self.embed["author"] = {"name": name}
        if url:
            self.embed["author"]["url"] = url
        if icon_url:
            self.embed["author"]["icon_url"] = icon_url
        return self

    def add_field(self, name: str, value: str, inline: bool = True) -> "EmbedBuilder":
        """Add a field to embed."""
        self.embed["fields"].append({"name": name, "value": value, "inline": inline})
        return self

    def build(self) -> Dict[str, Any]:
        """Build the embed."""
        return self.embed


# Mention parsers
def parse_mention(mention: str) -> Optional[str]:
    """Parse a mention and extract the ID."""
    # User mention: <@123456789> or <@!123456789>
    user_match = re.match(r"<@!?([0-9]{15,20})>", mention)
    if user_match:
        return user_match.group(1)

    # Channel mention: <#123456789>
    channel_match = re.match(r"<#([0-9]{15,20})>", mention)
    if channel_match:
        return channel_match.group(1)

    # Role mention: <@&123456789>
    role_match = re.match(r"<@&([0-9]{15,20})>", mention)
    if role_match:
        return role_match.group(1)

    # Emoji: <:name:id> or <a:name:id>
    emoji_match = re.match(r"<a?:[a-zA-Z0-9_]+:([0-9]{15,20})>", mention)
    if emoji_match:
        return emoji_match.group(1)

    return None


def is_user_mention(mention: str) -> bool:
    """Check if string is a user mention."""
    return bool(re.match(r"<@!?[0-9]{15,20}>", mention))


def is_channel_mention(mention: str) -> bool:
    """Check if string is a channel mention."""
    return bool(re.match(r"<#[0-9]{15,20}>", mention))


def is_role_mention(mention: str) -> bool:
    """Check if string is a role mention."""
    return bool(re.match(r"<@&[0-9]{15,20}>", mention))


def is_emoji(emoji: str) -> bool:
    """Check if string is an emoji."""
    return bool(re.match(r"<a?:[a-zA-Z0-9_]+:[0-9]{15,20}>", emoji))


# File utilities
def is_valid_image_url(url: str) -> bool:
    """Check if URL is a valid image URL."""
    image_extensions = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp")
    return any(url.lower().endswith(ext) for ext in image_extensions)


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return filename.split(".")[-1].lower() if "." in filename else ""


def is_image_file(filename: str) -> bool:
    """Check if file is an image file."""
    image_extensions = ("jpg", "jpeg", "png", "gif", "webp", "bmp")
    return get_file_extension(filename) in image_extensions


# Text utilities
def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def clean_text(text: str) -> str:
    """Clean text by removing extra whitespace."""
    return " ".join(text.split())


def escape_markdown(text: str) -> str:
    """Escape Discord markdown characters."""
    markdown_chars = ["*", "_", "~", "`", "|", ">", "#", "-", "+"]
    for char in markdown_chars:
        text = text.replace(char, f"\\{char}")
    return text


def remove_markdown(text: str) -> str:
    """Remove Discord markdown formatting."""
    # Remove bold, italic, underline, strikethrough, code blocks, inline code
    patterns = [
        r"\*\*(.*?)\*\*",  # Bold
        r"\*(.*?)\*",  # Italic
        r"__(.*?)__",  # Underline
        r"~~(.*?)~~",  # Strikethrough
        r"`(.*?)`",  # Inline code
        r"```[\s\S]*?```",  # Code block
    ]

    for pattern in patterns:
        text = re.sub(pattern, r"\1", text)

    return text


# Time utilities
def format_time_ago(dt: datetime.datetime) -> str:
    """Format datetime as 'time ago' string."""
    now = datetime.datetime.now(datetime.timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)

    diff = now - dt

    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return f"{diff.seconds} second{'s' if diff.seconds != 1 else ''} ago"


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"
