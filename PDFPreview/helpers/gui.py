# helpers.gui.py
from enum import Enum, StrEnum

from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import QPoint


class MessageType(Enum):
    QUESTION = 1
    WARNING = 2


def center_window_on_parent(*, parent: QWidget, child: QWidget) -> QPoint:
    return QPoint(
        parent.x() + ((parent.width() - child.width()) // 2),
        parent.y() + ((parent.height() - child.height()) // 2),
    )


def yes_or_no(parent: QWidget, title: str, message: str, kind: MessageType = MessageType.QUESTION) -> bool:
    return message_type_dispatch_table[kind](parent, title, message)


def _yes_or_no(parent, title: str, message: str) -> bool:
    return QMessageBox.question(
        parent,
        title,
        message
    ) == QMessageBox.StandardButton.Yes



def _warning_yes_no(parent, title: str, message: str) -> bool:
    """Display a warning message, returning True or False

    FYI, Windows automatically plays the warning sound. No need to use winsound.
    """
    return QMessageBox.warning(
        parent,
        title,
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    ) == QMessageBox.StandardButton.Yes


message_type_dispatch_table = {
    MessageType.QUESTION: _yes_or_no,
    MessageType.WARNING: _warning_yes_no,
}
