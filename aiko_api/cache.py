from typing import Dict, Optional, Any, Deque, List
from collections import deque
import time
import threading
from .common.models import (
    User,
    Guild,
    Message,
    Channel,
    Member,
    Attachment,
    Embed,
    Role,
)


class CacheStats:
    """Cache statistics tracking."""

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.updates = 0
        self.clears = 0
        self.start_time = time.time()

    def hit_ratio(self) -> float:
        """Calculate cache hit ratio."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def total_requests(self) -> int:
        """Get total number of cache requests."""
        return self.hits + self.misses

    def uptime(self) -> float:
        """Get cache uptime in seconds."""
        return time.time() - self.start_time


class ExpiringCache:
    """Cache with expiration support."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    self._access_times[key] = time.time()
                    return value
                else:
                    # Expired
                    del self._cache[key]
                    del self._access_times[key]
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set item in cache."""
        with self._lock:
            if ttl is None:
                ttl = self.default_ttl

            expiry = time.time() + ttl

            # Check if we need to evict
            if key not in self._cache and len(self._cache) >= self.max_size:
                self._evict_oldest()

            self._cache[key] = (value, expiry)
            self._access_times[key] = time.time()

    def delete(self, key: str) -> bool:
        """Delete item from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                del self._access_times[key]
                return True
            return False

    def clear(self):
        """Clear all items from cache."""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()

    def cleanup_expired(self):
        """Remove expired items."""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key
                for key, (_, expiry) in self._cache.items()
                if current_time >= expiry
            ]
            for key in expired_keys:
                del self._cache[key]
                del self._access_times[key]

    def _evict_oldest(self):
        """Evict the oldest accessed item."""
        if not self._access_times:
            return

        oldest_key = min(self._access_times.items(), key=lambda x: x[1])[0]
        del self._cache[oldest_key]
        del self._access_times[oldest_key]

    def __len__(self):
        return len(self._cache)


