#!/usr/bin/env python

import asyncio
import configparser
import logging
import sys
import time
import traceback
from collections import Counter
from logging.handlers import RotatingFileHandler

import discord
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext import commands
from peewee import SqliteDatabase
from pytz import timezone

from util import context

fortnite_db = SqliteDatabase('data/fortnite.db')


async def get_prefix(client, message):
    prefixes = [client.prefix]
    if isinstance(message.channel, discord.abc.PrivateChannel):
        return commands.when_mentioned_or(*prefixes)(bot, message)
    db = client.get_cog('Database')
    guild_prefix = db.get_setting(message.guild.id, 'prefix')
    if guild_prefix.count('|'):
        prefixes = guild_prefix.split('|')
    else:
        prefixes = [guild_prefix]
    return commands.when_mentioned_or(*prefixes)(bot, message)


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.logger = set_logger()
        self.config = configparser.ConfigParser()
        self.config.read('config/config.ini')
        self.db = fortnite_db
        self.version = self.config['core']['version']
        self.scheduler = AsyncIOScheduler(timezone=timezone('US/Pacific'))
        self.counter = Counter()
        self.uptime = time.time()
        self.prefix = '.'  # Fallback prefix for DMs and default
        super().__init__(*args, command_prefix=get_prefix, **kwargs)

    @staticmethod
    async def embed_notify(ctx: commands.Context, error: int, title: str, message: str = '', raw: bool = False):
        """Create and reply Discord embeds in one line."""
        embed = discord.Embed()
        embed.title = title
        if error == 1:
            embed.colour = discord.Colour.dark_red()
        else:
            if error == 0:
                embed.colour = discord.Colour.green()
            else:
                embed.colour = discord.Colour.blue()
        embed.description = message
        # embed.set_footer(text='Fortnite', icon_url='https://i.imgur.com/HZWHuVg.png')
        if raw:
            return embed
        else:
            await ctx.send(embed=embed)


def init(bot_class=Bot):
    client = bot_class(description='Fortnite: Battle Royale stats bot.')

    @client.event
    async def on_ready():
        client.logger.info(f'[Core] Logged into Discord as {client.user.name} ({client.user.id})')
        for _, cog in client.config.items('cogs'):
            try:
                client.load_extension(cog)
            except Exception as cog_error:
                client.logger.error(f'[Core] Unable to load cog {cog}')
                client.logger.error(cog_error)
        await client.change_presence(game=discord.Game(name=f'Fortnite (Say {client.prefix}help)'))

    @client.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await client.embed_notify(ctx, 1, 'Error', 'This command cannot be used in private messages!')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(':x: This command has been disabled.')
        elif isinstance(error, commands.CommandInvokeError):
            raise error
        elif isinstance(error, commands.CommandOnCooldown):
            await client.embed_notify(ctx, 1, 'Command Cooldown',
                                      f'You\'re on cooldown! Try again in {str(error)[34:]}.')
        elif isinstance(error, commands.CheckFailure):
            await client.embed_notify(ctx, 1, 'Command Error',
                                      'You do not have permission to use this command or it has been disabled!')
        elif isinstance(error, commands.MissingRequiredArgument):
            await client.embed_notify(ctx, 1, 'Command Error', str(error))
        elif isinstance(error, commands.CommandNotFound):
            command = str(error).split('\"')[1]
            client.logger.error(f'[Core] User tried to use command ({command}) that does not exist!')
        else:
            raise error

    @client.event
    async def on_command(ctx):
        client.counter[ctx.command.name] += 1
        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            destination = 'Private Message'
        else:
            destination = f'#{ctx.channel.name} ({ctx.guild.name})'
        client.logger.info(f'[Core] {ctx.author.name} in {destination}: {ctx.message.content}')

    @client.event
    async def on_message(message: discord.Message):
        if not message.author.bot:
            await client.process_commands(message)

    @client.event
    async def process_commands(message: discord.Message):
        ctx = await client.get_context(message, cls=context.Context)
        if ctx.valid:
            await client.invoke(ctx)

    return client


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
    yield from fortnite_bot.login(fortnite_bot.config['core']['token'])
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
