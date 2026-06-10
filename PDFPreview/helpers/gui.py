# helpers.gui.py

from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import QPoint


def center_window_on_parent(*, parent: QWidget, child: QWidget) -> QPoint:
    return QPoint(
        parent.x() + ((parent.width() - child.width()) // 2),
        parent.y() + ((parent.height() - child.height()) // 2),
    )


def yes_or_no(parent, title: str, message: str) -> bool:
    return QMessageBox.question(
        parent,
        title,
        message
    ) == QMessageBox.StandardButton.Yes
