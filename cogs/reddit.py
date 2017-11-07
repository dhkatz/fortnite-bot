import time

import discord
import praw
import prawcore
from discord.ext import commands
from peewee import *

from bot import fortnite_db
from util import checks
from util.paginator import EmbedPages


class Reddit:
    """Reddit related commands for the /r/Fortnite and /r/FortniteBR subreddits"""

    def __init__(self, bot):
        self.bot = bot
        self.instance = praw.Reddit(user_agent='Fortnite Discord Bot', client_id=self.bot.config['reddit']['client_id'],
                                    client_secret=self.bot.config['reddit']['client_secret'],
                                    username=self.bot.config['reddit']['username'],
                                    password=self.bot.config['reddit']['password'])
        self.subreddit = {'fortnite': self.instance.subreddit('fortnite'),
                          'fortnitebr': self.instance.subreddit('fortnitebr')}
        self.bot.logger.info(f'[Reddit] Logged into Reddit as {self.instance.user.me()}')
        self.icon_url = 'http://i.imgur.com/sdO8tAw.png'
        # self.bot.scheduler.add_job()

    def init(self):
        if 'post' not in self.bot.db.get_tables():
            self.bot.logger.info('[Reddit] Created Post table in database.')
            Post.create_table()

    @commands.group()
    @checks.cog_enabled()
    async def reddit(self, ctx):
        """Reddit commands. See 'help reddit'."""
        pass

    @commands.command(hidden=True)
    @checks.cog_enabled()
    @commands.is_owner()
    async def test(self, ctx):
        """Test post embed"""
        embed = discord.Embed()
        embed.colour = discord.Colour.blue()
        embed.title = 'Pending Submission'
        embed.description = 'Please approve or deny this post'
        embed.url = 'https://www.google.com/'
        embed.add_field(name='Author', value='JShredz')
        embed.add_field(name='Post Type', value='Link (Video)')
        embed.add_field(name='Length', value='1:30')
        embed.add_field(name='Title', value='My Awesome Fortnite Video', inline=False)
        embed.add_field(name='Approved', value='False')
        embed.add_field(name='Time', value='Wed, 01 Nov 2017 20:21 GMT')
        embed.add_field(name='User Notes',
                        value='Post history indicates this user is not following promotion guidelines.', inline=False)
        embed.set_footer(icon_url=self.icon_url, text='Status Pending')
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @checks.cog_enabled()
    @commands.is_owner()
    async def test2(self, ctx):
        """Test post embed"""
        embed = discord.Embed()
        embed.colour = discord.Colour.green()
        embed.title = 'Submission Approved'
        embed.description = 'Approved on Wed, 01 Nov 2017 20:24 GMT'
        embed.url = 'https://www.google.com/'
        embed.add_field(name='Author', value='JShredz')
        embed.add_field(name='Post Type', value='Link (Video)')
        embed.add_field(name='Length', value='1:30')
        embed.add_field(name='Title', value='My Awesome Fortnite Video', inline=False)
        embed.add_field(name='Approved', value='True')
        embed.add_field(name='Time', value='Wed, 01 Nov 2017 20:21 GMT')
        embed.add_field(name='User Notes',
                        value='Post history indicates this user is not following promotion guidelines.', inline=False)
        embed.set_footer(icon_url=self.icon_url, text='Approved by MCiLuZiioNz')
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @checks.cog_enabled()
    @commands.is_owner()
    async def test3(self, ctx):
        """Test post embed"""
        embed = discord.Embed()
        embed.colour = discord.Colour.dark_red()
        embed.title = 'Pending Report'
        embed.description = 'Please reapprove, remove, or ignore the report.'
        embed.url = 'https://www.google.com/'
        embed.add_field(name='Author', value='JShredz')
        embed.add_field(name='Post Type', value='Comment')
        embed.add_field(name='Content', value='Some generic mean comment', inline=False)
        embed.add_field(name='Score', value='-63')
        embed.add_field(name='Reports', value='2')
        embed.add_field(name='Approved', value='False')
        embed.add_field(name='Time', value='Wed, 01 Nov 2017 20:21 GMT')
        embed.add_field(name='Report Reason', value='This comment offended me.', inline=False)
        embed.add_field(name='Report Notes',
                        value='Possibly contains offensive content.', inline=False)
        # embed.set_footer(icon_url=self.icon_url, text='Approved by MCiLuZiioNz')
        await ctx.send(embed=embed)

    @reddit.command(name='sticky')
    @commands.cooldown(1, 15, commands.BucketType.user)
    @checks.cog_enabled()
    async def reddit_stickied(self, ctx, subreddit: str = 'fortnite'):
        """Get the stickied posts from /r/Fortnite or /r/FortniteBR"""
        subreddit = 'fortnitebr' if 'fortnitebr' in subreddit else 'fortnite'  # Normalize name
        embeds = []
        for i in range(1, 3):
            try:
                sticky = self.subreddit[subreddit].sticky(number=i)
            except prawcore.NotFound:
                continue
            else:
                embeds.append(await self.build_submission_embed(sticky))
        if len(embeds) == 0:
            self.bot.embed_notify(ctx, 2, 'Notice', 'There are currently no announcements!')
            return
        p = EmbedPages(ctx, icon_url=self.icon_url, entries=embeds)
        await p.paginate()

    @reddit.command(name='official')
    @commands.cooldown(1, 15, commands.BucketType.user)
    @checks.cog_enabled()
    async def reddit_official(self, ctx):
        """Get official posts from Epic Games currently on the front page."""
        embeds = []
        for _, subreddit in self.subreddit.items():
            for submission in subreddit.hot():
                if str(submission.link_flair_text).upper() in ['OFFICIAL', 'EPIC RESPONSE']:
                    embeds.append(await self.build_submission_embed(submission))

        if len(embeds) == 0:
            self.bot.embed_notify(ctx, 2, 'Notice', 'There are currently no official posts!')
            return

        p = EmbedPages(ctx, icon_url=self.icon_url, entries=embeds)
        await p.paginate()

    @staticmethod
    async def build_submission_embed(submission):
        embed = discord.Embed()
        embed.title = submission.title
        embed.url = submission.shortlink
        embed.description = submission.selftext[:240] + '...'
        embed.add_field(name='Author', value=submission.author.name, inline=False)
        embed.add_field(name='Time', value=time.strftime("%a, %d %b %Y %H:%M GMT", time.gmtime(submission.created_utc)),
                        inline=False)
        return embed


class BaseModel(Model):
    class Meta:
        database = fortnite_db


class Post(BaseModel):
    id = IntegerField(primary_key=True, unique=True)
    title = CharField()
    url = CharField(null=True)  # Might be a text post
    author = CharField()
    log_id = IntegerField()  # Moderation log message ID
    approved = BooleanField(default=False)
    flair = CharField(null=True)  # Might not have a flair


def setup(bot):
    bot.add_cog(Reddit(bot))
