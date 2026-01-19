from pathlib import Path
from typing import cast

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QFileSystemModel, QListWidget

from PDFPreview.gui.customwidgets import MyListWidgetItem


def load_favorites(
    file: Path,
    model: QFileSystemModel,
    listwidget: QListWidget,
) -> None:
    try:
        with file.open("r", encoding="utf-8") as inputfile:
            for line in inputfile:
                display_role, extra = line.split("|")
                # make sure to strip the "extra" or else the QFileSystemModel won't find the path due to the "\n"
                item = MyListWidgetItem(
                    display_role,
                    extra=model.index(extra.strip()),
                )
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                listwidget.addItem(item)
    except FileNotFoundError:
        pass


def save_favorites(
    file: Path,
    model: QFileSystemModel,
    listwidget: QListWidget,
) -> None:
    file.touch()
    with file.open(mode="w", encoding="utf-8") as save_file:
        for row in range(listwidget.count()):
            item: MyListWidgetItem = cast(
                "MyListWidgetItem",
                listwidget.item(row),
            )
            extra: QModelIndex = item.extra
            save_file.write(
                f"{item.data(Qt.ItemDataRole.DisplayRole)}|{model.filePath(extra)}\n",
            )
