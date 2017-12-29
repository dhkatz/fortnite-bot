import aiohttp
from discord.ext import commands


class DiscordBots:
    def __init__(self, bot):
        self.bot = bot
        self.bot.scheduler.add_job(self.send, 'interval', hours=1)
        self.dbltoken = self.bot.config['discordbots']['token']
        self.url = "https://discordbots.org/api/bots/" + str(self.bot.user.id) + "/stats"
        self.headers = {"Authorization": self.dbltoken}

    async def send(self):
        payload = {"server_count": len(self.bot.guilds)}
        async with aiohttp.ClientSession() as aioclient:
            async with aioclient.post(self.url, data=payload, headers=self.headers) as resp:
                self.bot.logger.info('[DiscordBots] Returned {0.status} for {1}'.format(resp, payload))

    async def on_ready(self):
        await self.send()

    async def on_guild_join(self, guild):
        await self.send()

    async def on_guild_remove(self, guild):
        await self.send()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def updatecount(self, ctx):
        await self.send()

    @commands.command(name='discordbots')
    async def discord_bots(self, ctx):
        embed = await self.bot.embed_notify(ctx, 2, 'Discord Bots Information',
                                            'Please vote for this bot on DiscordBots.org', True)
        embed.url = 'https://discordbots.org/bot/372957548451725322'
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DiscordBots(bot))
