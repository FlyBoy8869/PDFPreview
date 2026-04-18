# models.recent.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Recent:
    name: str
    path: str
