import logging
import os
from typing import Optional

import discord
import dotenv
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

dotenv.load_dotenv()

import ptero  # noqa e402

bot_bot = commands.Bot(command_prefix="$", help_command=None)
slash = SlashCommand(bot_bot, sync_commands=True)
logging.basicConfig(level=logging.INFO)
GUILD: Optional[discord.Guild] = None
GUILD_ID: int = 786473829190860800
API_URL = "http://discord.com/api/v8"
ptero_client = ptero.PteroClient(os.getenv("PTERO"), "https://panel.rawr-x3.me")


@bot_bot.event
async def on_ready():
    global GUILD
    print("Bot Bot ready!")
    GUILD = bot_bot.get_guild(GUILD_ID)


@slash.slash(guild_ids=[GUILD_ID], name="server-status")
async def server_status(ctx: SlashContext):
    await ctx.defer()
    await ctx.send(
        "\n".join(map(str, await ptero_client.get_all_server_details()))
    )


bot_bot.run(os.getenv("TOKEN"))
