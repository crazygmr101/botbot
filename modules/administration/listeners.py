"""
Copyright 2021 crazygmr101

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated 
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the 
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit 
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the 
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import re

import hikari
import tanjun

from bot.protos.cache import BotBotCacheProto
from bot.protos.modlog import ModLogProto
from bot.utils import ModLogValues
from bot.utils.misc import Null

DISCORD_INVITE = re.compile(r"(https?://)?(www\.|canary\.|ptb\.)?discord(\.gg|(app)?\.com/invite|\.me)/([^ ]{4,10})/?")

component = tanjun.Component()


@component.with_listener(hikari.MessageCreateEvent)
async def invite_filter(event: hikari.MessageCreateEvent):
    try:
        if re.findall(DISCORD_INVITE, event.message.content):
            await event.message.delete()
    except TypeError:
        pass


@component.with_listener(hikari.StoppingEvent)
async def log_stopping(event: hikari.StoppingEvent, modlog: ModLogProto = tanjun.injected(type=ModLogProto)):
    await modlog.send(modlog.create_embed(ModLogValues.stopping))


@component.with_listener(hikari.MessageDeleteEvent)
async def log_message_deletion(event: hikari.MessageDeleteEvent,
                               modlog: ModLogProto = tanjun.injected(type=ModLogProto),
                               cache: BotBotCacheProto = tanjun.injected(type=BotBotCacheProto)):
    try:
        original_message = await cache.get_message(event.channel_id, event.message_id)
    except ValueError:
        return
    await modlog.send(
        modlog.create_embed(ModLogValues.message_deleted).add_field(
            "Message", (original_message.content[:600] if original_message.content else "-"), inline=False
        ).add_field(
            "Author", f"{original_message.author.username}#{original_message.author.discriminator} "
                      f"({original_message.author.id})", inline=True
        ).add_field(
            "Sent at", f"<t:{int(original_message.created_at.timestamp())}>", inline=True
        ).add_field(
            "Sent in", f"<#{original_message.channel_id}>"
        )
    )


@component.with_listener(hikari.MessageUpdateEvent)
async def log_message_edit(event: hikari.MessageUpdateEvent,
                           modlog: ModLogProto = tanjun.injected(type=ModLogProto),
                           cache: BotBotCacheProto = tanjun.injected(type=BotBotCacheProto)):
    if event.message.author.is_bot:
        return
    try:
        original_message = await cache.get_message(event.channel_id, event.message_id)
    except ValueError:
        return
    current_message = event.message
    await modlog.send(
        modlog.create_embed(
            ModLogValues.message_edited,
            description=f"[Jump to message](https://discord.com/channels/"
                        f"{original_message.guild_id}/{original_message.channel_id}/{original_message.id})"
        ).add_field(
            "Old Content", original_message.content[:300], inline=False
        ).add_field(
            "New Content", current_message.content[:300], inline=False
        ).add_field(
            "Author", f"{original_message.author.username}#{original_message.author.discriminator} "
                      f"({original_message.author.id})", inline=True
        ).add_field(
            "Sent at", f"<t:{int(original_message.created_at.timestamp())}>", inline=True
        ).add_field(
            "Sent in", f"<#{original_message.channel_id}>"
        )
    )


@component.with_listener(hikari.VoiceStateUpdateEvent)
async def log_voice_change(event: hikari.VoiceStateUpdateEvent,
                           modlog: ModLogProto = tanjun.injected(type=ModLogProto)):
    if Null.safe(event.old_state).channel_id == event.state.channel_id:
        # user just deafened, muted, etc - not logging those
        return
    event.app.cache
    member = event.old_state.member if event.old_state else event.state.member
    old_channel = await event.app.rest.fetch_channel(event.old_state.channel_id) if \
        (event.old_state and event.old_state.channel_id) else None
    channel = await event.app.rest.fetch_channel(event.state.channel_id) if event.state.channel_id else None
    if not old_channel:  # joining voice
        description = f"Joined {channel.name}"
    elif not channel:
        description = f"Left {old_channel.name}"
    else:
        description = f"Moved from {old_channel.name} to {channel.name}"
    await modlog.send(modlog.create_embed(ModLogValues.voice_change).add_field(
        "Member", f"{member.username}#{member.discriminator} ({member.id})"
    ).add_field(
        "Change", description
    ))


@component.with_listener(hikari.MessageCreateEvent)
async def add_message_to_cache(event: hikari.MessageCreateEvent,
                               cache: BotBotCacheProto = tanjun.injected(type=BotBotCacheProto)):
    await cache.add_message(event.message)


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    # This loads the component, and is necessary in EVERY module,
    # otherwise you'll get an error.
    client.add_component(component.copy())
