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
import asyncio
from datetime import datetime, timezone
from typing import Optional

import hikari

from bot.utils import ModLogValues


class ModLogImpl:
    def __init__(self, bot: hikari.GatewayBot):
        self._bot = bot
        self._channel_id = 889422360925601833
        self._mod_log_channel: Optional[hikari.TextableGuildChannel] = None
        asyncio.get_event_loop().create_task(self.__deferred_init())

    async def __deferred_init(self):
        while not self._bot.is_alive:
            await asyncio.sleep(0.1)
        self._mod_log_channel = await self._bot.rest.fetch_channel(self._channel_id)

    # noinspection PyMethodMayBeStatic
    def create_embed(self, typ: int, description: Optional[str] = None) -> hikari.Embed:
        return hikari.Embed(title=ModLogValues.get_title(typ),
                            color=ModLogValues.get_color(typ),
                            description=description,
                            timestamp=datetime.now(tz=timezone.utc))

    async def send(self, embed: hikari.Embed, *, schedule: bool = False):
        coro = self._bot.rest.create_message(channel=self._channel_id, embed=embed)
        if schedule:
            asyncio.get_event_loop().create_task(coro)
        else:
            await coro
