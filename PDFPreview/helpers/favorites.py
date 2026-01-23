from pathlib import Path
from typing import cast

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QFileSystemModel, QListWidget

from PDFPreview.gui.customwidgets import MyListWidgetItem


def load_favorites_to(
    *,
    widget: QListWidget,
    from_file_path: Path,
    using_model: QFileSystemModel,
) -> None:
    try:
        with from_file_path.open("r", encoding="utf-8") as inputfile:
            for line in inputfile:
                display_role, extra = line.split("|")
                # make sure to strip the "extra" or else the QFileSystemModel won't find the path due to the "\n"
                item = MyListWidgetItem(
                    display_role,
                    extra=using_model.index(extra.strip()),
                )
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                widget.addItem(item)
    except FileNotFoundError:
        pass


def save_favorites_from(
    *,
    widget: QListWidget,
    to_file_path: Path,
    using_model: QFileSystemModel,
) -> None:
    to_file_path.touch()
    with to_file_path.open(mode="w", encoding="utf-8") as save_file:
        for row in range(widget.count()):
            item: MyListWidgetItem = cast(
                "MyListWidgetItem",
                widget.item(row),
            )
            extra: QModelIndex = item.extra
            save_file.write(
                f"{item.data(Qt.ItemDataRole.DisplayRole)}|{using_model.filePath(extra)}\n",
            )
