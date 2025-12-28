import asyncio
import inspect
import logging
from .client import Client
from .models import Message

log = logging.getLogger(__name__)

class Context:
    def __init__(self, message: Message, bot, args: list):
        self.message = message
        self.bot = bot
        self.args = args
        self.author = message.author
        self.channel_id = message.channel_id
        self.guild_id = getattr(message, 'guild_id', None) # Message model might need guild_id update
        self.content = message.content

    async def send(self, content):
        return await self.bot.send_message(self.channel_id, content)

    async def reply(self, content):
        # TODO: Implement actual reply with reference
        return await self.send(f"<@{self.author.id}> {content}")

class Command:
    def __init__(self, func, name=None):
        self.func = func
        self.name = name or func.__name__

    async def invoke(self, ctx):
        try:
            await self.func(ctx, *ctx.args)
        except Exception as e:
            log.error(f"Error invoking command {self.name}: {e}")

class Bot(Client):
    def __init__(self, command_prefix, loop=None):
        super().__init__(loop=loop)
        self.command_prefix = command_prefix
        self._commands = {}
        self.event(self.on_message_create)

    def command(self, name=None):
        def decorator(func):
            cmd = Command(func, name)
            self._commands[cmd.name] = cmd
            return cmd
        return decorator

    async def on_message_create(self, message: Message):
        if message.author.id == self.user.id:
            # Selfbots usually want to respond to themselves too, but let's be careful.
            # For now, let's allow it but maybe make it configurable.
            pass

        if message.content.startswith(self.command_prefix):
            content = message.content[len(self.command_prefix):]
            parts = content.split()
            if not parts:
                return
            
            command_name = parts[0]
            args = parts[1:]

            if command_name in self._commands:
                ctx = Context(message, self, args)
                await self._commands[command_name].invoke(ctx)
