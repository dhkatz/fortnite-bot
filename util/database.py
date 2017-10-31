from playhouse.sqlite_ext import SqliteExtDatabase, JSONField
from peewee import *

fortnite_db = SqliteExtDatabase('data/fortnite.db')


class GuildDatabase:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.db = fortnite_db

    def insert(self, guild_id):
        """Insert a new Guild into the database."""
        guild = self.bot.get_guild(guild_id)
        new_guild = Guild(uid=guild_id, name=guild.name)
        new_guild.save()

    def get(self, guild_id):
        """Get a Guild database object,"""
        try:
            guild = Guild.get(Guild.id == guild_id)
        except DoesNotExist:
            self.insert(guild_id)
            guild = Guild.get(Guild.id == guild_id)

        return guild

    def get_setting(self, guild_id, setting):
        """Get the JSON data for a specific setting."""
        try:
            guild = Guild.get(Guild.id == guild_id)
        except DoesNotExist:
            self.insert(guild_id)
            guild = Guild.get(Guild.id == guild_id)

        settings = guild.settings
        return settings[setting] if setting in settings else None

    def set_setting(self, guild_id, setting, value):
        try:
            guild = Guild.get(Guild.id == guild_id)
        except DoesNotExist:
            self.insert(guild_id)
            guild = Guild.get(Guild.id == guild_id)

        settings = guild.settings
        if setting in settings:
            settings[setting] = value
            return True
        else:
            return False


def default_settings():
    """Generate the default settings for a Guild"""
    return {'prefix': '.',
            'cogs': [{'partybus': True}, {'reddit': True}]}  # Not allowed to disable general or settings cogs


class BaseModel(Model):
    class Meta:
        database = fortnite_db


class Guild(BaseModel):
    id = CharField(unique=True, primary_key=True)
    name = CharField()
    settings = JSONField(default=default_settings)
