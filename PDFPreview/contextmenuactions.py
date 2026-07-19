from pathlib import Path

from PySide6.QtCore import QMimeData, QUrl, QObject, Signal
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QInputDialog, QMessageBox, QFileDialog, QFileSystemModel

from helpers import fileoperations
from helpers.gui import ask_yes_or_no, MessageType


class ContextMenuActions(QObject):
    fileDeleted: Signal = Signal(str)

    def do_acrobat_action(self, path: Path) -> None:
        if path.suffix.lower() == ".pdf":
            fileoperations.open_with_acrobat(str(path))

    def do_copy_action(self, path: Path, clipboard: QClipboard) -> None:
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(path))])
        clipboard.setMimeData(mime_data)

    def do_delete_action(self, path: Path) -> None:
        if ask_yes_or_no(None, "Delete",
                     f"Deleting '{path}'.\n\nThis action can not be undone.\nAre you sure?"):
            if path.is_dir():
                self._delete_folder(path)
            else:
                if self._delete_file(path):
                    self.fileDeleted.emit(str(path))

    def do_duplicate_action(self, path: Path) -> None:
        result = fileoperations.duplicate_file(Path(path))
        if not result.success:
            QMessageBox.warning(None, "Warning", result.message)

    def do_explorer_action(self, path: Path) -> None:
        fileoperations.open_file_location(str(path))

    def do_move_action(self, path: Path) -> None:
        if folder := QFileDialog.getExistingDirectory():
            source_path = path
            result = fileoperations.move_file(source_path, Path(folder) / source_path.name)
            if not result.success:
                QMessageBox.warning(None, "Warning", result.message)

    def do_new_folder_action(self, path: Path) -> None:
        path = path.parent if not path.is_dir() else path

        result = fileoperations.mkdir(path)
        if not result.success:
            QMessageBox.warning(None, "Warning", result.message)

    def do_new_text_file_action(self, path: Path) -> None:
        path = path if path.is_dir() else path.parent

        result = fileoperations.new_txt_file(path)
        if not result.success:
            QMessageBox.warning(None, "Warning", result.message)

    def do_paint_action(self, path: Path) -> None:
        fileoperations.open_with_mspaint(str(path))

    def do_rename_action(self, path: Path, model: QFileSystemModel) -> None:
        # TODO: Look into filing a bug report about the return value of this method.
        if new_name := QInputDialog.getText(
                None,
                "Rename File",
                "Enter a new name for this file:",
                text=path.name,
        )[0]:
            result = fileoperations.rename_file(model, model.index(str(path)), new_name)
            if not result.success:
                QMessageBox.warning(None, "Rename Failed", f"{result.message}\n\nUnable to rename this file.")

    def _delete_file(self, path: Path) -> bool:
        result = fileoperations.delete_file(path)
        if not result.success:
            QMessageBox.warning(None, "Warning", result.message)
            return False
        return True

    def _delete_folder(self, path: Path) -> bool:
        result = fileoperations.delete_folder(path)
        if result.success:
            return True

        # what went wrong, folder not empty?
        if result.message == "Not Empty":
            if ask_yes_or_no(None, "Warning", "Folder is not empty. Continue?", MessageType.WARNING):
                # retry, recursively deleting everything inside the folder
                result = fileoperations.delete_folder(path, recurse=True)
                if result.success:
                    return True
                # Nope still fails, something else must be causing the failure
                QMessageBox.warning(None, "Warning", result.message)
                return False
        # no, non-empty folder wasn't the problem
        else:
            QMessageBox.warning(None, "Warning", result.message)
        return False

