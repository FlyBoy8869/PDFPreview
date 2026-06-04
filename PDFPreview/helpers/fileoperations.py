# helpers.fileoperations.py
import os
import shutil
import subprocess
from collections import namedtuple
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


Result = namedtuple("Result", ["success", "message"])


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

def rename_file(model: QFileSystemModel, index: QModelIndex, new_name: str) -> Result:
    if not index.isValid():
        return Result(False, "Invalid Index")

    try:
        validate_filename(new_name)
    except ValidationError as e:
        return Result(False, f"{e.reason.description.upper()}\n\n'{new_name}' is an invalid file name.")

    result = model.setData(index, new_name, Qt.ItemDataRole.EditRole)

    return Result(result, "")


def delete_file(path: Path) -> Result:
    try:
        os.remove(str(path))
    except (PermissionError, OSError, FileNotFoundError) as e:
        return Result(False, e.strerror)

    return Result(True, "")


def delete_folder(path: Path, recurse: bool = False) -> Result:
    def has_files() -> bool:
        try:
            next(path.glob("*"))
            return True
        except StopIteration:
            return False

    if has_files() and not recurse:
        return Result(False, "Not Empty")

    try:
        folder = QDir(path)
        success = folder.removeRecursively()
        if not success:
            # need to get reason for failure since QDir.removeRecursively doesn't give one
            path.rmdir()
    except (PermissionError, OSError) as e:
        return Result(False, e.strerror)

    return Result(True, "")


def move_file(src: Path, dest: Path) -> Result:
    try:
        src.move(dest)
    except (PermissionError, OSError) as e:
        return Result(False, e.strerror)

    return Result(True, "")


def mkdir(path: Path) -> Result:
    try:
        unique_name = get_unique_filename(path / "New Folder")
        Path(unique_name).mkdir(parents=True, mode=0o777)
    except (PermissionError, OSError, FileExistsError) as e:
        return Result(False, e.strerror)

    return Result(True, "")


def duplicate_file(path: Path) -> Result:
    try:
        unique_name = get_unique_filename(path)
        path.copy(unique_name)
    except (PermissionError, OSError) as e:
        return Result(False, e.strerror)

    return Result(True, "")


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
