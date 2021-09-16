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
import os
from typing import Optional

import tanjun
from tanjun import SlashContext
import mcstatus

import ptero
from ptero.models import subdomains

component = tanjun.Component()
ptero_client = ptero.PteroClient(os.getenv("PTERO"), "https://panel.rawr-x3.me")


@component.with_slash_command
@tanjun.with_str_slash_option("server", "Server to get the status of",
                              choices=[(server.name, server.identifier) for server in ptero_client.servers],
                              default=None)
@tanjun.as_slash_command("server-status", "Shows the status of the network")
async def server_status(ctx: SlashContext, server: Optional[str] = None):
    if server:
        await ctx.respond(
            str(await ptero_client.server_details(server))
        )
    else:
        await ctx.respond("<a:loading:420359325437919243> Looking up all server details - might take a bit")
        await ctx.edit_initial_response(
            "\n".join(map(str, await ptero_client.get_all_server_details()))
        )

@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    # This loads the component, and is necessary in EVERY module,
    # otherwise you'll get an error.
    client.add_component(component.copy())
