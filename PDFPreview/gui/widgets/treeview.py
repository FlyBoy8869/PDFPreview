from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Signal
from PySide6.QtWidgets import QTreeView


class VTreeView(QTreeView):
    currentIndexChanged = Signal(QModelIndex, QModelIndex)  # noqa: N815

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def currentChanged(  # noqa: N802
        self,
        current: QModelIndex | QPersistentModelIndex,
        previous: QModelIndex | QPersistentModelIndex,
    ) -> None:
        self.currentIndexChanged.emit(current, previous)
        return super().currentChanged(current, previous)
