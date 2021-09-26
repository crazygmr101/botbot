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

import hikari
import tanjun
import yuyo
from hikari.impl import ActionRowBuilder

component = tanjun.Component()

group = component.with_slash_command(tanjun.slash_command_group("test", "Test stuff"))


class Executor(yuyo.MultiComponentExecutor):
    def __init__(self, bot: hikari.GatewayBotAware):
        super().__init__()
        self._bot = bot
        self._client = yuyo.ComponentClient.from_gateway_bot(bot)
        self.add_builder(ActionRowBuilder().add_button(1, "bonk").set_label("Click me!").add_to_container())


    async def execute(self, interaction: hikari.ComponentInteraction, **kwargs) -> None:
        await interaction.create_initial_response(content="bonk :D",
                                                  flags=hikari.MessageFlag.EPHEMERAL,
                                                  response_type=hikari.ResponseType.MESSAGE_CREATE)


@group.with_command
@tanjun.as_slash_command("test", "test")
async def server_status(ctx: tanjun.SlashContext):
    executor = Executor()
    client = yuyo.ComponentClient.from_gateway_bot(ctx.shards)
    row = ActionRowBuilder()
    row.add_button(1, "bonk").set_label("Click me!").add_to_container()
    executor.add_builder(row)
    message = await ctx.respond("Bonk", components=executor.builders, ensure_result=True)
    client.add_executor(message, executor)
    client.open()


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    # This loads the component, and is necessary in EVERY module,
    # otherwise you'll get an error.
    client.add_component(component.copy())
