import os
from pathlib import Path

from tinydb import TinyDB

_path = Path(os.path.expandvars(Path("%APPDATA%/FileViewer")))
if not _path.exists():
    _path.mkdir(parents=True)

DB_PATH = _path / "database.json"

db = TinyDB(DB_PATH, indent=4)
