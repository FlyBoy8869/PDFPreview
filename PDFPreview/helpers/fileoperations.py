try:
    from os import startfile  # type: ignore  # noqa: PGH003
except ImportError:
    import webbrowser
    from collections.abc import Callable

    startfile: Callable[..., bool] = webbrowser.open_new_tab

from pathvalidate import ValidationError, validate_filename
from PySide6.QtCore import QModelIndex, Qt, QUrl
from PySide6.QtWidgets import QFileSystemModel

from PDFPreview import ADOBE_ACROBAT_PATH


def open_file(path: str) -> None:
    """Open file in the default application."""
    startfile(QUrl.fromLocalFile(path).url())


def open_with_acrobat(path: str) -> None:
    """Open file in Adobe Acrobat. Falls back to system default application if not available."""
    import subprocess

    try:
        subprocess.Popen([ADOBE_ACROBAT_PATH, "/n", path])  # noqa: S603
    except FileNotFoundError:
        # fall back to system default application
        open_file(path)

def rename_file(model: QFileSystemModel, index: QModelIndex, new_name: str) -> bool:
    if not index.isValid():
        return False

    try:
        validate_filename(new_name)
    except ValidationError as e:
        print(f"{e}\n")
        return False

    read_only_state = model.isReadOnly()
    model.setReadOnly(False)

    result = model.setData(index, new_name, Qt.ItemDataRole.EditRole)

    model.setReadOnly(read_only_state)

    return result


def delete_file(model: QFileSystemModel, index: QModelIndex) -> None:
    if not index.isValid():
        return

    if model.isDir(index):
        return

    model.remove(index)
