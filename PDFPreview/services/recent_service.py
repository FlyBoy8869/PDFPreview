# services.recent_service.py
# Business logic layer that uses repositories

from PDFPreview.database.recent_repository import create_recent, get_recents, \
    delete_recent as _delete_recent
from PDFPreview.models.recent import Recent


def delete_recent(name: str) -> None:
    _delete_recent(name)


def load_recents() -> list[Recent]:
    return [Recent(**document) for document in get_recents()]


def register_recent(name: str, path: str) -> None:
    recent = Recent(name=name, path=path)
    return create_recent(recent.__dict__)
