from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QPoint


def center_window_on_parent(*, parent: QWidget, child: QWidget) -> QPoint:
    return QPoint(
        parent.x() + ((parent.width() - child.width()) // 2),
        parent.y() + ((parent.height() - child.height()) // 2),
    )
