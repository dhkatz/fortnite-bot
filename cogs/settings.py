from discord.ext import commands

from util import checks
from util import context


class Settings:
    """Settings and commands unique to servers."""

    def __init__(self, bot):
        self.bot = bot
        self.init()
        self.cannot_disable = ['DATABASE', 'SETTINGS', 'GENERAL']

    def init(self):
        pass

    @commands.group()
    @commands.guild_only()
    @checks.is_admin()
    async def settings(self, ctx):
        """Modify server settings."""
        pass

    @settings.group()
    @commands.guild_only()
    @checks.is_admin()
    async def reset(self, ctx: context.Context):
        """Reset the server's settings"""
        changed = ctx.db.reset(ctx.guild.id)
        if changed:
            await self.bot.embed_notify(ctx, 0, 'Settings Reset', 'The server settings were reset! (Including prefix)')

    @settings.group()
    @commands.guild_only()
    @checks.is_admin()
    async def prefix(self, ctx: context.Context):
        """Prefix configuration."""
        pass

    @prefix.command(name='get')
    @commands.guild_only()
    @checks.is_admin()
    async def prefix_get(self, ctx: context.Context):
        """Get the prefix for this server."""
        guild_prefix = ctx.db.get_setting(ctx.guild.id, 'prefix')
        print(f'Guild Prefix: {guild_prefix}')
        await self.bot.embed_notify(ctx, 2, 'Guild Prefix', f'The prefix of this server is "{guild_prefix}".'
                                                            f'\nRemember you can also @ me to use commands!')

    @prefix.command(name='set')
    @commands.guild_only()
    @checks.is_admin()
    async def prefix_set(self, ctx: context.Context, new_prefix: str):
        """Set the prefix for this server. BE CAREFUL! Remember you can @ the bot if you mess up."""
        changed = ctx.db.set_setting(ctx.guild.id, 'prefix', new_prefix)
        if changed:
            await self.bot.embed_notify(ctx, 2, 'Guild Prefix', f'The prefix of this server is now "{new_prefix}".'
                                                                f'\nRemember you can also @ me to use commands!')
        else:
            await self.bot.embed_notify(ctx, 1, 'Guild Prefix', 'Error changing the server prefix!')

    @settings.group(aliases=['extension', 'plugin'])
    @commands.guild_only()
    @checks.is_admin()
    async def cog(self, ctx: context.Context):
        """Extension configuration."""
        pass

    @cog.command(name='get')
    @commands.guild_only()
    @checks.is_admin()
    async def cog_get(self, ctx: context.Context, cog: str):
        """Get the current status of a cog/extension/plugin. Use 'all' instead to get all cogs."""
        if cog.upper() == 'ALL':
            cog_list = ''
            for key in self.bot.cogs.keys():
                cog_list += key + '\n'
            await self.bot.embed_notify(ctx, 2, 'List of Extensions', cog_list)
            return
        cog = cog.capitalize()
        enabled = ctx.db.get_cog(ctx.guild.id, cog)
        if enabled:
            await self.bot.embed_notify(ctx, 2, 'Extension', f'The {cog} extension is enabled!')
        else:
            await self.bot.embed_notify(ctx, 1, 'Extension', f'The {cog} extension is disabled or does not exist!')

    @cog.command(name='set')
    @commands.guild_only()
    @checks.is_admin()
    async def cog_set(self, ctx: context.Context, cog: str, value: bool):
        """Set the status of a cog/extension/plugin. Value must be true/false."""
        if cog.upper() in self.cannot_disable:
            await self.bot.embed_notify(ctx, 1, 'Error', 'You cannot disable core extensions!')
            return
        cog = cog.capitalize()
        changed = ctx.db.set_cog(ctx.guild.id, cog, value)
        if changed:
            await self.bot.embed_notify(ctx, 2, 'Extension', f'The {cog} extension is now '
                                                             f'{str("enabled") if value else str("disabled")}!')
        else:
            await self.bot.embed_notify(ctx, 1, 'Extension', f'The {cog} extension does not exist!')


def setup(bot):
    bot.add_cog(Settings(bot))