class Cache:
    def __init__(self, client):
        self.client = client
        self.stats = CacheStats()

        # Configuration
        self.config = {
            "max_users": 10000,
            "max_guilds": 1000,
            "max_channels": 5000,
            "max_messages": 5000,
            "max_roles": 2000,
            "default_ttl": 3600,  # 1 hour
            "cleanup_interval": 300,  # 5 minutes
            "track_stats": True,
        }

        # Expiring caches
        self._user_cache = ExpiringCache(
            self.config["max_users"], self.config["default_ttl"]
        )
        self._guild_cache = ExpiringCache(
            self.config["max_guilds"], self.config["default_ttl"]
        )
        self._channel_cache = ExpiringCache(
            self.config["max_channels"], self.config["default_ttl"]
        )
        self._message_cache = ExpiringCache(
            self.config["max_messages"], self.config["default_ttl"]
        )
        self._role_cache = ExpiringCache(
            self.config["max_roles"], self.config["default_ttl"]
        )

        # Deques for message history
        self.messages: Deque[Message] = deque(maxlen=self.config["max_messages"])

        # Cache cleanup task
        self._cleanup_task = None
        self._stop_cleanup = False

    def configure(self, **kwargs):
        """Configure cache settings."""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value

        # Update cache sizes
        self._user_cache.max_size = self.config["max_users"]
        self._guild_cache.max_size = self.config["max_guilds"]
        self._channel_cache.max_size = self.config["max_channels"]
        self._message_cache.max_size = self.config["max_messages"]
        self._role_cache.max_size = self.config["max_roles"]
        self._user_cache.default_ttl = self.config["default_ttl"]
        self._guild_cache.default_ttl = self.config["default_ttl"]
        self._channel_cache.default_ttl = self.config["default_ttl"]
        self._message_cache.default_ttl = self.config["default_ttl"]
        self._role_cache.default_ttl = self.config["default_ttl"]

        # Update message deque
        self.messages = deque(maxlen=self.config["max_messages"])

    def start_cleanup_task(self):
        """Start the background cleanup task."""
        if self._cleanup_task is None:
            import asyncio

            self._stop_cleanup = False
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    def stop_cleanup_task(self):
        """Stop the background cleanup task."""
        if self._cleanup_task:
            self._stop_cleanup = True
            self._cleanup_task.cancel()
            self._cleanup_task = None

    async def _cleanup_loop(self):
        """Background task to clean up expired cache entries."""
        import asyncio

        while not self._stop_cleanup:
            await asyncio.sleep(self.config["cleanup_interval"])
            self.cleanup_expired()

    def cleanup_expired(self):
        """Clean up expired entries from all caches."""
        self._user_cache.cleanup_expired()
        self._guild_cache.cleanup_expired()
        self._channel_cache.cleanup_expired()
        self._message_cache.cleanup_expired()
        self._role_cache.cleanup_expired()

    def clear(self):
        """Clear all caches."""
        self._user_cache.clear()
        self._guild_cache.clear()
        self._channel_cache.clear()
        self._message_cache.clear()
        self._role_cache.clear()
        self.messages.clear()

        if self.config["track_stats"]:
            self.stats.clears += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.config["track_stats"]:
            return {"stats_tracking_disabled": True}

        return {
            "hits": self.stats.hits,
            "misses": self.stats.misses,
            "evictions": self.stats.evictions,
            "updates": self.stats.updates,
            "clears": self.stats.clears,
            "hit_ratio": self.stats.hit_ratio(),
            "total_requests": self.stats.total_requests(),
            "uptime": self.stats.uptime(),
            "cache_sizes": {
                "users": len(self._user_cache),
                "guilds": len(self._guild_cache),
                "channels": len(self._channel_cache),
                "messages": len(self._message_cache),
                "roles": len(self._role_cache),
                "message_deque": len(self.messages),
            },
            "config": self.config,
        }

    def store_user(self, data: Dict[str, Any]) -> User:
        """Store user in cache."""
        user_id = data["id"]

        # Check cache first
        cached_user = self._user_cache.get(user_id)
        if cached_user:
            if self.config["track_stats"]:
                self.stats.hits += 1
            return cached_user

        if self.config["track_stats"]:
            self.stats.misses += 1

        # Create new user
        user = User(
            id=user_id,
            username=data["username"],
            discriminator=data.get("discriminator", "0000"),
            avatar=data.get("avatar"),
            bot=data.get("bot", False),
            _state=self.client,
        )

        # Cache the user
        self._user_cache.set(user_id, user)
        if self.config["track_stats"]:
            self.stats.updates += 1

        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user from cache."""
        user = self._user_cache.get(user_id)
        if user:
            if self.config["track_stats"]:
                self.stats.hits += 1
            return user

        if self.config["track_stats"]:
            self.stats.misses += 1
        return None

    def store_member(self, guild_id: str, data: Dict[str, Any]) -> Member:
        """Store member in cache."""
        user_data = data.get("user")
        if not user_data:
            user_data = data

        user = self.store_user(user_data)
        member = Member(
            id=user.id,
            username=user.username,
            discriminator=user.discriminator,
            avatar=user.avatar,
            bot=user.bot,
            nick=data.get("nick"),
            roles=data.get("roles", []),
            joined_at=data.get("joined_at"),
            _state=self.client,
        )

        guild = self.get_guild(guild_id)
        if guild:
            guild.members[member.id] = member

        return member

    def store_guild(self, data: Dict[str, Any]) -> Guild:
        """Store guild in cache."""
        guild_id = data["id"]

        # Check cache first
        cached_guild = self._guild_cache.get(guild_id)
        if cached_guild:
            if self.config["track_stats"]:
                self.stats.hits += 1
            return cached_guild

        if self.config["track_stats"]:
            self.stats.misses += 1

        guild = Guild(
            id=guild_id,
            name=data["name"],
            icon=data.get("icon"),
            owner_id=data.get("owner_id", ""),
            _state=self.client,
        )

        # Cache the guild
        self._guild_cache.set(guild_id, guild)
        if self.config["track_stats"]:
            self.stats.updates += 1

        # Process channels and members
        for channel_data in data.get("channels", []):
            channel_data["guild_id"] = guild_id
            self.store_channel(channel_data)

        for member_data in data.get("members", []):
            self.store_member(guild_id, member_data)

        return guild

    def get_guild(self, guild_id: str) -> Optional[Guild]:
        """Get guild from cache."""
        guild = self._guild_cache.get(guild_id)
        if guild:
            if self.config["track_stats"]:
                self.stats.hits += 1
            return guild

        if self.config["track_stats"]:
            self.stats.misses += 1
        return None

    def store_channel(self, data: Dict[str, Any]) -> Channel:
        """Store channel in cache."""
        channel_id = data["id"]

        # Check cache first
        cached_channel = self._channel_cache.get(channel_id)
        if cached_channel:
            if self.config["track_stats"]:
                self.stats.hits += 1
            return cached_channel

        if self.config["track_stats"]:
            self.stats.misses += 1

        channel = Channel(
            id=channel_id,
            name=data.get("name", "unknown"),
            type=data.get("type", 0),
            guild_id=data.get("guild_id"),
            position=data.get("position", 0),
            parent_id=data.get("parent_id"),
            permission_overwrites=data.get("permission_overwrites", []),
            nsfw=data.get("nsfw", False),
            topic=data.get("topic"),
            _state=self.client,
        )

        # Cache the channel
        self._channel_cache.set(channel_id, channel)
        if self.config["track_stats"]:
            self.stats.updates += 1

        if channel.guild_id:
            guild = self.get_guild(channel.guild_id)
            if guild:
                guild.channels[channel.id] = channel

        return channel

    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Get channel from cache."""
        channel = self._channel_cache.get(channel_id)
        if channel:
            if self.config["track_stats"]:
                self.stats.hits += 1
            return channel

        if self.config["track_stats"]:
            self.stats.misses += 1
        return None

    def store_message(self, data: Dict[str, Any]) -> Message:
        """Store message in cache."""
        message_id = data["id"]

        # Check cache first
        cached_message = self._message_cache.get(message_id)
        if cached_message:
            if self.config["track_stats"]:
                self.stats.hits += 1
            return cached_message

        if self.config["track_stats"]:
            self.stats.misses += 1

        author_data = data.get("author")
        author = self.store_user(author_data) if author_data else None

        # Process attachments
        attachments = []
        for a_data in data.get("attachments", []):
            attachments.append(
                Attachment(
                    id=a_data["id"],
                    filename=a_data["filename"],
                    url=a_data["url"],
                    proxy_url=a_data["proxy_url"],
                    size=a_data["size"],
                    height=a_data.get("height"),
                    width=a_data.get("width"),
                    content_type=a_data.get("content_type"),
                    ephemeral=a_data.get("ephemeral", False),
                    _state=self.client,
                )
            )

        # Process embeds
        embeds = []
        for e_data in data.get("embeds", []):
            embeds.append(
                Embed(
                    title=e_data.get("title"),
                    type=e_data.get("type", "rich"),
                    description=e_data.get("description"),
                    url=e_data.get("url"),
                    timestamp=e_data.get("timestamp"),
                    color=e_data.get("color"),
                    footer=e_data.get("footer"),
                    image=e_data.get("image"),
                    thumbnail=e_data.get("thumbnail"),
                    video=e_data.get("video"),
                    provider=e_data.get("provider"),
                    author=e_data.get("author"),
                    fields=e_data.get("fields", []),
                )
            )

        message = Message(
            id=message_id,
            channel_id=data["channel_id"],
            guild_id=data.get("guild_id"),
            author=author,
            content=data.get("content", ""),
            timestamp=data["timestamp"],
            tts=data.get("tts", False),
            mention_everyone=data.get("mention_everyone", False),
            attachments=attachments,
            embeds=embeds,
            reactions=data.get("reactions", []),
            _state=self.client,
        )

        # Cache the message
        self._message_cache.set(message_id, message)
        self.messages.append(message)
        if self.config["track_stats"]:
            self.stats.updates += 1

        return message

    def get_message(self, message_id: str) -> Optional[Message]:
        """Get message from cache."""
        message = self._message_cache.get(message_id)
        if message:
            if self.config["track_stats"]:
                self.stats.hits += 1
            return message

        # Check message deque
        for msg in self.messages:
            if msg.id == message_id:
                if self.config["track_stats"]:
                    self.stats.hits += 1
                return msg

        if self.config["track_stats"]:
            self.stats.misses += 1
        return None

    def store_role(self, data: Dict[str, Any]) -> Role:
        """Store role in cache."""
        role_id = data["id"]

        # Check cache first
        cached_role = self._role_cache.get(role_id)
        if cached_role:
            if self.config["track_stats"]:
                self.stats.hits += 1
            return cached_role

        if self.config["track_stats"]:
            self.stats.misses += 1

        role = Role(
            id=role_id,
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
            _state=self.client,
        )

        # Cache the role
        self._role_cache.set(role_id, role)
        if self.config["track_stats"]:
            self.stats.updates += 1

        return role

    def get_role(self, role_id: str) -> Optional[Role]:
        """Get role from cache."""
        role = self._role_cache.get(role_id)
        if role:
            if self.config["track_stats"]:
                self.stats.hits += 1
            return role

        if self.config["track_stats"]:
            self.stats.misses += 1
        return None
