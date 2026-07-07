from typing import cast

from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtGui import QKeyEvent


class GlobalEventFilter(QObject):
    def __init__(self, func, parent=None):
        super().__init__(parent)
        self._func = func

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.Type.KeyPress:
            if cast("QKeyEvent", event).key() == Qt.Key.Key_AsciiTilde:
                self._func()
                return True

        return super().eventFilter(obj, event)
