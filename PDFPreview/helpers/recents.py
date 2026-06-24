from pathlib import Path

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QComboBox

from PDFPreview.services.recent_service import (
    register_recent, load_recents, delete_recent,
    clear_recents as _clear_recents
)


class RecentsManager:
    def __init__(self, widget: QComboBox, limit: int = 10):
        self.widget: QComboBox = widget
        self.limit = limit
        self._indexes = {}

        self._load_recents()

    def add(self, path: str) -> None:
        if path in self._indexes:
            return

        if self.widget.count() >= self.limit:
            item = self.widget.itemText(0)
            delete_recent(item)
            self.widget.removeItem(0)

        self._add(path)

        # add to database
        register_recent(Path(path).resolve().name, path)

    def _add(self, path: str) -> None:
        self.widget.addItem(Path(path).resolve().name, path)
        self.widget.setItemData(self.widget.count() - 1, str(Path(path)), Qt.ItemDataRole.ToolTipRole)
        self._indexes[path] = True

    @Slot()
    def clear_recents(self) -> None:
        self.widget.clear()
        self._indexes = {}
        _clear_recents()

    def item_data(self, index: int) -> Path:
        return Path(self.widget.itemData(index, Qt.ItemDataRole.UserRole)).resolve()

    def __getitem__(self, index: int) -> Path:
        return Path(self.widget.itemData(index, Qt.ItemDataRole.UserRole)).resolve()

    @Slot()
    def remove(self, recent: str) -> None:
        name: str = Path(recent).name
        for i in range(self.widget.count()):
            widget_text = self.widget.itemText(i).lower()
            if name.lower() == widget_text:
                self.widget.removeItem(i)
                try:
                    self._indexes.pop(recent)
                except KeyError:
                    pass
                return

    @Slot()
    def rename(self, path: str, old_name: str, new_name: str) -> None:
        index = self.widget.findText(old_name)
        self.widget.setItemText(index, new_name)
        self.widget.setItemData(index, f"{path}/{new_name}", Qt.ItemDataRole.UserRole)

    def _load_recents(self) -> None:
        recents = load_recents()

        if len(recents) > self.limit:
            remove_count = len(recents) - self.limit
            for i in range(remove_count):
                r = recents.pop(0)
                delete_recent(r.name)

        for recent in load_recents():
            if not Path(recent.path).exists():
                delete_recent(recent.name)
                continue
            self._add(recent.path)
