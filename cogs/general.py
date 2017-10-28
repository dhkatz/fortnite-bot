import discord
import platform
import time
from memory_profiler import memory_usage
from discord.ext import commands


class General:
    """General Discord commands for Fortnite."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bug(self, ctx):
        """Where to report a bug found in Fortnite."""
        embed = discord.Embed()
        embed.title = 'Epic Games Support'
        embed.colour = discord.Colour.blue()
        embed.description = 'How do I submit a bug report for Fortnite?'
        embed.url = 'http://fortnitehelp.epicgames.com/customer/en/portal/articles/2841545-how-do-i-submit-a-bug-report-for-fortnite-'
        embed.add_field(name='Report the Bug In-game',
                        value='• Open the game menu\n\n• Select *Feedback*\n\n• Select *Bug*\n\n'
                              '• Fill in the *Subject* and *Body* fields with your feedback\n\n• Select *Send*',
                        inline=False)
        embed.add_field(name='Report the Bug Online',
                        value='Additionally you can post in the Bug Reporting section of the forums.', inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def support(self, ctx):
        """Do you need support from Epic Games?"""
        await self.bot.embed_notify(ctx, 2, 'Support', 'Our tech support page can be found at http://epic.gm/fnhelp'
                                                       '\nPlease see if any of the issues listed on the page apply to'
                                                       ' you, if not, use the Contact Us button on the right.')

    @commands.command()
    async def lfg(self, ctx):
        """Are you looking for a game?"""
        br_channels, stw_channels = set(), set()
        br_list = stw_list = ''
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel) and 'lfg' in channel.name:
                if 'br' in channel.name:
                    br_channels.add(channel)
                elif 'stw' in channel.name:
                    stw_channels.add(channel)

        if len(br_channels) > 0:
            br_list = '**Battle Royale:** '
            while len(br_channels) > 0:
                channel = br_channels.pop()
                if 'br' in channel.name:
                    br_list += channel.mention
                    if len(br_channels) > 0:
                        br_list += ' | '
            br_list += '\n\n'
        if len(stw_channels) > 0:
            stw_list = '**Save the World:** '
            while len(stw_channels) > 0:
                channel = stw_channels.pop()
                if 'stw' in channel.name:
                    stw_list += channel.mention
                    if len(stw_channels) > 0:
                        stw_list += ' | '
            stw_list += '\n\n'
        if len(br_list) or len(stw_list):
            await ctx.send('Please use any of the #lfg channels if you\'re looking for people to play with:\n\n' +
                           br_list + stw_list)
        else:
            await self.bot.embed_notify(ctx, 1, 'Error', 'This server does not have any LFG channels setup!\n\n'
                                                         'Please add channels containing *lfg* and either'
                                                         ' *br* or *stw*.\n\nExample: **lfg_br** or **lfg_stw_pc**.')

    @commands.command(name='info', aliases=['uptime', 'up'])
    async def _status(self, ctx: commands.Context):
        """Information about the bot's status."""
        uptime = time.time() - self.bot.uptime
        hours = uptime / 3600
        minutes = (uptime / 60) % 60
        seconds = uptime % 60

        users = 0
        channel = 0
        try:
            commands_chart = sorted(self.bot.counter.items(), key=lambda t: t[1], reverse=False)
            top_command = commands_chart.pop()
            command_info = f'{sum(self.bot.counter.values())} (Top Command: {top_command[0]} [x{top_command[1]}])'
        except IndexError:
            command_info = str(sum(self.bot.counter.values()))

        bot_member = ctx.message.guild.get_member(self.bot.user.id)
        for guild in self.bot.guilds:
            users += len(guild.members)
            channel += len(guild.channels)
        embed = discord.Embed(colour=bot_member.top_role.colour)
        app = await self.bot.application_info()
        embed.add_field(name='Bot Creator', value=app.owner.name, inline=False)
        embed.add_field(name='Uptime',
                        value='{0:.0f} Hours, {1:.0f} Minutes, and {2:.0f} Seconds'.format(hours, minutes, seconds),
                        inline=False)
        embed.add_field(name='Total Users', value=users)
        embed.add_field(name='Total Channels', value=channel)
        embed.add_field(name='Total Servers', value=str(len(self.bot.guilds)))
        embed.add_field(name='Command Usage', value=command_info)
        embed.add_field(name='Bot Version', value=self.bot.version)
        embed.add_field(name='Discord.py Version', value=discord.__version__)
        embed.add_field(name='Python Version', value=platform.python_version())
        embed.add_field(name='Memory Usage', value='{} MB'.format(round(memory_usage(-1)[0], 3)))
        embed.add_field(name='Operating System',
                        value='{} {} {}'.format(platform.system(), platform.release(), platform.version()),
                        inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(General(bot))
