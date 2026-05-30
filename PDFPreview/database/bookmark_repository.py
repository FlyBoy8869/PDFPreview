# database.bookmark_repository.py
# handles the CRUD operations

from tinydb import Query
from tinydb.table import Document

from .db import db

bookmarks_table = db.table(name="bookmarks")
BookmarkQuery = Query()


def create_bookmark(bookmark_dict: dict):
    return bookmarks_table.insert(bookmark_dict)


def get_bookmarks() -> list[Document]:
    return bookmarks_table.all()


def truncate_bookmarks() -> None:
    bookmarks_table.truncate()


def delete_bookmark(name: str) -> None:
    bookmarks_table.remove(BookmarkQuery.name == name)
