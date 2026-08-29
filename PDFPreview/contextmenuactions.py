from pathlib import Path
from typing import cast

from PySide6.QtCore import QMimeData, QUrl, QObject, Signal, QModelIndex
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QInputDialog, QMessageBox, QFileDialog, QFileSystemModel, QTreeView

from .helpers import fileoperations
from .helpers.gui import ask_yes_or_no, MessageType


class ContextMenuActions(QObject):
    fileDeleted: Signal = Signal(str)

    @staticmethod
    def do_acrobat_action(path: Path) -> None:
        if path.suffix.lower() == ".pdf":
            fileoperations.open_with_acrobat(str(path))

    @staticmethod
    def do_copy_action(path: Path, clipboard: QClipboard) -> None:
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(str(path))])
        clipboard.setMimeData(mime_data)

    def do_collapse_folder_action(self, tree_view: QTreeView, index: QModelIndex) -> None:
        """Recursively collapse all child folders."""

        if not index.isValid() or not tree_view.isExpanded(index):
            return

        model = tree_view.model()

        # Loop through all child rows of this folder index
        for row in range(model.rowCount(index)):
            child_index = model.index(row, 0, index)
            self.do_collapse_folder_action(tree_view, child_index)

        # Collapse the current folder after its children are collapsed
        tree_view.collapse(index)

    def do_delete_action(self, path: Path, tree_view: QTreeView) -> None:
        if ask_yes_or_no(None, "Delete",
                         f"Deleting '{path}'.\n\nThis action can not be undone.\nAre you sure?"):
            if path.is_dir():
                result = self._delete_folder(path, tree_view)
                if not result.success:
                    QMessageBox.warning(None, "Warning", result.message)
            else:
                if self._delete_file(path):
                    self.fileDeleted.emit(str(path))

    @staticmethod
    def do_duplicate_action(path: Path) -> None:
        result = fileoperations.duplicate_file(Path(path))
        if not result.success:
            QMessageBox.warning(None, "Warning", result.message)

    @staticmethod
    def do_explorer_action(path: Path) -> None:
        fileoperations.open_file_location(str(path))

    @staticmethod
    def do_move_action(path: Path) -> None:
        if folder := QFileDialog.getExistingDirectory():
            source_path = path
            result = fileoperations.move_file(source_path, Path(folder) / source_path.name)
            if not result.success:
                QMessageBox.warning(None, "Warning", result.message)

    @staticmethod
    def do_new_folder_action(path: Path) -> None:
        path = path.parent if not path.is_dir() else path

        result = fileoperations.mkdir(path)
        if not result.success:
            QMessageBox.warning(None, "Warning", result.message)

    @staticmethod
    def do_new_text_file_action(path: Path, text: str = "") -> None:
        path = path if path.is_dir() else path.parent

        result = fileoperations.new_txt_file(path, text)
        if not result.success:
            QMessageBox.warning(None, "Warning", result.message)

    @staticmethod
    def do_paint_action(path: Path) -> None:
        fileoperations.open_with_mspaint(str(path))

    @staticmethod
    def do_rename_action(path: Path, model: QFileSystemModel) -> None:
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

    @staticmethod
    def _delete_file(path: Path) -> bool:
        result = fileoperations.delete_file(path)
        if not result.success:
            QMessageBox.warning(None, "Warning", result.message)
            return False
        return True

    @staticmethod
    def _delete_folder(path: Path, tree_view: QTreeView) -> fileoperations.Result:
        model: QFileSystemModel = cast(QFileSystemModel, tree_view.model())
        index = model.index(str(path))

        if model.rowCount(index) == 0:
            return fileoperations.delete_folder(path)

        if not ask_yes_or_no(None, "Warning", "Folder is not empty. Continue?", MessageType.WARNING):
            return fileoperations.Result(success=True, message="")

        return fileoperations.delete_folder(path)

