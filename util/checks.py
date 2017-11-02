from discord.ext import commands

from config import config
from util import context


def check_permissions(ctx, perms, *, check=all):
    owner = ctx.author.id == config.__owner__
    if owner:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_permissions(*, check=all, **perms):
    def predicate(ctx):
        return check_permissions(ctx, perms, check=check)

    return commands.check(predicate)


def check_guild_permissions(ctx: commands.Context, perms, *, check=all):
    owner = ctx.author.id == config.__owner__
    if owner:
        return True

    if ctx.guild is None:
        return False

    resolved = ctx.author.guild_permissions
    return check(getattr(resolved, name, None) == value for name, value in perms.items())


def has_guild_permissions(*, check=all, **perms):
    def predicate(ctx):
        return check_guild_permissions(ctx, perms, check=check)

    return commands.check(predicate)


# These do not take channel overrides into account

def is_mod():
    def predicate(ctx):
        return check_guild_permissions(ctx, {'manage_guild': True})

    return commands.check(predicate)


def is_admin():
    def predicate(ctx):
        return check_guild_permissions(ctx, {'administrator': True})

    return commands.check(predicate)


def mod_or_permissions(**perms):
    perms['manage_guild'] = True

    def predicate(ctx):
        return check_guild_permissions(ctx, perms, check=any)

    return commands.check(predicate)


def admin_or_permissions(**perms):
    perms['administrator'] = True

    def predicate(ctx):
        return check_guild_permissions(ctx, perms, check=any)

    return commands.check(predicate)


def cog_enabled():
    def predicate(ctx: context.Context):
        return ctx.db.get_cog(ctx.guild.id, ctx.command.cog_name)

    return commands.check(predicate)


def is_in_guilds(*guild_ids):
    def predicate(ctx):
        guild = ctx.guild
        if guild is None:
            return False
        return guild.id in guild_ids

    return commands.check(predicate)
