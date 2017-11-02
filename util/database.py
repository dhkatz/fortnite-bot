from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase, JSONField

fortnite_db = SqliteExtDatabase('data/fortnite.db')


class Database:
    def __init__(self, bot):
        self.bot = bot
        self.raw_db = fortnite_db
        self.init()

    def init(self):
        if 'guild' not in self.bot.db.get_tables():
            self.bot.logger.info('[Database] Created Player table in database.')
            Guild.create_table()

    def insert(self, guild_id: int):
        """Insert a new Guild into the database."""
        guild = self.bot.get_guild(guild_id)
        return Guild.create(id=guild.id, name=guild.name)

    def get(self, guild_id: int):
        """Get a Guild database object,"""
        try:
            guild = Guild.get(Guild.id == guild_id)
        except DoesNotExist:
            guild = self.insert(guild_id)

        return guild

    def get_setting(self, guild_id: int, setting: str):
        """Get the JSON data for a specific setting."""
        try:
            guild = Guild.get(Guild.id == guild_id)
        except DoesNotExist:
            guild = self.insert(guild_id)

        settings = guild.settings
        return settings[setting] if setting in settings else None

    def set_setting(self, guild_id: int, setting: str, value):
        try:
            guild = Guild.get(Guild.id == guild_id)
        except DoesNotExist:
            guild = self.insert(guild_id)

        settings = guild.settings
        if setting in settings:
            settings[setting] = value
            guild.save()
            return True
        else:
            return False

    def get_cog(self, guild_id: int, cog: str):
        cog = cog.upper()
        try:
            guild = Guild.get(Guild.id == guild_id)
        except DoesNotExist:
            guild = self.insert(guild_id)

        cogs = guild.settings['cogs']
        return cogs[cog] if cog in cogs else False  # Just return false if it somehow doesn't exist

    def set_cog(self, guild_id: int, cog: str, value: bool):
        cog = cog.upper()
        try:
            guild = Guild.get(Guild.id == guild_id)
        except DoesNotExist:
            guild = self.insert(guild_id)
        cogs = guild.settings['cogs']
        if cog in cogs:
            cogs[cog] = value
            guild.save()
            return True
        guild.save()
        return False  # Failed to set value, cog DNE or cannot be changed

    def reset(self, guild_id: int):
        try:
            guild = Guild.get(Guild.id == guild_id)
        except DoesNotExist:
            guild = self.insert(guild_id)
        guild.settings = default_settings()
        guild.save()
        return True


def default_settings():
    """Generate the default settings for a Guild"""
    return {'prefix': '.',
            'cogs': {
                'PARTYBUS': True,
                'REDDIT': True,
                'DISCORDBOTS': True
            },  # Not allowed to disable general or settings cogs
            'subscribed': True
            }


class BaseModel(Model):
    class Meta:
        database = fortnite_db


class Guild(BaseModel):
    id = IntegerField(unique=True, primary_key=True)
    name = CharField()
    settings = JSONField(default=default_settings)


def setup(bot):
    bot.add_cog(Database(bot))
