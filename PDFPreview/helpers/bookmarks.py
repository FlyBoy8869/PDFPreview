# helpers.bookmarks.py
from pathlib import Path

from PySide6.QtCore import Qt

from PDFPreview.gui.widgets.listwidget import VListWidgetItem
from PDFPreview.models.bookmark import Bookmark

from PySide6.QtWidgets import QFileSystemModel, QListWidget, QListWidgetItem

from PDFPreview.services.bookmark_service import delete_bookmark


def load_bookmarks(bookmarks: list[Bookmark], list_widget: QListWidget, model: QFileSystemModel) -> None:
    for bookmark in bookmarks:
        if not Path(bookmark.path).exists():
            delete_bookmark(bookmark.name)
            continue

        item = QListWidgetItem(bookmark.name)
        item.setData(Qt.ItemDataRole.UserRole, bookmark.path)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        list_widget.addItem(item)
