from tinydb import TinyDB

from config import config

db = TinyDB(config.SUPPORT_PATH / "database.json", indent=4)
