import logging
import os
import sys
from pathlib import Path

import dotenv

from bot.impl import DatabaseImpl
from bot.logging import LoggingHandler
from bot.protos import DatabaseProto

logging.basicConfig(level=logging.INFO)
logging.setLoggerClass(LoggingHandler)

# have to import these after logging is configured, cuz for some fucking
# reason, if i don't, it sets up its own logging *when imported* :SCWEEEE:
import hikari  # noqa E402
import tanjun  # noqa E402
from bot.bot import BotBot  # noqa E402

sys.path.append(os.path.abspath("external/hikari-yougan/"))

dotenv.load_dotenv()
import ptero  # noqa e402

bot_bot = BotBot(os.getenv("TOKEN"),
                 intents=hikari.Intents.GUILD_MESSAGES | hikari.Intents.GUILD_INTEGRATIONS)  # noqa


@bot_bot.listen(hikari.StartedEvent)
async def ready(event: hikari.StartedEvent):
    await bot_bot.lavalink_client.start_nodes()


GUILD_ID: int = 786473829190860800

(
    tanjun.Client
        .from_gateway_bot(bot_bot, set_global_commands=GUILD_ID)
        .set_type_dependency(DatabaseProto, tanjun.cache_callback(DatabaseImpl.connect))
        .add_prefix("!")
        .load_modules(*Path("./modules").glob("*.py"))
)

bot_bot.run()
