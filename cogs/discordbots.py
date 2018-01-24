import aiohttp
from discord import Guild
from discord.ext import commands


class DiscordBots:
    def __init__(self, bot):
        self.bot = bot
        self.bot.scheduler.add_job(self.full_send, 'interval', hours=1)
        self.dbltoken = self.bot.config['discordbots']['token']
        self.url = "https://discordbots.org/api/bots/" + str(self.bot.user.id) + "/stats"
        self.headers = {"Authorization": self.dbltoken}

    async def send(self, guild: Guild):
        payload = {
            "server_count": len([server for server in self.bot.guilds if server.shard_id == guild.shard_id]),
            "shard_id": guild.shard_id,
            "shard_count": self.bot.shard_count
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=payload, headers=self.headers) as response:
                self.bot.logger.info(f'[DiscordBots] Returned {response.status} for {payload}')

    async def full_send(self):
        shards = [0] * self.bot.shard_count
        for guild in self.bot.guilds:
            shards[guild.shard_id] += 1

        for i in range(self.bot.shard_count):
            payload = {
                "server_count": shards[i],
                "shard_id": i,
                "shard_count": self.bot.shard_count
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, data=payload, headers=self.headers) as response:
                    self.bot.logger.info(f'[DiscordBots] Returned {response.status} for {payload}')

    async def on_ready(self):
        await self.full_send()

    async def on_guild_join(self, guild):
        await self.send(guild)

    async def on_guild_remove(self, guild):
        await self.send(guild)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def updatecount(self, ctx):
        await self.full_send()

    @commands.command(name='discordbots')
    async def discord_bots(self, ctx):
        embed = await self.bot.embed_notify(ctx, 2, 'Discord Bots Information',
                                            'Please vote for this bot on DiscordBots.org', True)
        embed.url = 'https://discordbots.org/bot/372957548451725322'
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(DiscordBots(bot))
