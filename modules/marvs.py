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

from bot.checks import is_maddie_or_dan
from bot.protos.database import DatabaseProto

component = tanjun.Component()

group = component.with_slash_command(tanjun.slash_command_group("marv", "Marv stuff"))


@group.with_command
@tanjun.with_check(is_maddie_or_dan)
@tanjun.with_str_slash_option("marv", "Marv URL")
@tanjun.as_slash_command("add", "add a marv", default_to_ephemeral=True)
async def add_marv(ctx: tanjun.SlashContext, marv: str, database: DatabaseProto = tanjun.injected(type=DatabaseProto)):
    status, row = await database.add_marv(marv)
    if status == DatabaseProto.DUPLICATE:
        await ctx.respond(f"That marv is already added as marv {row}")
    else:
        await ctx.respond(f"Added {marv} as marv {row}")


@group.with_command
@tanjun.as_slash_command("show", "show a marv")
async def show_marv(ctx: tanjun.SlashContext, database: DatabaseProto = tanjun.injected(type=DatabaseProto)):
    await ctx.respond(embed=hikari.Embed(title="Marv").set_image(await database.get_marv()))


@group.with_command
@tanjun.with_check(is_maddie_or_dan)
@tanjun.with_int_slash_option("page", "Page to get")
@tanjun.as_slash_command("list", "list the marvs", default_to_ephemeral=True)
async def list_marvs(ctx: tanjun.SlashContext, page: int,
                     database: DatabaseProto = tanjun.injected(type=DatabaseProto)):
    marvs = await database.get_all_marvs()
    pages = [marvs[i:i + 10] for i in range(0, len(marvs), 10)]

    if not 0 < page <= len(pages):
        return ctx.respond(f"That's an invalid page, there {'are' if len(pages) > 1 else 'is'} {len(pages)} "
                           f"page{'s' if len(pages) > 1 else ''}")
    await ctx.respond(content=f"**Marv page {page}**\n" +
                              "\n\n".join(f"Marv {n}:\n<{marv}>" for n, marv in pages[page-1]))

@group.with_command
@tanjun.with_check(is_maddie_or_dan)
@tanjun.with_int_slash_option("marv", "Marv to delete")
@tanjun.as_slash_command("delete", "remove a marv", default_to_ephemeral=True)
async def list_marvs(ctx: tanjun.SlashContext, marv: int,
                     database: DatabaseProto = tanjun.injected(type=DatabaseProto)):
    result, deleted = await database.delete_marv(marv)
    if result == DatabaseProto.NOT_FOUND:
        await ctx.respond("That marv wasn't found - do /marv list to see marvs")
    else:
        await ctx.respond(f"Marv <{deleted}> deleted")

@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    # This loads the component, and is necessary in EVERY module,
    # otherwise you'll get an error.
    client.add_component(component.copy())
