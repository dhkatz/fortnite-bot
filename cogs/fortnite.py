import re
from datetime import datetime

import aiohttp
import discord
import pycountry
from bs4 import BeautifulSoup
from discord.ext import commands

from util import context
from util import paginator


class Fortnite:
    """General Fortnite commands and information."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def daily(self, ctx: context.Context):
        """Get daily sale items."""
        url, html = f'https://stormshield.one/pvp/sales', None
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    html = await r.text()

        if html is None:
            return None

        data, soup = {}, BeautifulSoup(html, 'html.parser')

        sale = soup.find_all(class_='sale__items')[1]
        date = sale.find_previous_sibling(class_="row").h2.text
        data['date'] = datetime.strptime(date + ' ' + str(datetime.utcnow().year), '%d %b %Y').strftime('%B %d, %Y')
        images = sale.find_all('img', class_='col')
        data['images'] = ['https://stormshield.one' + image['src'] for image in images]

        items = sale.find_all('strong')
        title = [item.parent.text for item in items]
        title = [item.replace('\n', ' ').strip() for item in title]

        prices, items = [], []
        regex, regex2 = '\([0-9]+v\)', '[0-9]+'
        for item in title:
            match = re.search(regex, item).group(0)
            prices.append(re.search(regex2, match).group(0))
            items.append(item.replace(match, '').strip())
        data['prices'] = prices
        data['items'] = items

        embeds = []
        for i in range(len(items)):
            embeds.append(await self.build_item_embed(data, i))
        p = paginator.EmbedPages(ctx, entries=embeds)
        await p.paginate()

    @commands.command()
    async def weekly(self, ctx: context.Context):
        """Get weekly sale items."""
        url, html = f'https://stormshield.one/pvp/sales', None
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    html = await r.text()

        if html is None:
            return None

        data, soup = {}, BeautifulSoup(html, 'html.parser')

        sale = soup.find_all(class_='sale__items')[0]
        data['date'] = 'Weekly Sale'
        images = sale.find_all('img')
        data['images'] = ['https://stormshield.one' + image['src'] for image in images]

        items = sale.find_all('strong')
        title = [item.parent.text for item in items]
        title = [item.replace('\n', ' ').strip() for item in title]

        prices, items = [], []
        regex, regex2 = '\([0-9]+v\)', '[0-9]+'
        for item in title:
            match = re.search(regex, item).group(0)
            prices.append(re.search(regex2, match).group(0))
            items.append(item.replace(match, '').strip())
        data['prices'] = prices
        data['items'] = items

        embeds = []
        for i in range(len(items)):
            embeds.append(await self.build_item_embed(data, i))
        p = paginator.EmbedPages(ctx, entries=embeds)
        await p.paginate()

    @commands.command()
    async def bug(self, ctx):
        """Where to report a bug found in Fortnite."""
        embed = discord.Embed()
        embed.title = 'Epic Games Support'
        embed.colour = discord.Colour.blue()
        embed.description = 'How do I submit a bug report for Fortnite?'
        embed.url = 'http://fortnitehelp.epicgames.com/customer/en/portal/articles/2841545-how-do-i-submit-a-bug' \
                    '-report-for-fortnite- '
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
    async def twitch(self, ctx):
        """Get the top Fortnite Twitch streamers."""
        url = 'https://api.partybus.gg/v1/streams'
        streamers = []
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    json = await r.json()
                    for i in range(0, 10):
                        streamers.append(json[i])

        embeds = []
        for streamer in streamers:
            embeds.append(await self.build_stream_embed(streamer))
        p = paginator.EmbedPages(ctx, icon_url='https://i.imgur.com/dXyljNT.png', entries=embeds)
        await p.paginate()

    @commands.command()
    async def lfg(self, ctx):
        """Are you looking for a game?"""
        br_channels, stw_channels, lfg_channels = set(), set(), set()
        br_list = stw_list = lfg_list = ''
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel) and 'lfg' in channel.name:
                if 'br' in channel.name:
                    br_channels.add(channel)
                elif 'stw' in channel.name:
                    stw_channels.add(channel)
                else:
                    lfg_channels.add(channel)

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
        if len(lfg_channels) > 0:
            lfg_list = '**LFG Channels:** '
            while len(lfg_channels) > 0:
                channel = lfg_channels.pop()
                if 'lfg' in channel.name:
                    lfg_list += channel.mention
                    if len(lfg_channels) > 0:
                        lfg_list += ' | '
            lfg_list += '\n\n'
        if len(br_list) or len(stw_list):
            await ctx.send('Please use any of the #lfg channels if you\'re looking for people to play with:\n\n' +
                           br_list + stw_list)
        elif len(lfg_list):
            await ctx.send('Please use any of the #lfg channels if you\'re looking for people to play with:\n\n' +
                           lfg_list)
        else:
            await self.bot.embed_notify(ctx, 1, 'Error', 'This server does not have any LFG channels setup!\n\n'
                                                         'Please add channels containing *lfg* and optionally either'
                                                         ' *br* or *stw*.\n\n'
                                                         'Example: **lfg_channel**, **lfg_br**, or **lfg_stw_pc**.')

    @staticmethod
    async def build_item_embed(data: dict, number: int):
        embed = discord.Embed(color=8198301)
        embed.title = 'Fortnite: Item Sale'
        embed.description = data['date']
        embed.set_thumbnail(url=data['images'][number])
        embed.add_field(name='Item', value=data['items'][number])
        embed.add_field(name='Price', value=str(data['prices'][number]) + ' V-Bucks')
        return embed

    @staticmethod
    async def build_stream_embed(streamer):
        embed = discord.Embed(color=6570404)
        embed.title = streamer['displayName']
        embed.description = streamer['status']
        embed.url = f'https://twitch.tv/{streamer["name"]}'
        embed.add_field(name='Viewers', value=str(streamer['viewers']))
        language = pycountry.languages.lookup(streamer['language'][:2])
        embed.add_field(name='Language', value=language.name)
        return embed


def setup(bot):
    bot.add_cog(Fortnite(bot))