import platform
from typing import TYPE_CHECKING, Literal, cast

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QFileSystemModel, QListWidget

from PDFPreview.gui.widgets.listwidget import VListWidgetItem
from PDFPreview.services.bookmark_service import register_bookmark, delete_bookmark

if TYPE_CHECKING:
    from PySide6.QtGui import QDragEnterEvent, QDropEvent, QKeyEvent
    from PySide6.QtWidgets import QDialog, QListWidgetItem

PATH_PREFIX: Literal["file://", "file:///"] = (
    "file://" if "macOS" in platform.platform() else "file:///"
)


class AboutDialogFilter(QObject):
    def __init__(self, source):
        self.source = source
        super().__init__()

    def eventFilter(self, source: QObject, event: QEvent) -> bool:  # noqa: N802
        source = cast("QDialog", source)
        if (
                event.type() == QEvent.Type.MouseButtonRelease
                or event.type() == QEvent.Type.KeyRelease
        ):
            self.source.close()
            event.accept()
            return event.isAccepted()

        return False


class BookmarkListEventFilter(QObject):
    def __init__(self, source: QListWidget, model: QFileSystemModel):
        super().__init__()
        self.source: QListWidget = source
        self.model: QFileSystemModel = model

    def eventFilter(self, source: QObject, event: QEvent) -> bool:  # noqa: N802
        source = cast("QListWidget", source)
        if event.type() == QEvent.Type.DragEnter:
            print("processing drag enter event")
            event = cast("QDragEnterEvent", event)
            if (
                    event.proposedAction() == Qt.DropAction.CopyAction
                    and event.mimeData().hasText()
            ):
                event.acceptProposedAction()
                return event.isAccepted()
            event.ignore()

        if event.type() == QEvent.Type.Drop:
            print("processing drop event")
            path: str = (
                cast("QDropEvent", event).mimeData().text().replace(PATH_PREFIX, "")
            )
            favorites_text: str = self.model.fileName(self.model.index(path))
            item = VListWidgetItem(favorites_text, extra=self.model.index(path))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            source.addItem(item)

            register_bookmark(name=favorites_text, path=path, index=source.count() - 1)
            print("created bookmark")

            event.accept()
            return event.isAccepted()

        if (
                event.type() == QEvent.Type.KeyPress
                and cast("QKeyEvent", event).key() == Qt.Key.Key_Delete
        ):
            item: QListWidgetItem = source.currentItem()
            name = item.text()
            source.takeItem(source.row(item))
            delete_bookmark(name)
            event.accept()
            return event.isAccepted()

        return super().eventFilter(source, event)
