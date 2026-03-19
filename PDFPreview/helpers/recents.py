from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox

from PDFPreview.database.recent_repository import delete_recent
from PDFPreview.services.recent_service import register_recent, load_recents


class RecentsTracker:
    def __init__(self, widget: QComboBox, limit: int = 10):
        self.widget: QComboBox = widget
        self.limit = limit
        self._indexes = {}

        self._load_recents()

    def add(self, path: str) -> None:
        if path in self._indexes:
            return

        if self.widget.count() == self.limit:
            item = self.widget.itemText(0)
            delete_recent(item)
            self.widget.removeItem(0)
            
        self._add(path)
        register_recent(Path(path).resolve().name, path)

    def _add(self, path: str) -> None:
        self.widget.addItem(Path(path).resolve().name, path)
        self._indexes[path] = True

    def item_data(self, index: int) -> str:
        return self.widget.itemData(index, Qt.ItemDataRole.UserRole)

    def remove(self, recent: str) -> None:
        name: str = Path(recent).name
        for i in range(self.widget.count()):
            widget_text = self.widget.itemText(i).lower()
            if name.lower() == widget_text:
                self.widget.removeItem(i)
                self._indexes.pop(recent)
                return

    def rename(self, path: str, old_name: str, new_name: str) -> None:
        index = self.widget.findText(old_name)
        self.widget.setItemText(index, new_name)
        self.widget.setItemData(index, f"{path}/{new_name}", Qt.ItemDataRole.UserRole)

    def _load_recents(self) -> None:
        for recent in load_recents():
            self._add(recent.path)
