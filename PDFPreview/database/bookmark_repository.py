from tinydb import Query
from tinydb.table import Document

from .db import db

bookmarks_table = db.table(name="bookmarks")
BookmarkQuery = Query()

def create_bookmark(bookmark_dict: dict):
    return bookmarks_table.insert(bookmark_dict)

def get_bookmarks() -> list[Document]:
    return bookmarks_table.all()
