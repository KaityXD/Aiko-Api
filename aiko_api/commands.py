import asyncio
import inspect
import shlex
import os
import importlib.util
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Union, Dict
from .katlog import get_logger
from .client import Client
from .common.models import Message, User

log = get_logger("aiko_api", level="DEBUG")


class Context:
    def __init__(
        self,
        message: Message,
        bot,
        args: list,
        prefix: str,
        invoked_with: str,
        kwargs: dict = None,
    ):
        self.message = message
        self.bot = bot
        self.args = args
        self.prefix = prefix
        self.invoked_with = invoked_with
        self.kwargs = kwargs or {}
        self.author = message.author
        self.channel_id = message.channel_id
        self.guild_id = getattr(message, "guild_id", None)
        self.content = message.content

    async def send(self, content, **kwargs):
        return await self.bot.send_message(self.channel_id, content, **kwargs)

    async def send_image(self, url_or_path, content="", **kwargs):
        return await self.bot.send_image(
            self.channel_id, url_or_path, content, **kwargs
        )

    def send_bg(self, content, **kwargs):
        return self.bot.send_message_bg(self.channel_id, content, **kwargs)

    async def reply(self, content, **kwargs):
        return await self.message.reply(content, **kwargs)

    def reply_bg(self, content, **kwargs):
        return self.message.reply_bg(content, **kwargs)

    async def react(self, emoji):
        await self.message.react(emoji)


