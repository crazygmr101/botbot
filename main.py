import logging
import os
import sys
from pathlib import Path

import dotenv
import hikari
import tanjun

sys.path.append(os.path.abspath("external/hikari-yougan/"))

from bot.bot import BotBot  # noqa E402

logging.basicConfig(level=logging.INFO)
dotenv.load_dotenv()

import ptero  # noqa e402

bot_bot = BotBot(os.getenv("TOKEN"))  # noqa


@bot_bot.listen(hikari.StartedEvent)
async def ready(event: hikari.StartedEvent):
    await bot_bot.lavalink_client.start_nodes()


GUILD_ID: int = 786473829190860800

client = tanjun.Client.from_gateway_bot(bot_bot, set_global_commands=GUILD_ID).add_prefix("!")
client.load_modules(*Path("./modules").glob("*.py"))

bot_bot.run()
