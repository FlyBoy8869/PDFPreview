from pathlib import Path

from tinydb import TinyDB
from config.config import config

DB_PATH = Path(config["paths"]["database"]) / "database.json"

db = TinyDB(DB_PATH, indent=4)
