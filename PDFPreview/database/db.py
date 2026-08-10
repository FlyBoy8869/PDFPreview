from tinydb import TinyDB

from config import DATABASE_PATH

db = TinyDB(DATABASE_PATH / "database.json", indent=4)
