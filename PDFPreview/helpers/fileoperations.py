# helpers.fileoperations.py
import os
import shutil
import subprocess
from contextlib import suppress
from pathlib import Path

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
        subprocess.Popen(["mspaint.exe", str(Path(path))])

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


def delete_file(model: QFileSystemModel, index: QModelIndex) -> tuple[bool, str]:
    if not index.isValid():
        return False, "Invalid Index"

    if model.isDir(index):
        try:
            shutil.rmtree(model.filePath(index))
        except (PermissionError, OSError) as e:
            return False, e.strerror

        return True, ""

    try:
        os.remove(model.filePath(index))
    except (PermissionError, OSError, FileNotFoundError) as e:
        return False, e.strerror

    return True, ""


def move_file(src: Path, dest: Path) -> tuple[bool, str]:
    try:
        src.move(dest)
    except (PermissionError, OSError) as e:
        return False, e.strerror

    return True, ""


def duplicate_file(model: QFileSystemModel, index: QModelIndex) -> tuple[bool, str]:
    if not index.isValid():
        return False, "Invalid Index"

    try:
        original_path = Path(model.filePath(index))
        unique_name = get_unique_filename(original_path)
        original_path.copy(unique_name)
    except (PermissionError, OSError) as e:
        return False, e.strerror

    return True, ""


def get_unique_filename(filename: Path | str) -> str:
    filename = Path(filename)

    if not filename.exists():
        return str(filename)

    stem = filename.stem
    suffix = filename.suffix

    new_name = f"{stem} - Copy{suffix}"
    candidate_path = filename.with_name(new_name)
    if not candidate_path.exists():
        return str(candidate_path)

    counter = 1
    while True:
        new_name = f"{stem} - Copy ({counter}){suffix}"
        candidate_path = filename.with_name(new_name)
        if not candidate_path.exists():
            return str(candidate_path)
        counter += 1
