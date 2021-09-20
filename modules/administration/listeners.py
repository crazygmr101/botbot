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
from datetime import datetime

import hikari
import humanize
import tanjun

from bot.protos.modlog import ModLogProto
from bot.utils import ModLogValues

DISCORD_INVITE = re.compile(r"(https?://)?(www\.|canary\.|ptb\.)?discord(\.gg|(app)?\.com/invite|\.me)/([^ ]{4,10})/?")

component = tanjun.Component()


@component.with_listener(hikari.MessageCreateEvent)
async def invite_filter(event: hikari.MessageCreateEvent):
    try:
        if re.findall(DISCORD_INVITE, event.message.content):
            await event.message.delete()
    except TypeError:
        pass


startup = datetime.now()


@component.with_listener(hikari.StartedEvent)
async def log_startup(event: hikari.StartedEvent, modlog: ModLogProto = tanjun.injected(type=ModLogProto)):
    await modlog.send(modlog.create_embed(ModLogValues.started,
                                          description=f"Startup completed in "
                                                      f"{humanize.naturaldelta(datetime.now() - startup)}"))


@component.with_listener(hikari.StoppingEvent)
async def log_stopping(event: hikari.StoppingEvent, modlog: ModLogProto = tanjun.injected(type=ModLogProto)):
    await modlog.send(modlog.create_embed(ModLogValues.stopping))


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    # This loads the component, and is necessary in EVERY module,
    # otherwise you'll get an error.
    client.add_component(component.copy())
