# models.bookmark.py

from dataclasses import dataclass


@dataclass(frozen=True)
class Bookmark:
    name: str
    path: str
    index: int
