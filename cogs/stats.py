from datetime import datetime, timedelta
from urllib.parse import quote

import aiohttp
import discord
from discord.ext import commands
from peewee import *

from bot import fortnite_db
from util import checks


class Stats:
    """Stats on weapons and chests."""

    def __init__(self, bot):
        self.bot = bot
        self.init()

    def init(self):
        if 'weapon' not in self.bot.db.get_tables():
            self.bot.logger.info('[Stats] Created Weapon table in database.')
            Weapon.create_table()

        if 'chest' not in self.bot.db.get_tables():
            self.bot.logger.info('[Stats] Created Chest table in database.')
            Weapon.create_table()


class BaseModel(Model):
    class Meta:
        database = fortnite_db


class Weapon(BaseModel):
    type = CharField()
    name = CharField()
    rarity = CharField()
    dps = FloatField()
    damage = FloatField()
    fire_rate = FloatField()
    mag_size = IntegerField()
    range = FloatField()
    reload = FloatField()
    ammo_cost = IntegerField()
    impact = IntegerField()


def setup(bot):
    bot.add_cog(Stats(bot))