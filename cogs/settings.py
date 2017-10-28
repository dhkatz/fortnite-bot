class Settings:
    def __init__(self, bot):
        self.bot = bot
        self.init()

    def init(self):
        pass


def setup(bot):
    bot.add_cog(Settings(bot))