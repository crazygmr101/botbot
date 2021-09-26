import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import dotenv
import humanize

# noinspection PyUnresolvedReferences
from yuyo import ComponentClient

from bot.logging import LoggingHandler

logging.basicConfig(level=logging.INFO)
#logging.setLoggerClass(LoggingHandler)

# have to import these after logging is configured, cuz for some fucking
# reason, if i don't, it sets up its own logging *when imported* :SCWEEEE:
from bot.impl.cache import BotBotCacheImpl  # noqa E402
from bot.impl.database import DatabaseImpl  # noqa E402
from bot.impl.modlog import ModLogImpl  # noqa E402
from bot.protos.cache import BotBotCacheProto  # noqa E402
from bot.protos.database import DatabaseProto  # noqa E402
from bot.protos.modlog import ModLogProto  # noqa E402
from bot.utils import ModLogValues  # noqa E402
import hikari  # noqa E402
import tanjun  # noqa E402
from bot.bot import BotBot  # noqa E402

sys.path.append(os.path.abspath("external/hikari-yougan/"))
sys.path.append(os.path.abspath("external/yuyo/"))

dotenv.load_dotenv()
import ptero  # noqa e402

bot_bot = BotBot(os.getenv("TOKEN"),
                 intents=hikari.Intents.ALL_GUILDS_UNPRIVILEGED)  # noqa

cache = BotBotCacheImpl(bot_bot, 100)
modlog = ModLogImpl(bot_bot)
client = ComponentClient.from_gateway_bot(bot_bot)
client.open()

startup = datetime.now()


@bot_bot.listen(hikari.StartedEvent)
async def ready(event: hikari.StartedEvent):
    await bot_bot.lavalink_client.start_nodes()
    await cache.populate(GUILD_ID, False)
    await modlog.send(modlog.create_embed(ModLogValues.started,
                                          description=f"Startup completed in "
                                                      f"{humanize.naturaldelta(datetime.now() - startup)}"))


def create_modlog_impl():
    return modlog


def create_cache_impl():
    return cache

def create_component_client():
    return client

GUILD_ID: int = 786473829190860800

(
    tanjun.Client
        .from_gateway_bot(bot_bot, set_global_commands=GUILD_ID)  # noqa e131
        .set_type_dependency(DatabaseProto, tanjun.cache_callback(DatabaseImpl.connect))
        .set_type_dependency(ModLogProto, tanjun.cache_callback(create_modlog_impl))
        .set_type_dependency(BotBotCacheProto, tanjun.cache_callback(create_cache_impl))
        .set_type_dependency(ComponentClient, tanjun.cache_callback(create_component_client))
        .add_prefix("!")
        .load_modules(*Path("./modules").glob("**/*.py"))
)

bot_bot.run()
