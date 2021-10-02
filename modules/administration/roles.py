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
import asyncio
from typing import Optional

import hikari
import tanjun
from yuyo.components import ResponseT, MultiComponentExecutor, ComponentClient

from bot.protos.database import DatabaseProto

component = tanjun.Component()
slash_group = component.with_slash_command(tanjun.slash_command_group("roles", "Select roles"))


class RoleExecutor(MultiComponentExecutor):
    def __init__(self, *args, **kwargs):
        self._roles = kwargs.pop("roles")
        super().__init__(*args, **kwargs)
        self.initial_id = None

    async def execute(
            self, interaction: hikari.ComponentInteraction, /, *, future: Optional[asyncio.Future[ResponseT]] = None
    ) -> None:
        if interaction.message.id != self.initial_id:
            return
        role_ids = [int(value.split("-")[1]) for value in interaction.values]
        current_role_ids = [int(role_id) for role_id in interaction.member.role_ids]
        for role in self._roles:
            if role in role_ids and role not in current_role_ids:
                await interaction.member.add_role(role)
            if role not in role_ids and role in current_role_ids:
                await interaction.member.remove_role(role)
        await interaction.create_initial_response(4, "Roles changed!", flags=hikari.MessageFlag.EPHEMERAL)


@slash_group.with_command
@tanjun.as_slash_command("select", "Select roles", default_to_ephemeral=True)
async def role_select(ctx: tanjun.SlashContext,
                      database: DatabaseProto = tanjun.injected(type=DatabaseProto),
                      client: ComponentClient = tanjun.injected(type=ComponentClient)
                      ):
    row = hikari.impl.ActionRowBuilder()
    sel = row.add_select_menu(f"roles-{ctx.interaction.id}")
    for role_id in (roles := await database.get_roles()):
        role = ctx.cache.get_role(role_id)
        sel.add_option(role.name, f"role-{role.id}").set_is_default(role.id in ctx.member.role_ids).add_to_menu()
    sel.set_placeholder("Select your roles").set_min_values(0).set_max_values(len(roles)).add_to_container()
    executor = RoleExecutor(roles=roles)
    executor.add_builder(row)
    await ctx.create_initial_response("_ _", components=executor.builders, flags=hikari.MessageFlag.EPHEMERAL)
    message = await ctx.fetch_initial_response()
    executor.initial_id = message.id
    client.add_executor(message, executor)


@slash_group.with_command
@tanjun.with_author_permission_check(hikari.Permissions.ADMINISTRATOR)
@tanjun.with_role_slash_option("role", "The role to add")
@tanjun.as_slash_command("add", "Add a role to be self-assignable")
async def role_add(ctx: tanjun.SlashContext, role: hikari.Role,
                   database: DatabaseProto = tanjun.injected(type=DatabaseProto)):
    if await database.add_role(role.id) == DatabaseProto.SUCCESS:
        await ctx.respond(f"Added {role.mention} to be self-assignable", role_mentions=False)
    else:
        await ctx.respond(f"{role.mention} was already self-assignable", role_mentions=False)


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    # This loads the component, and is necessary in EVERY module,
    # otherwise you'll get an error.
    client.add_component(component.copy())
