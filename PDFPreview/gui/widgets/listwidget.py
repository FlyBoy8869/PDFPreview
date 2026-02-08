from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QListWidgetItem


class VListWidgetItem(QListWidgetItem):
    def __init__(self, *args, extra: QModelIndex, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra: QModelIndex = extra
