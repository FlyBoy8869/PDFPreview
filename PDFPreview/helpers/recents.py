from pathlib import Path

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QComboBox


class RecentsTracker:
    def __init__(self, widget: QComboBox, limit: int = 10):
        self.widget: QComboBox = widget
        self.limit = limit
        self._indexes = {}

    def add(self, path: str) -> None:
        if path in self._indexes:
            return

        if self.widget.count() == self.limit:
            self.widget.removeItem(0)
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
