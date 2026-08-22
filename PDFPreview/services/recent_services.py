# services.recent_services.py
# Business logic layer that uses repositories

import PDFPreview.database.recent_repository as recent_repository
from PDFPreview.models.recent import Recent


def clear_recents() -> None:
    recent_repository.truncate_recents()


def delete_recent(path: str) -> None:
    recent_repository.delete_recent(path)


def load_recents() -> list[Recent]:
    return [Recent(**document) for document in recent_repository.get_recents()]


def register_recent(name: str, path: str) -> None:
    recent = Recent(name=name, path=path)
    recent_repository.create_recent(recent.__dict__)
