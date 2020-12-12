from typing import Callable, Container, Optional

from discord.ext import commands
from discord.ext.commands import CheckFailure



def in_whitelist(
        *,
        channels: Container[int] = (),
        categories: Container[int] = (),
        roles: Container[int] = (),
        redirect: Optional[int] = None,
        fail_silently: bool = False,
) -> Callable:
    """
    Check if a command was issued in a whitelisted context.
    The whitelists that can be provided are:
    - `channels`: a container with channel ids for whitelisted channels
    - `categories`: a container with category ids for whitelisted categories
    - `roles`: a container with with role ids for whitelisted roles
    If the command was invoked in a context that was not whitelisted, the member is either
    redirected to the `redirect` channel that was passed (default: #bot-commands) or simply
    told that they're not allowed to use this particular command (if `None` was passed).
    """

    def predicate(ctx: commands.Context) -> bool:
        """Check if command was issued in a whitelisted context."""
        return in_whitelist_check(ctx, channels, categories, roles, redirect, fail_silently)

    return commands.check(predicate)


def in_whitelist_check(
        ctx: commands.Context,
        channels: Container[int] = (),
        categories: Container[int] = (),
        roles: Container[int] = (),
        redirect: Optional[int] = None,
        fail_silently: bool = False,
) -> bool:
    """
    Check if a command was issued in a whitelisted context.
    The whitelists that can be provided are:
    - `channels`: a container with channel ids for whitelisted channels
    - `categories`: a container with category ids for whitelisted categories
    - `roles`: a container with with role ids for whitelisted roles
    If the command was invoked in a context that was not whitelisted, the member is either
    redirected to the `redirect` channel that was passed (default: #bot-commands) or simply
    told that they're not allowed to use this particular command (if `None` was passed).
    """
    if redirect and redirect not in channels:
        # It does not make sense for the channel whitelist to not contain the redirection
        # channel (if applicable). That's why we add the redirection channel to the `channels`
        # container if it's not already in it. As we allow any container type to be passed,
        # we first create a tuple in order to safely add the redirection channel.
        #
        # Note: It's possible for the redirect channel to be in a whitelisted category, but
        # there's no easy way to check that and as a channel can easily be moved in and out of
        # categories, it's probably not wise to rely on its category in any case.
        channels = tuple(channels) + (redirect,)

    if channels and ctx.channel.id in channels:
        return True

    # Only check the category id if we have a category whitelist and the channel has a `category_id`
    if categories and hasattr(ctx.channel, "category_id") and ctx.channel.category_id in categories:
        return True

    # Only check the roles whitelist if we have one and ensure the author's roles attribute returns
    # an iterable to prevent breakage in DM channels (for if we ever decide to enable commands there).
    if roles and any(r.id in roles for r in getattr(ctx.author, "roles", ())):
        return True

    # Some commands are secret, and should produce no feedback at all.
    if not fail_silently:
        raise InWhitelistCheckFailure(redirect)
    return False


class InWhitelistCheckFailure(CheckFailure):
    """Raised when the `in_whitelist` check fails."""

    def __init__(self, redirect_channel: Optional[int]) -> None:
        self.redirect_channel = redirect_channel

        if redirect_channel:
            redirect_message = f" here. Please use the <#{redirect_channel}> channel instead"
        else:
            redirect_message = ""

        error_message = f"You are not allowed to use that command{redirect_message}."

        super().__init__(error_message)