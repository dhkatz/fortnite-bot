import praw, prawcore, discord, time
from config.config import __reddit__ as login
from discord.ext import commands
from util.paginator import EmbedPages


class Reddit:
    """Reddit related commands for the /r/Fortnite and /r/FortniteBR subreddits"""

    def __init__(self, bot):
        self.bot = bot
        self.instance = praw.Reddit(user_agent='Fortnite Discord Bot', client_id=login['client_id'],
                                    client_secret=login['client_secret'], username=login['username'],
                                    password=login['password'])
        self.subreddit = {'fortnite': self.instance.subreddit('fortnite'),
                          'fortnitebr': self.instance.subreddit('fortnitebr')}
        self.bot.logger.info(f'Logged into Reddit as {self.instance.user.me()}')
        self.icon_url = 'http://i.imgur.com/sdO8tAw.png'

    @commands.group()
    async def reddit(self, ctx):
        """Reddit commands. See 'help reddit'."""
        pass

    @reddit.command(name='sticky')
    @commands.cooldown(1, 15, commands.BucketType.user)
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


def setup(bot):
    bot.add_cog(Reddit(bot))