from playhouse.sqlite_ext import SqliteExtDatabase

class Database(SqliteExtDatabase):
    def __init__(self, bot, config):
        self.config = config
        super().__init__(self.config)