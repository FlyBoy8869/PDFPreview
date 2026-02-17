from pathlib import Path
from typing import cast

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QFileSystemModel, QListWidget

from PDFPreview.gui.widgets.listwidget import VListWidgetItem


def load_favorites_to(
    *,
    dest: QListWidget,
    file_path: Path,
    model: QFileSystemModel,
) -> None:
    try:
        with file_path.open("r", encoding="utf-8") as inputfile:
            for line in inputfile:
                favorite_text, path = line.split("|")
                # make sure to strip the "extra" or else the QFileSystemModel won't find the path due to the "\n"
                item = VListWidgetItem(
                    favorite_text,
                    extra=model.index(path.strip()),
                )
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                dest.addItem(item)
    except FileNotFoundError:
        pass


def save_favorites_from(
    *,
    source: QListWidget,
    file_path: Path,
    model: QFileSystemModel,
) -> None:
    file_path.touch()
    with file_path.open(mode="w", encoding="utf-8") as save_file:
        for row in range(source.count()):
            item: VListWidgetItem = cast(
                "VListWidgetItem",
                source.item(row),
            )
            extra: QModelIndex = item.extra
            save_file.write(
                f"{item.data(Qt.ItemDataRole.DisplayRole)}|{model.filePath(extra)}\n",
            )
