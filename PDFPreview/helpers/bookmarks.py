from PySide6.QtCore import Qt

from PDFPreview.gui.widgets.listwidget import VListWidgetItem
from PDFPreview.models.bookmark import Bookmark

from PySide6.QtWidgets import QFileSystemModel


def load_bookmarks(bookmarks: list[Bookmark], list_widget, model: QFileSystemModel) -> None:
    for bookmark in bookmarks:
        item = VListWidgetItem(
            bookmark.name,
            extra=model.index(bookmark.path)
        )
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        list_widget.addItem(item)
