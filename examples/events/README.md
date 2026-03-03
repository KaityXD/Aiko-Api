# aiko_api Events

This folder contains examples of how to handle events dispatched from Discord's Gateway.

## Supported Events

Events in `aiko_api` are handled by decorating a coroutine function with `@client.event`.

### Core Events (Mapped to Models)
The following events are explicitly mapped to model objects:

- `on_ready(user)`: Called when the client is logged in and ready. Receives a `User` object.
- `on_message_create(message)`: Called when a message is sent. Receives a `Message` object.
- `on_guild_create(guild)`: Called when the client joins a guild or during initial guild load. Receives a `Guild` object.

### Generic Events (Raw Data)
The library also supports listening to any other Discord event using its lowercase equivalent. For these events, the callback will receive the **raw payload dictionary** as sent by Discord.

- `on_resumed(data)`: Called when a lost session is resumed.
- `on_message_update(data)`: Called when a message is edited.
- `on_message_delete(data)`: Called when a message is deleted.
- `on_voice_state_update(data)`: Called when someone joins/leaves a voice channel.
- `on_presence_update(data)`: Called when someone's status or activity changes.
- ...and many others.

## Event Dispatch Logic
`aiko_api` uses a flexible dispatching system:
1. It looks for an explicit mapping (like `READY -> on_ready`).
2. If no mapping exists, it constructs the name as `on_` + `lowercase_event_name`.
3. If a matching function exists in your code, it is invoked with the event data.

## Example
```python
@client.event
async def on_presence_update(data):
    # This will catch any presence update event
    user = data.get('user', {})
    print(f"User {user.get('id')} updated their status to {data.get('status')}")
```
