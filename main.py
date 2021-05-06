import io
import logging
import os
import random
import sys
import traceback
from typing import List, Optional

import aiohttp
import discord
import dotenv
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

from checks import InWhitelistCheckFailure

bot_bot = commands.Bot(command_prefix="$", help_command=None)
dotenv.load_dotenv()
slash = SlashCommand(bot_bot, sync_commands=True)
logging.basicConfig(level=logging.INFO)
mod_commands = os.getenv("MOD_COMMANDS").split(",")
GUILD: Optional[discord.Guild] = None
GUILD_ID: int = 786473829190860800
API_URL = "http://discord.com/api/v8"


@bot_bot.event
async def on_ready():
    global GUILD
    print("Bot Bot ready!")
    GUILD = bot_bot.get_guild(GUILD_ID)


@slash.slash(guild_ids=[GUILD_ID])
async def bonk(ctx: SlashContext):
    await ctx.send(content="Bonk!", hidden=True)


@slash.slash(guild_ids=[GUILD_ID])
async def hug(ctx: SlashContext, user: discord.User):
    hugs = [
        "{author} hugged {user}!",
        "{user} got a hug from {author} :)"
    ]
    async with aiohttp.ClientSession() as sess:
        async with sess.get("https://nekos.life/api/v2/img/hug") as resp:
            buf = io.BytesIO()
            url = (await resp.json())["url"]
            async with sess.get(url) as image:
                buf.write(await image.read())
                buf.seek(0)
            await ctx.send(
                content=random.choice(hugs)
                    .format(user=user.mention, author=ctx.author.mention),  # noqa
                file=discord.File(buf, filename=url.split("/")[-1])
            )

@slash.slash(guild_ids=[GUILD_ID])
async def slap(ctx: SlashContext, user: discord.User):
    slaps = [
        "{author} slapped {user}!",
        "{user} got slapped by {author}..ow"
    ]
    async with aiohttp.ClientSession() as sess:
        async with sess.get("https://nekos.life/api/v2/img/slap") as resp:
            buf = io.BytesIO()
            url = (await resp.json())["url"]
            async with sess.get(url) as image:
                buf.write(await image.read())
                buf.seek(0)
            await ctx.send(
                content=random.choice(slaps)
                    .format(user=user.mention, author=ctx.author.mention),  # noqa
                file=discord.File(buf, filename=url.split("/")[-1])
            )


@slash.slash(guild_ids=[GUILD_ID])
async def cat(ctx: SlashContext):
    async with aiohttp.ClientSession() as sess:
        async with sess.get("https://nekos.life/api/v2/img/meow") as resp:
            buf = io.BytesIO()
            url = (await resp.json())["url"]
            async with sess.get(url) as image:
                buf.write(await image.read())
                buf.seek(0)
            async with sess.get("https://nekos.life/api/v2/cat") as cat:
                cat_str = (await cat.json())["cat"]
            await ctx.send(
                content=cat_str,
                file=discord.File(buf, filename=url.split("/")[-1])
            )


@bot_bot.event
async def on_command_error(ctx: commands.Context, error):
    """The event triggered when an error is raised while invoking a command.
    ctx   : Context
    error : Exception"""

    # This prevents any commands with local handlers being handled here in on_command_error.
    if hasattr(ctx.command, 'on_error'):
        return

    ignored = (commands.CommandNotFound,)

    # Allows us to check for original exceptions raised and sent to CommandInvokeError.
    # If nothing is found. We keep the exception passed to on_command_error.
    error = getattr(error, 'original', error)

    # Anything in ignored will return and prevent anything happening.
    if isinstance(error, ignored):
        pass
    elif isinstance(error, commands.DisabledCommand):
        return await ctx.send(f'{ctx.command} has been disabled.')

    elif isinstance(error, commands.MissingAnyRole):
        missing_roles: List[discord.Role] = [ctx.guild.get_role(i) for i in error.missing_roles[0]]
        return await ctx.send("You must be one of the folowing roles to run that command: " +
                              ", ".join([f"**{r.name}**" for r in missing_roles]))

    elif isinstance(error, InWhitelistCheckFailure):
        await ctx.send(str(error))

    # All other Errors not returned come here... And we can just print the default TraceBack.
    print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


bot_bot.run(os.getenv("TOKEN"))
