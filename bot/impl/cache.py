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
import logging
from typing import List, Dict

import hikari

from bot.utils.misc import binary_search


class BotBotCacheImpl:
    def __init__(self, bot: hikari.GatewayBot, max_cache_size: int):
        self._bot = bot
        self._cache_locks: Dict[int, asyncio.Lock] = {}
        self._cache: Dict[int, List[hikari.Message]] = {}
        self._max_cache_size = max_cache_size
        self._logger = logging.getLogger(__name__)

    async def populate(self, guild_id: int, fetch_messages: bool = True):
        guild = await self._bot.rest.fetch_guild(guild_id)
        for snowflake, channel in guild.get_channels().items():
            if not isinstance(channel, hikari.TextableGuildChannel):
                continue
            self._logger.info(f"Caching channel {channel.name} ({channel.id})")
            self._cache[channel.id] = []
            self._cache_locks[channel.id] = asyncio.Lock()
            if not fetch_messages:
                continue
            async for message in channel.fetch_history():
                self._cache[channel.id].append(message)
                if len(self._cache[channel.id]) > self._max_cache_size:
                    break

    async def add_message(self, message: hikari.Message):
        async with self._cache_locks[message.channel_id]:
            self._cache[message.channel_id].append(message)
            if len(self._cache) > self._max_cache_size:
                self._cache[message.channel_id].pop(0)

    async def get_message(self, channel_id: int, message_id: int) -> hikari.Message:
        for message in self._cache[channel_id]:
            if message.id == message_id:
                return message
        raise ValueError