class Command:
    def __init__(self, func: Callable, name: str = None, cog=None, parent=None):
        self.func = func
        self.name = name or func.__name__
        self.cog = cog
        self.parent = parent
        self.subcommands: Dict[str, Command] = {}
        self._is_command = True

        # Check if func is already a Command (from @command())
        if hasattr(func, "subcommands"):
            self.subcommands.update(func.subcommands)
            self.func = func.func

        self.params = inspect.signature(self.func).parameters

    def __call__(self, *args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return self.add_command(args[0])
        return self.func(*args, **kwargs)

    def add_command(self, func_or_cmd, name: str = None):
        if isinstance(func_or_cmd, Command):
            cmd = func_or_cmd
            cmd.parent = self
            if self.cog:
                cmd.cog = self.cog
        else:
            cmd = Command(func_or_cmd, name=name, parent=self, cog=self.cog)

        self.subcommands[cmd.name] = cmd
        return cmd

    async def invoke(self, ctx: Context):
        try:
            # Check for subcommands first
            if ctx.args:
                sub_name = ctx.args[0]
                if sub_name in self.subcommands:
                    sub_ctx = Context(
                        ctx.message,
                        ctx.bot,
                        ctx.args[1:],
                        ctx.prefix,
                        f"{ctx.invoked_with} {sub_name}",
                    )
                    return await self.subcommands[sub_name].invoke(sub_ctx)

            args, kwargs = await self._parse_arguments(ctx)

            # Smart Signature logic
            params = list(self.params.values())
            args_to_pass = []

            if params and params[0].name == "self":
                if self.cog:
                    args_to_pass.append(self.cog)
                params = params[1:]  # Consume self

            if params and params[0].name in ("ctx", "message", "data"):
                args_to_pass.append(ctx)

            await self.func(*args_to_pass, *args, **kwargs)
        except Exception as e:
            log.error(f"Error invoking command {self.name}: {e}")
            await ctx.send(f"Error: {e}")

    async def _parse_arguments(self, ctx: Context) -> tuple[List[Any], dict[str, Any]]:
        iterator = iter(ctx.args)
        converted_args = []
        converted_kwargs = {}

        # Skip 'ctx' and 'self' parameters in signature parsing
        params = list(self.params.items())
        if params and params[0][0] == "self":
            params = params[1:]
        if params and params[0][0] in ("ctx", "message", "data"):
            params = params[1:]

        for name, param in params:
            if param.kind == param.KEYWORD_ONLY:
                rest = " ".join(list(iterator))
                if not rest and param.default == param.empty:
                    raise ValueError(f"Missing required argument: {name}")
                elif not rest:
                    converted_kwargs[name] = param.default
                else:
                    converted_kwargs[name] = rest
                break

            try:
                arg = next(iterator)
            except StopIteration:
                if param.default != param.empty:
                    converted_args.append(param.default)
                    continue
                raise ValueError(f"Missing required argument: {name}")

            if param.annotation != param.empty:
                try:
                    arg = await self._convert(ctx, arg, param.annotation)
                except Exception as e:
                    raise ValueError(f"Failed to convert argument '{name}': {e}")

            converted_args.append(arg)

        return converted_args, converted_kwargs

    async def _convert(self, ctx, arg, annotation):
        if annotation is int:
            return int(arg)
        elif annotation is float:
            return float(arg)
        elif annotation is bool:
            return arg.lower() in ("yes", "y", "true", "t", "1", "enable", "on")
        elif annotation is User:
            # Handle mentions: <@123> or <@!123>
            user_id = arg
            if arg.startswith("<@") and arg.endswith(">"):
                user_id = arg.replace("<@", "").replace("!", "").replace(">", "")

            user = ctx.bot.cache.get_user(user_id)
            if user:
                return user

            # If not in cache, try to fetch from API (though we don't have a direct get_user API method yet,
            # we can fallback to raw dict if we had one, but for now let's just return what we can)
            # For now, just return a dummy User with the ID if we can't find it?
            # Or raise error. Let's raise error if not found.
            raise ValueError(f"User '{user_id}' not found in cache.")
        return arg


def command(name: str = None):
    def decorator(func):
        if isinstance(func, Command):
            if name:
                func.name = name
            return func
        return Command(func, name=name)

    return decorator


def cog_event(func):
    func._is_cog_event = True
    return func


class Cog:
    def __init__(self, bot):
        self.bot = bot

    def get_commands(self) -> List[Command]:
        cmds = []
        for name, member in inspect.getmembers(self):
            if hasattr(member, "_is_command") and not getattr(member, "parent", None):
                if isinstance(member, Command):
                    member.cog = self
                    # Update all subcommands recursively
                    self._update_subcommand_cogs(member)
                    cmds.append(member)
                else:
                    cmds.append(
                        Command(
                            member, getattr(member, "_command_name", None), cog=self
                        )
                    )
        return cmds

    def _update_subcommand_cogs(self, cmd: Command):
        for sub in cmd.subcommands.values():
            sub.cog = self
            self._update_subcommand_cogs(sub)

    @staticmethod
    def event(func):
        func._is_cog_event = True
        return func


@dataclass
class _PluginRecord:
    file_path: str
    module_name: str
    cogs_added: List[str] = field(default_factory=list)
    cogs_replaced: Dict[str, "Cog"] = field(default_factory=dict)
    commands_added: List[str] = field(default_factory=list)
    commands_overwritten: Dict[str, "Command"] = field(default_factory=dict)


# For @cog.event syntax as per spec
class _CogDecorator:
    @staticmethod
    def event(func):
        func._is_cog_event = True
        return func


cog = _CogDecorator()


class Bot(Client):
    def __init__(self, command_prefix, loop=None, proxy=None, bot=False, intents=None):
        super().__init__(loop=loop, proxy=proxy, bot=bot, intents=intents)
        self.command_prefix = command_prefix
        self._commands: Dict[str, Command] = {}
        self._cogs: Dict[str, Cog] = {}
        self._plugin_mtimes: Dict[str, float] = {}
        self._plugins: Dict[str, "_PluginRecord"] = {}
        self._cog_event_wrappers: Dict[str, List[tuple[str, Callable]]] = {}
        self.event(self.on_message_create)

    def _normalize_plugin_path(self, file_path: str) -> str:
        return os.path.abspath(file_path)

    def command(self, name=None):
        def decorator(func):
            if isinstance(func, Command):
                cmd = func
                if name:
                    cmd.name = name
            else:
                cmd = Command(func, name)
            self._commands[cmd.name] = cmd
            return cmd

        return decorator

    def cmd(self, name=None):
        """Alias for command."""
        return self.command(name)

    def add_cog(self, cog: Cog):
        self._cogs[cog.__class__.__name__] = cog
        for cmd in cog.get_commands():
            if cmd.name in self._commands:
                log.warn(
                    f"Command '{cmd.name}' from Cog '{cog.__class__.__name__}' is overriding an existing command."
                )
            self._commands[cmd.name] = cmd
            log.debug(
                f"Registered command: {cmd.name} (from Cog: {cog.__class__.__name__})"
            )

        # Register events
        for name, member in inspect.getmembers(cog):
            # Check for name or _is_cog_event attribute
            if name.startswith("on_") or hasattr(member, "_is_cog_event"):
                if asyncio.iscoroutinefunction(member):
                    wrapper = self._wrap_cog_event(cog, member)
                    event_key = wrapper.__name__
                    if event_key == "on_message":
                        event_key = "on_message_create"
                    self.event(wrapper)
                    self._cog_event_wrappers.setdefault(
                        cog.__class__.__name__, []
                    ).append((event_key, wrapper))
                    log.debug(
                        f"Registered event: {name} (from Cog: {cog.__class__.__name__})"
                    )

        log.info(f"Loaded Cog: {cog.__class__.__name__}")

    def _wrap_cog_event(self, cog, member):
        async def wrapper(*args, **kwargs):
            sig = inspect.signature(member)
            params = list(sig.parameters.values())

            args_to_pass = []
            if params and params[0].name == "self":
                args_to_pass.append(cog)

            # Use original args from dispatcher
            return await member(*args_to_pass, *args, **kwargs)

        wrapper.__name__ = member.__name__
        return wrapper

    def remove_cog(self, name: str):
        if name in self._cogs:
            cog = self._cogs.pop(name)
            cmd_names = [cmd.name for cmd in cog.get_commands()]
            for cmd_name in cmd_names:
                self._commands.pop(cmd_name, None)

            # Unregister events for this cog
            for event_key, wrapper in self._cog_event_wrappers.pop(name, []):
                handlers = self._events.get(event_key)
                if not handlers:
                    continue
                try:
                    handlers.remove(wrapper)
                except ValueError:
                    pass

            log.info(f"Unloaded Cog: {name}")
            return cog
        return None

    def load_plugin(self, file_path: str):
        """Loads a plugin from a file path."""
        try:
            file_path = self._normalize_plugin_path(file_path)

            # If already loaded, treat as reload.
            if file_path in self._plugins:
                self.unload_plugin(file_path)

            before_commands = dict(self._commands)
            before_cogs = dict(self._cogs)

            base = os.path.splitext(os.path.basename(file_path))[0]
            module_name = f"plugin_{base}_{abs(hash(file_path))}"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            record = _PluginRecord(file_path=file_path, module_name=module_name)

            # Look for Cog classes and standalone commands
            loaded = False
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Cog) and obj is not Cog:
                    # If a cog with the same name already exists, replace it but keep the old one for restore.
                    cog_name = obj.__name__
                    if cog_name in self._cogs:
                        old = self.remove_cog(cog_name)
                        if old is not None:
                            record.cogs_replaced[cog_name] = old
                    self.add_cog(obj(self))
                    loaded = True
                elif hasattr(obj, "_is_command") and not getattr(obj, "parent", None):
                    if isinstance(obj, Command):
                        if (
                            obj.name in self._commands
                            and obj.name not in record.commands_overwritten
                        ):
                            record.commands_overwritten[obj.name] = self._commands[
                                obj.name
                            ]
                        self._commands[obj.name] = obj
                    else:
                        cmd = Command(obj, getattr(obj, "_command_name", None))
                        if (
                            cmd.name in self._commands
                            and cmd.name not in record.commands_overwritten
                        ):
                            record.commands_overwritten[cmd.name] = self._commands[
                                cmd.name
                            ]
                        self._commands[cmd.name] = cmd
                    loaded = True

            if loaded:
                # Track what this plugin introduced.
                after_commands = self._commands
                after_cogs = self._cogs

                record.commands_added = [
                    n for n in after_commands.keys() if n not in before_commands
                ]
                record.cogs_added = [
                    n for n in after_cogs.keys() if n not in before_cogs
                ]

                self._plugins[file_path] = record
                self._plugin_mtimes[file_path] = os.path.getmtime(file_path)
                return True
            else:
                log.warn(f"No Cogs or standalone commands found in plugin {file_path}")
        except Exception as e:
            log.error(f"Failed to load plugin {file_path}: {e}")
        return False

    def unload_plugin(self, file_path: str) -> bool:
        file_path = self._normalize_plugin_path(file_path)
        record = self._plugins.get(file_path)
        if not record:
            return False

        # Remove cogs this plugin added.
        for cog_name in list(record.cogs_added):
            self.remove_cog(cog_name)

        # Remove standalone commands this plugin added.
        for cmd_name in list(record.commands_added):
            self._commands.pop(cmd_name, None)

        # Restore overwritten commands.
        for cmd_name, old_cmd in record.commands_overwritten.items():
            self._commands[cmd_name] = old_cmd

        # Restore any cogs that were replaced.
        for cog_name, old_cog in record.cogs_replaced.items():
            self.add_cog(old_cog)

        self._plugins.pop(file_path, None)
        self._plugin_mtimes.pop(file_path, None)
        return True

    def reload_plugin(self, file_path: str) -> bool:
        file_path = self._normalize_plugin_path(file_path)
        self.unload_plugin(file_path)
        return self.load_plugin(file_path)

    def load_plugins(self, directory: str):
        """Automatically loads all plugins in a directory."""
        if not os.path.exists(directory):
            os.makedirs(directory)
            return

        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("_"):
                self.load_plugin(os.path.join(directory, filename))

    async def watch_plugins(self, directory: str):
        """Background task to hot-reload plugins."""
        log.info(f"Watching directory '{directory}' for changes...")
        while not self._stop_event.is_set():
            await asyncio.sleep(2)  # Check every 2 seconds
            for filename in os.listdir(directory):
                if filename.endswith(".py") and not filename.startswith("_"):
                    path = self._normalize_plugin_path(
                        os.path.join(directory, filename)
                    )
                    mtime = os.path.getmtime(path)

                    if (
                        path not in self._plugin_mtimes
                        or mtime > self._plugin_mtimes[path]
                    ):
                        log.info(f"Reloading plugin: {filename}")
                        self.load_plugin(path)

    async def on_message_create(self, message: Message):
        if not self.user:
            return

        if message.author.id == self.user.id:
            pass  # Allow selfbot commands

        if message.content.startswith(self.command_prefix):
            content = message.content[len(self.command_prefix) :]
            try:
                parts = shlex.split(content)
            except ValueError:
                parts = content.split()

            if not parts:
                return

            command_name = parts[0]
            args = parts[1:]

            if command_name in self._commands:
                log.debug(
                    f"Command found: {command_name} from {message.author.username}"
                )
                ctx = Context(message, self, args, self.command_prefix, command_name)
                asyncio.create_task(self._commands[command_name].invoke(ctx))
            else:
                log.debug(f"Command not found: '{command_name}'")
