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
from tanjun import SlashContext, HaltExecution


async def in_voice_channel(ctx: SlashContext):
    if not ctx.get_guild().get_voice_state(ctx.get_guild().get_my_member()):
        await ctx.respond("I'm not in a voice channel. Use `/music join` when in a voice "
                          "channel")
        raise HaltExecution
    return True


async def author_in_voice_channel(ctx: SlashContext):
    if not ctx.get_guild().get_voice_state(ctx.author):
        await ctx.respond("You must be in a voice channel to use this command")
        raise HaltExecution
    return True


async def author_in_same_voice_channel(ctx: SlashContext):
    if not (author_state := ctx.get_guild().get_voice_state(ctx.author)):
        await ctx.respond("You must be in a voice channel to use this command")
        raise HaltExecution
    if not (bot_state := ctx.get_guild().get_voice_state(ctx.get_guild().get_my_member())):
        await ctx.respond("I'm not in a voice channel. Use `/music join` when in a voice "
                          "channel")
        raise HaltExecution
    if author_state.channel_id != bot_state.channel_id:
        await ctx.respond("You must be in the same voice channel as me to run this command")
        raise HaltExecution
    return True


async def is_maddie_or_impostor_with_maddie_role(ctx: SlashContext):
    if 787131145480699917 not in [role.id for role in ctx.get_guild().get_member(ctx.author).get_roles()]:
        await ctx.create_initial_response("You can't use this command", flags=hikari.MessageFlag.EPHEMERAL)
        raise HaltExecution
    return True
