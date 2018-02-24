from peewee import *

from bot import fortnite_db
from util.validator import VideoValidator, UserValidator


class Moderation:
    """Moderation actions for moderators of /r/FortniteBR and /r/Fortnite"""

    def __init__(self, bot):
        self.bot = bot
        self.log = self.bot.logger
        self.reddit = bot.get_cog('Reddit')
        self.reddit = self.reddit.instance
        self.video_validator, self.user_validator = None, None
        self.domains = self.bot.config['domains']
        self.setup()

    def setup(self):
        self._create_db()
        self.video_validator = VideoValidator(limit=60)
        self.user_validator = UserValidator('fortnitebr', threshold=10)
        # self.bot.scheduler.add_job(self.process_posts, 'interval', seconds=30)
        self.bot.scheduler.add_job(self.process_reports, 'interval', seconds=60)

    def _create_db(self):
        if 'post' not in self.bot.db.get_tables():
            self.bot.logger.info('[Reddit] Created Post table in database.')
            Post.create_table()

        if 'watchedpost' not in self.bot.db.get_tables():
            self.bot.logger.info('[Reddit] Created WatchedPost table in database.')
            WatchedPost.create_table()

    async def process_posts(self):
        for post in self.reddit.subreddit('fortnitebr').mod.unmoderated():
            if post.is_self:
                continue
            elif any(host in post.url for host in self.domains['approved'].split(',')):
                self.log.info(f'Post would have been approved! {post.url} ({post.shortlink})')
                # post.mod.approve()
            elif any(host in post.url for host in self.domains['rejected'].split(',')):
                self.log.info(f'Post would have been rejected! {post.url} ({post.shortlink})')
            elif any(host in post.url for host in self.domains['watched'].split(',')):
                if self.video_validator.validate(post.url) and self.user_validator.validate(post.author):
                    self.log.info(f'Post would have been approved! {post.url} ({post.shortlink})')
                else:
                    self.log.info(f'Post would have been rejected! {post.url} ({post.shortlink})')
            elif any(host in post.url for host in self.domains['reported'].split(',')):
                self.log.info(f'Post would have been reported! {post.url} ({post.shortlink})')

    def process_reports(self):
        for report in self.reddit.subreddit('fortnitebr').mod.reports():
            print("User Reports: {}".format(report.user_reports))
            print("Mod Reports: {}".format(report.mod_reports))

    def approve_post(self, post):
        pass

    def remove_post(self, post):
        pass


class BaseModel(Model):
    class Meta:
        database = fortnite_db


class Post(BaseModel):
    id = IntegerField(primary_key=True, unique=True)
    subreddit = CharField()
    title = CharField()
    flair = CharField(null=True)  # Might not have a flair
    url = CharField(null=True)  # Might be a text post
    author = CharField()
    log_id = IntegerField()  # Moderation log message ID
    votes = IntegerField()
    approved = BooleanField(default=False)


class WatchedPost(BaseModel):
    """Post's votes and other information gets updated."""
    post = ForeignKeyField(Post, primary_key=True)


def setup(bot):
    bot.add_cog(Moderation(bot))
