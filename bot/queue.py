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
from dataclasses import dataclass
from typing import Optional, List
from random import randrange, shuffle

import hikari

from yougan import Track, Player


class QueueTrack:
    def __init__(self, track: Track, requester: hikari.User):
        self.track = track
        self.requester = requester
        self._length = f"{self.track.length // 60000}m{self.track.length // 1000 % 60:0>2}s"

    @property
    def length(self) -> str:
        return self._length


class BotBotPlayer:
    def __init__(self, player: Player, channel: hikari.TextableChannel):
        self.tracks: List[QueueTrack] = []
        self.now_playing: Optional[QueueTrack] = None
        self._play_task: Optional[asyncio.Task] = None
        self._player = player
        self._channel = channel
        self._paused = False
        self._lock = asyncio.Lock()

    @property
    def paused(self):
        return self._paused

    async def shuffle(self):
        shuffle(self.tracks)

    async def pause(self):
        self._paused = True
        await self._player.pause()

    async def play(self):
        if self._paused:
            self._paused = False
            await self._player.resume()
        else:
            self._play_task = asyncio.create_task(self.play_loop())

    async def stop(self):
        self._play_task.cancel()

    async def add(self, track: QueueTrack):
        async with self._lock:
            self.tracks.append(track)

    async def skip(self):
        await self._player.stop()

    async def play_loop(self):
        while True:
            while True:
                if self.tracks:
                    break
                await asyncio.sleep(0.5)
            async with self._lock:
                self.now_playing = self.tracks.pop(0)
            await self._channel.send(
                hikari.Embed(
                    title="Playing song",
                    description=f"{self.now_playing.track.title[:100]}\n"
                                f"{self.now_playing.length}",
                    color=hikari.Color.from_int(0x4682b4)
                ).set_footer(
                    text=f"{self.now_playing.requester.username}#{self.now_playing.requester.discriminator}",
                    icon=self.now_playing.requester.avatar_url
                ).set_thumbnail(self.now_playing.track.thumbnail)
            )
            self._player.is_stopped = False
            await self._player.play(self.now_playing.track)
            await asyncio.sleep(0.5)
            while self._player.is_playing and not self._player.is_stopped:
                await asyncio.sleep(0.1)
