from pathlib import Path

from tinydb import TinyDB

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "Resources/Files/database.json"

db = TinyDB(DB_PATH, indent=4)
