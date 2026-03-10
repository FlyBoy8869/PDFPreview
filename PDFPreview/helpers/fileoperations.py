# helpers.fileoperations.py

import subprocess
from contextlib import suppress

try:
    from os import startfile  # type: ignore  # noqa: PGH003
except ImportError:
    import webbrowser
    from collections.abc import Callable

    startfile: Callable[..., bool] = webbrowser.open_new_tab

from pathvalidate import ValidationError, validate_filename
from PySide6.QtCore import QModelIndex, Qt, QUrl, QDir
from PySide6.QtWidgets import QFileSystemModel

from config.config import ADOBE_ACROBAT_PATH


def open_file(path: str) -> None:
    """Open file in the default application."""
    startfile(QUrl.fromLocalFile(path).url())


def open_with_acrobat(path: str) -> None:
    """Open file in Adobe Acrobat. Falls back to system default application if not available."""
    try:
        subprocess.Popen([ADOBE_ACROBAT_PATH, "/n", path])  # noqa: S603
    except FileNotFoundError:
        # fall back to system default application
        open_file(path)


def open_file_location(path: str) -> None:
    with suppress(FileNotFoundError):
        subprocess.Popen(f'explorer.exe /select,"{path.replace("/", "\\")}"')


def open_with_mspaint(path: str) -> None:
    with suppress(FileNotFoundError):
        subprocess.Popen(
            ["mspaint.exe", f"{path.replace("/", "\\")}"]
        )


def rename_file(model: QFileSystemModel, index: QModelIndex, new_name: str) -> bool:
    if not index.isValid():
        return False

    try:
        validate_filename(new_name)
    except ValidationError as e:
        print(f"{e}\n")
        return False

    result = model.setData(index, new_name, Qt.ItemDataRole.EditRole)

    return result


def delete_file(model: QFileSystemModel, index: QModelIndex) -> None:
    if not index.isValid():
        return

    if model.isDir(index):
        return

    model.remove(index)


def delete_directory(model: QFileSystemModel, index: QModelIndex) -> None:
    if not index.isValid():
        return

    dir_ = QDir(model.filePath(index))
    dir_.removeRecursively()
