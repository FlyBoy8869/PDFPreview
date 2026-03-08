# services.bookmark_service.py
# Business logic layer that uses repositories

from PDFPreview.database.bookmark_repository import create_bookmark, get_bookmarks, truncate_bookmarks, \
    delete_bookmark as _delete_bookmark
from PDFPreview.models.bookmark import Bookmark


def delete_bookmark(name: str) -> None:
    _delete_bookmark(name)


def load_bookmarks() -> list[Bookmark]:
    return [Bookmark(**document) for document in get_bookmarks()]


def register_bookmark(name: str, path: str, index: int):
    bookmark = Bookmark(name=name, path=path, index=index)
    return create_bookmark(bookmark.__dict__)


def update_bookmark_order(items: list[tuple[str, str, int]]) -> None:
    truncate_bookmarks()
    for item in items:
        register_bookmark(*item)
