# database.recent_repository.py
# handles the CRUD operations

from tinydb import Query
from tinydb.table import Document

from .db import db

recents_table = db.table(name="recents")
RecentQuery = Query()


def create_recent(recent_dict: dict):
    return recents_table.insert(recent_dict)


def get_recents() -> list[Document]:
    return recents_table.all()


def delete_recent(name: str) -> None:
    recents_table.remove(RecentQuery.name == name)
