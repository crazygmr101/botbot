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
from random import choice

import hikari
import tanjun

component = tanjun.Component()

group = component.with_slash_command(tanjun.slash_command_group("bot", "BotBot stuff"))

with open("marvs.txt") as marvs_fp:
    marvs = marvs_fp.readlines()


@group.with_command
@tanjun.as_slash_command("status", "Status")
async def test_command(ctx: tanjun.SlashContext):
    marv_button_bar = ctx.rest.build_action_row() \
        .add_button(1, "show-marv").set_label("Have a marv pic :D").add_to_container()
    await ctx.respond(
        content=f"**BotBot status**\n"
                f"Users: {ctx.cache.get_guild(ctx.guild_id).member_count}",
        component=marv_button_bar
    )


@component.with_listener(hikari.InteractionCreateEvent)
async def marv_button_listener(event: hikari.InteractionCreateEvent):
    if event.interaction.type != hikari.InteractionType.MESSAGE_COMPONENT:
        return
    # noinspection PyTypeChecker
    interaction: hikari.ComponentInteraction = event.interaction
    if interaction.custom_id != "show-marv":
        return
    await interaction.create_initial_response(response_type=4,
                                              embed=hikari.Embed(title="Marv").set_image(choice(marvs)),
                                              flags=hikari.MessageFlag.EPHEMERAL)


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    # This loads the component, and is necessary in EVERY module,
    # otherwise you'll get an error.
    client.add_component(component.copy())
