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
        if guild_prefix.count('|'):
            prefixes = guild_prefix.split('|')
            guild_prefix = ''
            for prefix in prefixes:
                if len(prefix):
                    guild_prefix += f'\"{prefix}\" '
            await self.bot.embed_notify(ctx, 2, 'Guild Prefix', f'The prefixes of this server are {guild_prefix}.'
                                                                f'\nRemember you can also @ me to use commands!')
        else:
            await self.bot.embed_notify(ctx, 2, 'Guild Prefix', f'The prefix of this server is "{guild_prefix}".'
                                                                f'\nRemember you can also @ me to use commands!')

    @prefix.command(name='set')
    @commands.guild_only()
    @checks.is_admin()
    async def prefix_set(self, ctx: context.Context, new_prefix: str):
        """Set the ONE prefix for this server. Use add to add more. Remember you can @ the bot if you mess up."""
        if '|' in new_prefix:
            await self.bot.embed_notify(ctx, 1, 'Guild Prefix Error', 'Your prefix cannot contain the character \'|\'')
            return
        elif new_prefix.startswith(('@', '#')):
            await self.bot.embed_notify(ctx, 1, 'Guild Prefix Error',
                                        f'Your prefix cannot start with the character {new_prefix[0]}')
            return
        changed = ctx.db.set_setting(ctx.guild.id, 'prefix', new_prefix)
        if changed:
            await self.bot.embed_notify(ctx, 2, 'Guild Prefix', f'The prefix of this server is now "{new_prefix}".'
                                                                f'\nRemember you can also @ me to use commands!')
        else:
            await self.bot.embed_notify(ctx, 1, 'Guild Prefix', 'Error changing the server prefix!')

    @prefix.command(name='add')
    @commands.guild_only()
    @checks.is_admin()
    async def prefix_add(self, ctx: context.Context, new_prefix: str):
        """Add another prefix for this server. BE CAREFUL! Remember you can @ the bot if you mess up."""
        if '|' in new_prefix:
            await self.bot.embed_notify(ctx, 1, 'Guild Prefix Error', 'Your prefix cannot contain the character \'|\'')
            return
        elif new_prefix.startswith(('@', '#')):
            await self.bot.embed_notify(ctx, 1, 'Guild Prefix Error',
                                        f'Your prefix cannot start with the character {new_prefix[0]}')
            return
        current = ctx.db.get_setting(ctx.guild.id, 'prefix')
        if '|' in current:  # Multiple prefixes
            if new_prefix in current.split('|'):
                await self.bot.embed_notify(ctx, 1, 'Guild Prefix Error', 'This prefix already exists!')
                return
            else:  # Add the prefix to the existing list
                current += new_prefix + '|'
        else:
            if new_prefix in current:
                await self.bot.embed_notify(ctx, 1, 'Guild Prefix Error', 'This prefix already exists!')
                return
            else:
                current += '|' + new_prefix + '|'
        changed = ctx.db.set_setting(ctx.guild.id, 'prefix', current)
        if changed:
            await self.bot.embed_notify(ctx, 2, 'Guild Prefix', f'The prefix "{new_prefix}" has been added.'
                                                                f'\nRemember you can also @ me to use commands!')
        else:
            await self.bot.embed_notify(ctx, 1, 'Guild Prefix', 'Error changing the server prefix!')

    @prefix.command(name='remove')
    @commands.guild_only()
    @checks.is_admin()
    async def prefix_remove(self, ctx: context.Context, prefix: str):
        """Remove a prefix for this server. You must always have at least one."""
        if '|' in prefix:
            await self.bot.embed_notify(ctx, 1, 'Guild Prefix Error', 'Prefixes cannot contain the character \'|\'')
            return
        current = ctx.db.get_setting(ctx.guild.id, 'prefix')
        if '|' in current:
            if prefix not in current:
                await self.bot.embed_notify(ctx, 1, 'Guild Prefix Error', 'This prefix does not exist!')
                return
            if current.count('|') == 2:
                current = current.replace('|' + prefix + '|', '')
            else:
                current = current.replace(prefix + '|', '')
        else:  # We only have one prefix
            await self.bot.embed_notify(ctx, 1, 'Guild Prefix Error', 'You must have at least one prefix! '
                                                                      'Please use prefix reset to set default.')
            return
        changed = ctx.db.set_setting(ctx.guild.id, 'prefix', current)
        if changed:
            await self.bot.embed_notify(ctx, 2, 'Guild Prefix', f'The prefix "{prefix}" has been removed.'
                                                                f'\nRemember you can also @ me to use commands!')
        else:
            await self.bot.embed_notify(ctx, 1, 'Guild Prefix', 'Error changing the server prefix!')

    @prefix.command(name='reset')
    @commands.guild_only()
    @checks.is_admin()
    async def prefix_reset(self, ctx: context.Context):
        """Reset the server prefix to the default"""
        changed = ctx.db.set_setting(ctx.guild.id, 'prefix', self.bot.prefix)
        if changed:
            await self.bot.embed_notify(ctx, 2, 'Guild Prefix', f'The prefix has been reset to "{self.bot.prefix}".'
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
