from pathlib import Path
from typing import cast

from PySide6.QtCore import QObject, QEvent, QModelIndex, Qt
from PySide6.QtWidgets import QAbstractItemView, QTreeView, QFileSystemModel
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from PDFPreview.viewer import ViewerManager


class ViewerFilter(QObject):
    def __init__(self, model: QFileSystemModel, file_browser: QTreeView, viewer_manager: ViewerManager):
        super().__init__()
        self.model = model
        self.file_browser = file_browser
        self.viewer_manager = viewer_manager

    def eventFilter(self, source: QObject, event: QEvent):
        if event.type() == QEvent.Type.DragEnter:
            event = cast("QDragEnterEvent", event)

            # allow drops if they have urls attached
            if (
                event.proposedAction() == Qt.DropAction.CopyAction
                and event.mimeData().hasUrls()
            ):
                event.acceptProposedAction()
                return True

            return source.eventFilter(source, event)

        # handle drops on the preview pane
        if event.type() == QEvent.Type.Drop:
            path = Path.from_uri(cast("QDropEvent", event).mimeData().urls()[0].toString())
            new_index: QModelIndex = self.model.index(str(path))

            self.file_browser.setCurrentIndex(new_index)
            self.file_browser.scrollTo(new_index, QAbstractItemView.ScrollHint.PositionAtTop)

            self.viewer_manager.preview_file(path)

            event.accept()
            return True

        return super().eventFilter(source, event)
