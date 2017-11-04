import json

import aiohttp
from discord.ext import commands

import config.config as config


class DiscordBots:
    def __init__(self, bot):
        self.bot = bot
        self.bot.scheduler.add_job(self.send, 'interval', hours=1)

    async def send(self):
        dump = json.dumps({
            'server_count': len(self.bot.guilds)
        })
        head = {
            'authorization': config.__dbl__['token'],
            'content-type': 'application/json'
        }

        url = 'https://discordbots.org/api/bots/{0}/stats'.format(config.__dbl__['id'])
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=dump, headers=head) as resp:
                self.bot.logger.info('[DiscordBots] Returned {0.status} for {1}'.format(resp, dump))

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
