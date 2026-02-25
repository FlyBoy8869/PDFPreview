from PDFPreview.database.bookmark_repository import create_bookmark
from PDFPreview.models.bookmark import Bookmark

def register_bookmark(name: str, path: str, index: int):
    bookmark = Bookmark(name=name, path=path, index=index)
    return create_bookmark(bookmark.__dict__)
