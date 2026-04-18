from tinydb import TinyDB

from config import config

db = TinyDB(config.DATABASE_PATH / "database.json", indent=4)
