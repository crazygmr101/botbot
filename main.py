import logging
import os
import sys
from pathlib import Path

import dotenv

from bot.impl.database import DatabaseImpl
from bot.impl.modlog import ModLogImpl
from bot.protos.database import DatabaseProto
from bot.protos.modlog import ModLogProto

logging.basicConfig(level=logging.INFO)
# logging.setLoggerClass(LoggingHandler)

# have to import these after logging is configured, cuz for some fucking
# reason, if i don't, it sets up its own logging *when imported* :SCWEEEE:
import hikari  # noqa E402
import tanjun  # noqa E402
from bot.bot import BotBot  # noqa E402

sys.path.append(os.path.abspath("external/hikari-yougan/"))

dotenv.load_dotenv()
import ptero  # noqa e402

bot_bot = BotBot(os.getenv("TOKEN"),
                 intents=hikari.Intents.GUILD_MESSAGES | hikari.Intents.GUILD_INTEGRATIONS |
                         hikari.Intents.GUILD_VOICE_STATES | hikari.Intents.GUILDS | hikari.Intents.GUILD_MEMBERS)  # noqa


@bot_bot.listen(hikari.StartedEvent)
async def ready(event: hikari.StartedEvent):
    await bot_bot.lavalink_client.start_nodes()


def create_modlog_impl():
    return ModLogImpl(bot_bot)


GUILD_ID: int = 786473829190860800

(
    tanjun.Client
        .from_gateway_bot(bot_bot, set_global_commands=GUILD_ID)  # noqa e131
        .set_type_dependency(DatabaseProto, tanjun.cache_callback(DatabaseImpl.connect))
        .set_type_dependency(ModLogProto, tanjun.cache_callback(create_modlog_impl))
        .add_prefix("!")
        .load_modules(*Path("./modules").glob("*.py"))
)

bot_bot.run()
