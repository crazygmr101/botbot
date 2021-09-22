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
from typing import Optional

import hikari
import tanjun

from bot.checks import author_in_same_voice_channel, author_in_voice_channel
from bot.queue import BotBotPlayer, QueueTrack
from yougan import Client, SearchResult, Track

component = tanjun.Component()

group = component.with_slash_command(tanjun.slash_command_group("music", "music commands"))
queue: Optional[BotBotPlayer] = None


@group.with_command
@tanjun.with_check(author_in_voice_channel)
@tanjun.as_slash_command("join", "Join your voice channel")
async def join(ctx: tanjun.SlashContext):
    global queue
    # noinspection PyUnresolvedReferences
    client: Client = ctx.shards.lavalink_client
    await client.connect(ctx.guild_id, ctx.get_guild().get_voice_state(ctx.author).channel_id, deaf=True)
    # noinspection PyTypeChecker
    queue = BotBotPlayer(client.get_player(ctx.guild_id), ctx.get_channel(), ctx.client)
    await queue.play()
    await ctx.respond("Connected to your voice channel")


@group.with_command
@tanjun.with_check(author_in_same_voice_channel)
@tanjun.as_slash_command("leave", "Leave the voice channel")
async def leave(ctx: tanjun.SlashContext):
    global queue
    if queue:
        # noinspection PyUnresolvedReferences
        await queue.stop()
        queue = None
    await ctx.shards.voice.disconnect(ctx.guild_id)
    await ctx.respond("Disconnected from your voice channel")


@group.with_command
@tanjun.with_check(author_in_same_voice_channel)
@tanjun.as_slash_command("skip", "Skips the song")
async def skip(ctx: tanjun.SlashContext):
    await queue.skip()
    await ctx.respond("Skipped")


@group.with_command
@tanjun.with_check(author_in_same_voice_channel)
@tanjun.as_slash_command("shuffle", "Shuffles the play queue")
async def shuffle(ctx: tanjun.SlashContext):
    await queue.shuffle()
    await ctx.respond("Shuffled")


@group.with_command
@tanjun.with_check(author_in_same_voice_channel)
@tanjun.with_int_slash_option(
    "level", "Volume to set to",
    choices=[(str(x // 10), x) for x in range(10, 101, 10)]
)
@tanjun.as_slash_command("volume", "Set the player volume")
async def volume(ctx: tanjun.SlashContext, level: int):
    await queue.set_volume(level)
    await ctx.respond(f"Set volume to {level}/10")


@group.with_command
@tanjun.with_check(author_in_same_voice_channel)
@tanjun.as_slash_command("queue", "Shows the current queue")
async def queue(ctx: tanjun.SlashContext):
    await ctx.respond(
        hikari.Embed(
            title="Play queue",
            description=f"Now Playing:"
                        f"```{queue.now_playing.track.title[:30] :<30} {queue.now_playing.length: >5}```\n" +
                        (("Up Next:\n"
                          "```" +
                          "\n".join(
                              f"{track.track.title[:30] :<30} {track.length: >5}" for track in queue.tracks[:10]) +
                          "```") if queue.tracks else "")
        )
    )


@group.with_command
@tanjun.with_check(author_in_same_voice_channel)
@tanjun.with_str_slash_option("song", "URL of the song to play")
@tanjun.as_slash_command("play", "Play a song")
async def play(ctx: tanjun.SlashContext, song: str):
    # noinspection PyUnresolvedReferences
    client: Client = ctx.shards.lavalink_client
    result: SearchResult = await client.search_track(query=song, yt=True)
    first: Track = [t for t in result.tracks][0]
    await queue.add(QueueTrack(first, ctx.author))
    await ctx.respond(
        hikari.Embed(
            title="Added song",
            description=f"{first.title[:100]}\n{first.length // 60000}m{first.length // 1000 % 60:>0}s",
            color=hikari.Color.from_int(0x191970)
        ).set_footer(
            text=f"{queue.volume // 10} | {ctx.author.username}#{ctx.author.discriminator}",
            icon=ctx.author.avatar_url
        ).set_thumbnail(first.thumbnail)
    )


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    # This loads the component, and is necessary in EVERY module,
    # otherwise you'll get an error.
    client.add_component(component.copy())
