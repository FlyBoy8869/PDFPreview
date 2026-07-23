# database.recent_repository.py
# handles the CRUD operations

from tinydb import Query

from .db import db

recents_table = db.table(name="recents")
RecentQuery = Query()


def create_recent(recent_dict: dict):
    return recents_table.insert(recent_dict)


def get_recents() -> list[dict[str, str]]:
    return recents_table.all()


def delete_recent(path: str) -> None:
    recents_table.remove(RecentQuery.path == path)


def truncate_recents() -> None:
    recents_table.truncate()
