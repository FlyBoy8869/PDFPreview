from tinydb import TinyDB

from config import SUPPORT_PATH

db = TinyDB(SUPPORT_PATH / "database.json", indent=4)
