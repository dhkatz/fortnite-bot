from discord.ext import commands


class Context(commands.Context):
    """Custom context class in which a command is being invoked under."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def db(self):
        return self.bot.get_cog('Database')
