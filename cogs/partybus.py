import aiohttp
import discord
from discord.ext import commands
from peewee import *
from datetime import datetime

from bot import fortnite_db


class PartyBus:
    """Partybus.gg related commands."""

    def __init__(self, bot):
        self.bot = bot
        self.init()

    def init(self):
        if 'player' not in self.bot.db.get_tables():
            self.bot.logger.info('Created Player table in database.')
            Player.create_table()

    @commands.command()
    async def solo(self, ctx, name: str = ''):
        """Return solo stats for a player or yourself using Partybus.gg"""
        player = await self.player_interface(ctx, name)

        if len(player) > 0:
            embed = await self.player_stats(player, 1)
            if embed is not None:
                await ctx.send(embed=embed)
            else:
                await self.bot.embed_notify(ctx, 2, 'Notice', 'No solo statistics found!')

    @commands.command()
    async def duo(self, ctx, name: str = ''):
        """Return duo stats for a player or yourself using Partybus.gg"""
        player = await self.player_interface(ctx, name)
        if len(player) > 0:
            embed = await self.player_stats(player, 2)
            if embed is not None:
                await ctx.send(embed=embed)
            else:
                await self.bot.embed_notify(ctx, 2, 'Notice', 'No duo statistics found!')

    @commands.command()
    async def squad(self, ctx, name: str = ''):
        """Return squad stats for a player or yourself using Partybus.gg"""
        player = await self.player_interface(ctx, name)
        if len(player) > 0:
            embed = await self.player_stats(player, 3)
            if embed is not None:
                await ctx.send(embed=embed)
            else:
                await self.bot.embed_notify(ctx, 2, 'Notice', 'No squad statistics found!')

    @commands.command()
    async def lpg(self, ctx, name: str = ''):
        player = await self.player_interface(ctx, name)

        if len(player) > 0:
            embed = await self.player_lpg(player)
            if embed is not None:
                await ctx.send(embed=embed)
            else:
                await self.bot.embed_notify(ctx, 1, 'Error', 'No game data found!')

    @commands.command()
    async def ign(self, ctx, epic_id: str = ''):
        """Tag your Paragon IGN to your Discord account. Surround names with spaces in quotes. Empty to see current."""
        embed = discord.Embed()
        if len(epic_id) > 0:
            player_id = await self.player_interface(ctx, epic_id)

            if player_id == '':
                await self.bot.embed_notify(ctx, 1, 'Error',
                                            'The Epic ID you entered does not exist! Remember names with spaces need quotes!')
                return

            try:
                player = Player.get(Player.discord_id == ctx.author.id)
                player.partybus_id = epic_id
                player.save()
                await self.bot.embed_notify(ctx, 0, 'Epic ID Updated', 'You have updated your Epic ID!')
            except DoesNotExist:
                player = Player(partybus_id=player_id, discord_id=ctx.author.id)
                player.save()
                await self.bot.embed_notify(ctx, 0, 'Epic ID Updated',
                                            'You have attached your Epic ID to your Discord ID!')
        else:
            # User is requesting their current ID!
            try:
                player = Player.get(Player.discord_id == ctx.author.id)
                embed.title = 'Current Epic ID'
                embed.colour = discord.Colour.blue()
                embed.description = player.partybus_id
                embed.url = 'https://partybus.gg/player/' + player.partybus_id
                embed.set_footer(text='Fortnite')
                await ctx.send(embed=embed)
            except DoesNotExist:
                await self.bot.embed_notify(ctx, 1, 'Error',
                                            'No player name specified or no Epic ID was found linked to your account!'
                                            + '\n(See \'' + self.bot.prefix
                                            + 'help ign\' for more command information!)')

    async def player_interface(self, ctx, name):
        # Command has NOT specified a username
        if len(name) == 0:
            try:
                # Player is stored in DB
                player = Player.get(Player.discord_id == ctx.author.id)
                name = player.partybus_id
            except DoesNotExist:
                if isinstance(ctx.author, discord.Member):
                    # Public channel message
                    name = ctx.author.nick if ctx.author.nick is not None else ctx.author.name
                else:
                    # Private channel. We have to pull by name or DB
                    name = ctx.author.name

        if not await self.player_exists(name):
            if len(name) > 0:
                await self.bot.embed_notify(ctx, 1, 'Error',
                                            'The user you entered does not seem to exist, please re-check the name!')
            else:
                await self.bot.embed_notify(ctx, 1, 'Error',
                                            'Your Discord name does not seem to be the same as your Fortnite username,'
                                            + ' please find your IGN and use the command again. Alternatively, tag your'
                                            + ' Epic ID to your Discord account by typing ' + self.bot.prefix
                                            + 'ign <PlayerName>!')
            return ''
        else:
            return name

    @staticmethod
    async def player_exists(name: str):
        """Check if a player account exists."""
        url = 'https://api.partybus.gg/v1/players/' + name

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                return r.status == 200

    @staticmethod
    async def player_stats(name, mode):
        """Get the general stats for a Fortnite player."""
        url = 'https://api.partybus.gg/v1/players/' + name

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    js = await r.json()

                    embed = discord.Embed()

                    embed.title = js['details']['displayName']
                    embed.url = 'https://partybus.gg/player/' + js['details']['displayName']

                    platform = js['stats'][0]['platform']
                    if platform == 'pc':
                        embed.set_footer(text='PC',
                                         icon_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Windows_logo_-_2012.svg/768px-Windows_logo_-_2012.svg.png')
                        embed.colour = 44527
                    elif platform == 'ps4':
                        embed.set_footer(text='PS4',
                                         icon_url='https://psmedia.playstation.com/is/image/psmedia/404-three-column-playstationlogo-01-en-19feb15?$ThreeColFeature_Image$')
                        embed.colour = discord.Colour.dark_blue()
                    elif platform == 'xb1':
                        embed.set_footer(text='XB1',
                                         icon_url='https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/2000px-Xbox_one_logo.svg.png')
                        embed.colour = 1080335

                    if mode == 1:
                        embed.description = 'Solo Statistics'
                        for stat in js['stats']:
                            if stat['p'] == 2:
                                embed.add_field(name='Total Games', value=str(stat['games']))
                                embed.add_field(name='Wins', value=str(stat['placeA']))
                                embed.add_field(name='Win Rate',
                                                value=str(round(stat['placeA'] / stat['games'] * 100, 2)) + '%')
                                embed.add_field(name='KD Ratio',
                                                value=str(round(stat['kills'] / (stat['games'] - stat['placeA']), 1)))
                                embed.add_field(name='Top 10s', value=str(stat['placeB']))
                                embed.add_field(name='Top 25s', value=str(stat['placeC']))
                                return embed
                        return None
                    elif mode == 2:
                        embed.description = 'Duo Statistics'
                        for stat in js['stats']:
                            if stat['p'] == 10:
                                embed.add_field(name='Total Games', value=str(stat['games']))
                                embed.add_field(name='Wins', value=str(stat['placeA']))
                                embed.add_field(name='Win Rate',
                                                value=str(round(stat['placeA'] / stat['games'] * 100, 2)) + '%')
                                embed.add_field(name='Kill Rate', value=str(round(stat['kills'] / stat['games'], 1)))
                                embed.add_field(name='Top 5s', value=str(stat['placeB']))
                                embed.add_field(name='Top 12s', value=str(stat['placeC']))
                                return embed
                        return None
                    elif mode == 3:
                        embed.description = 'Squad Statistics'
                        for stat in js['stats']:
                            if stat['p'] == 9:
                                embed.add_field(name='Total Games', value=str(stat['games']))
                                embed.add_field(name='Wins', value=str(stat['placeA']))
                                embed.add_field(name='Win Rate',
                                                value=str(round(stat['placeA'] / stat['games'] * 100, 2)) + '%')
                                embed.add_field(name='Kill Rate', value=str(round(stat['kills'] / stat['games'], 1)))
                                embed.add_field(name='Top 3s', value=str(stat['placeB']))
                                embed.add_field(name='Top 6s', value=str(stat['placeC']))
                                return embed
                        return None

    @staticmethod
    async def player_lpg(name):
        url = 'https://api.partybus.gg/v1/players/' + name + '/history?p='

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    js = await r.json()
                    game = js[0]

                    embed = discord.Embed()
                    embed.colour = discord.Colour.green() if game['placeA'] > 0 else discord.Colour.dark_red()
                    embed.title = 'Game Played ' + datetime.fromtimestamp(game['modified']).strftime('%Y-%m-%d') + ' (UTC)'
                    embed.description = 'Duration: ' + str(game['minutes']) + ' Min.'
                    embed.add_field(name='Mode',
                                    value='Solo' if game['p'] == 2 else 'Duo' if game['p'] == 10 else 'Squad')
                    embed.add_field(name='Result', value='Victory' if game['placeA'] > 0 else 'Lost')
                    embed.add_field(name='Kills', value=game['kills'])

                    platform = game['platform']
                    if platform == 'pc':
                        embed.set_footer(text='PC',
                                         icon_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Windows_logo_-_2012.svg/768px-Windows_logo_-_2012.svg.png')
                    elif platform == 'ps4':
                        embed.set_footer(text='PS4',
                                         icon_url='https://psmedia.playstation.com/is/image/psmedia/404-three-column-playstationlogo-01-en-19feb15?$ThreeColFeature_Image$')
                    elif platform == 'xb1':
                        embed.set_footer(text='XB1',
                                         icon_url='https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/2000px-Xbox_one_logo.svg.png')

                    return embed
                return None


class BaseModel(Model):
    class Meta:
        database = fortnite_db


class Player(BaseModel):
    partybus_id = CharField(default='')  # This should be unique, but no way to authenticate users
    discord_id = CharField(unique=True)
    blacklist = BooleanField(default=False)


def setup(bot):
    bot.add_cog(PartyBus(bot))
