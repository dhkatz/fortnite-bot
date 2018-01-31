import platform
import time

import aiohttp
import discord
from discord.ext import commands
from memory_profiler import memory_usage
from datetime import datetime, timedelta

from util import context


class General:
    """General Discord bot commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def party(self, ctx: context.Context):
        url = 'https://api.partybus.gg/v1/players/Jaksta'

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                js = await r.json() if r.status == 200 else None

        if js is None:
            return

        modes = [get_mode(js, 2), get_mode(js, 10), get_mode(js, 9)]

        player = {
            'name': js['details']['displayName'],
            'platform': js['stats'][0]['platform'],
        }

        for mode in modes:
            player[mode[0]] = {
                'time': datetime(0, 1, 1) + timedelta(minutes=mode[1]['minutes']),
                'games': mode[1]['games'],
                'wins': mode[1]['placeA'],
                'winRate': round(mode[1]['placeA'] / mode[1]['games'] * 100, 2),
                'killRate': round(mode[1]['kills'] / mode[1]['games'], 1),
                'top25': mode[1]['placeB'],
                'top50': mode[1]['placeC']
            }

        return player

    @commands.command()
    async def donate(self, ctx: context.Context):
        """Can you donate to keep the bot alive?"""
        embed = discord.Embed()
        embed.title = 'Donations'
        embed.colour = 0xefce47
        embed.url = 'https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ZCVUPVPYKUUBN'
        embed.description = 'If you can, please donate to keep the bot alive.'
        embed.add_field(name='Bitcoin', value='1B4NMnzEhQ55wF6X7vj6Utfh79fP15nkw')
        embed.add_field(name='Ethereum', value='0x392b8411d4796c0af98a1E64d23882EC948F0198')
        embed.add_field(name='Paypal', value='xiluziionz@gmail.com', inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='info', aliases=['uptime', 'up'])
    async def _status(self, ctx: context.Context):
        """Information about the bot's status."""
        uptime = time.time() - self.bot.uptime
        hours, minutes, seconds = uptime / 3600, (uptime / 60) % 60, uptime % 60

        users, channel = 0, 0
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

    @commands.command()
    async def ping(self, ctx: context.Context):
        """Measure bot response time."""
        ping = ctx.message
        pong = await ctx.send(embed=discord.Embed(title='Measuring Latency...', color=discord.Colour.dark_red()))
        delta = pong.created_at - ping.created_at
        delta = int(delta.total_seconds() * 1000)
        embed = discord.Embed(color=discord.Colour.green())
        embed.title = 'Latency Results'
        embed.add_field(name='Round Trip', value=f'{delta} ms')
        embed.add_field(name='Web Socket Latency', value=f'{round(self.bot.latency, 5)} ms')
        await pong.edit(embed=embed)

    @commands.command()
    async def prefix(self, ctx: context.Context):
        """Get the command prefix of this server."""
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


def get_mode(data: dict, mode: int):
    mode_str = 'Solo' if mode == 1 else 'Duo' if mode == 10 else 'Squad'
    for stat in data['stats']:
        if stat['p'] == mode:
            return mode_str, stat


def setup(bot):
    bot.add_cog(General(bot))
