#!/usr/bin/env python

import asyncio
import logging
import sys
import traceback
import time
from logging.handlers import RotatingFileHandler

import discord
from discord.ext import commands
from peewee import SqliteDatabase
from collections import Counter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

import config.config as config

fortnite_db = SqliteDatabase('data/fortnite.db')


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.logger = set_logger()
        self.db = fortnite_db
        self.version = config.__version__
        self.scheduler = AsyncIOScheduler(timezone=timezone('US/Pacific'))
        self.counter = Counter()
        self.uptime = time.time()
        self.prefix = '.'
        super().__init__(*args, command_prefix=commands.when_mentioned_or(self.prefix), **kwargs)

    @staticmethod
    async def embed_notify(ctx: commands.Context, error: int, title: str, message: str, raw: bool = False):
        """Create and reply Discord embeds in one line."""
        embed = discord.Embed()
        embed.title = title
        embed.colour = discord.Colour.dark_red() if error == 1 else discord.Colour.green() if error == 0 else discord.Colour.blue()
        embed.description = message
        # embed.set_footer(text='Fortnite', icon_url='https://i.imgur.com/HZWHuVg.png')
        if raw:
            return embed
        else:
            await ctx.send(embed=embed)


def init(bot_class=Bot):
    bot = bot_class(description='Fortnite: Battle Royale stats bot.')

    @bot.event
    async def on_ready():
        bot.logger.info(f'[Core] Logged into Discord as {bot.user.name} ({bot.user.id})')
        for cog in config.__cogs__:
            try:
                bot.load_extension(cog)
            except Exception as cog_error:
                bot.logger.error(f'[Core] Unable to load cog {cog}')
                bot.logger.error(cog_error)
        await bot.change_presence(game=discord.Game(name='Fortnite (Say ' + bot.prefix + 'help)'))

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await bot.embed_notify(ctx, 1, 'Error', 'This command cannot be used in private messages!')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(':x: This command has been disabled.')
        elif isinstance(error, commands.CommandInvokeError):
            raise error
        elif isinstance(error, commands.CommandOnCooldown):
            await bot.embed_notify(ctx, 1, 'Command Cooldown', f'You\'re on cooldown! Try again in {str(error)[34:]}.')
        elif isinstance(error, commands.CheckFailure):
            await bot.embed_notify(ctx, 1, 'Command Error', 'You do not have permission to use this command!')
        elif isinstance(error, commands.CommandNotFound):
            command = str(error).split('\"')[1]
            bot.logger.error(f'[Core] User tried to use command ({command}) that does not exist!')
        else:
            raise error

    @bot.event
    async def on_command(ctx):
        bot.counter[ctx.command.name] += 1
        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            destination = 'Private Message'
        else:
            destination = f'#{ctx.channel.name} ({ctx.guild.name})'
        bot.logger.info(f'[Core] {ctx.author.name} in {destination}: {ctx.message.content}')

    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return
        await bot.process_commands(message)

    return bot


def set_logger():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    log_format = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(log_format)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    fh = RotatingFileHandler(filename='data/discordbot.log', maxBytes=1024 * 5, backupCount=2, encoding='utf-8',
                             mode='w')
    fh.setFormatter(log_format)
    logger.addHandler(fh)

    return logger


def main(fortnite_bot: Bot):
    yield from fortnite_bot.login(config.__token__)
    yield from fortnite_bot.connect()


if __name__ == '__main__':
    bot = init()
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main(bot))
    except discord.LoginFailure:
        bot.logger.error(traceback.format_exc())
    except Exception as e:
        bot.logger.exception('[Core] Fatal exception, attempting graceful logout.', exc_info=e)
        loop.run_until_complete(bot.logout())
    finally:
        loop.close()
        exit(0)
