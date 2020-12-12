import os
import sys
import traceback
from typing import List

import discord
import dotenv
import mcstatus
from discord.ext import commands

from checks import in_whitelist, InWhitelistCheckFailure
from rcon import minecraft

bot_bot = commands.Bot(command_prefix="$", help_command=None)
dotenv.load_dotenv()

IP = os.getenv("IP")
PORT = os.getenv("PORT")
SERVER_PORT = os.getenv("SERVER_PORT")
RCON = os.getenv("RCON")
server = minecraft.Server(IP, PORT, RCON, connect_on_send=True)
mod_commands = os.getenv("MOD_COMMANDS").split(",")


@bot_bot.event
async def on_ready():
    await server.connect()
    print("Bot Bot ready!")


@bot_bot.command()
async def send(ctx: commands.Context, *, command: str):
    if int(os.getenv("MOD")) not in [r.id for r in ctx.author.roles]:
        return
    for cmd in mod_commands:
        if command.startswith(f"{cmd} ") or command == cmd:
            return await ctx.send(f"```{(await server.send(command))[:1500]}```")
    if ctx.author.id not in [569362627935862784]:
        await ctx.send("Allowed commands for moderators: " + ", ".join(mod_commands))
    await ctx.send(f"```{(await server.send(command))[:1500]}```")


@bot_bot.command()
@in_whitelist(channels=[787396313380945941], roles=[787206476896403467], redirect=787396313380945941)
async def list(ctx: commands.Context):
    await send(ctx, command="list")


@in_whitelist(channels=[787396313380945941], roles=[787206476896403467], redirect=787396313380945941)
@bot_bot.command(name="server")
async def _server(ctx: commands.Context):
    svr = mcstatus.MinecraftServer.lookup(f'{IP}:{SERVER_PORT}')
    status = svr.status()
    e = discord.Embed()
    e.title = f'Modded 1.12.2 Server'
    e.description = flatten(status.description)
    e.add_field(name="Players", value=str(status.players.online) + "/" + str(status.players.max))
    e.add_field(name="Ping", value=str(status.latency))
    e.add_field(name="Version", value=status.version.name)
    e.add_field(name="Protocol", value="v" + str(status.version.protocol))
    await ctx.send(embed=e)


def flatten(mc_text):
    if isinstance(mc_text, str):
        return mc_text
    if isinstance(mc_text, List):
        return "".join(flatten(text for text in mc_text))
    if isinstance(mc_text, dict):
        if "text" not in mc_text:
            return ""
        return mc_text["text"]


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
