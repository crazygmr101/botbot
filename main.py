import logging
import os
from pathlib import Path
from typing import Optional

import dotenv
import hikari
import tanjun

dotenv.load_dotenv()

import ptero  # noqa e402

bot_bot = hikari.BotApp(os.getenv("TOKEN"))  # noqa

logging.basicConfig(level=logging.INFO)
GUILD: Optional[hikari.Guild] = None
GUILD_ID: int = 786473829190860800
API_URL = "http://discord.com/api/v8"

client = tanjun.Client.from_gateway_bot(bot_bot, set_global_commands=GUILD_ID)
client.load_modules(*Path("./modules").glob("*.py"))

bot_bot.run()
