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

from bot.protos import DatabaseProto

component = tanjun.Component()

group = component.with_slash_command(tanjun.slash_command_group("test", "test commands"))


@group.with_command
@tanjun.with_user_slash_option("user", "User")
@tanjun.as_slash_command("user", "user1")
async def volume(ctx: tanjun.SlashContext, user: hikari.User,
                 database: DatabaseProto = tanjun.injected(type=DatabaseProto)):
    await ctx.respond(await database.get_info(user.id))



@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    # This loads the component, and is necessary in EVERY module,
    # otherwise you'll get an error.
    client.add_component(component.copy())
