# aiko_api/core/headers.py
import base64
import json
import uuid
import sys
from typing import Optional
from ..utils import get_super_properties, get_user_agent

class HeaderBuilder:
    def __init__(self, token: Optional[str] = None, bot: bool = False):
        self.token = token
        self.bot = bot
        self.user_agent = get_user_agent()
        self.super_properties = get_super_properties()

    def build(self, context: Optional[str] = None) -> dict:
        headers = {
            "Content-Type": "application/json",
        }
        
        if not self.bot:
            headers["User-Agent"] = self.user_agent
            headers["X-Super-Properties"] = self.super_properties
        else:
            headers["User-Agent"] = "DiscordBot (https://github.com/kaity/aiko_api, 1.0.0)"

        if self.token:
            token = self.token
            if self.bot and not token.startswith("Bot "):
                token = f"Bot {token}"
            headers["Authorization"] = token

        if context and not self.bot:
            # Discord often uses x-context-properties for tracking origin of actions
            payload = base64.b64encode(json.dumps({"location": context}).encode()).decode()
            headers["X-Context-Properties"] = payload
        return headers
