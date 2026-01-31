import platform
from typing import cast
from PySide6.QtCore import QObject, QEvent, Qt

from PDFPreview.gui.customwidgets import MyListWidgetItem

PATH_PREFIX = "file://" if "macOS" in platform.platform() else "file:///"


class AboutDialogFilter(QObject):
    def __init__(self, source):
        self.source = source
        super().__init__()

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if source is self.source and (
            event.type() == QEvent.Type.MouseButtonRelease
            or event.type() == QEvent.Type.KeyRelease
        ):
            self.source.close()
            event.accept()
            return event.isAccepted()
        
        return False


class FavoritesListFilter(QObject):
    def __init__(self, source, model):
        super().__init__()
        self.source = source
        self.model = model

    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.DragEnter:
                    event = cast("QDragEnterEvent", event)
                    if (
                        event.proposedAction() == Qt.DropAction.CopyAction
                        and event.mimeData().hasText()
                    ):
                        event.acceptProposedAction()
                        return event.isAccepted()
                    event.ignore()

        if event.type() == QEvent.Type.Drop:
            path = (
                cast("QDropEvent", event).mimeData().text().replace(PATH_PREFIX, "")
            )
            favorites_text: str = self.model.fileName(self.model.index(path))
            item = MyListWidgetItem(favorites_text, extra=self.model.index(path))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            source.addItem(item)

            event.accept()
            return event.isAccepted()

        if (
            event.type() == QEvent.Type.KeyPress
            and cast("QKeyEvent", event).key() == Qt.Key.Key_Delete
        ):
            item = source.currentItem()
            source.takeItem(source.row(item))
            event.accept()
            return event.isAccepted()
        
        return super().eventFilter(source, event)
