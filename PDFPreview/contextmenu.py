from pathlib import Path

from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QMenu, QStyle, QApplication

from PDFPreview.helpers.paths import Paths


class ContextMenu:
    def get_menu_action(self, path: Path, is_dir: bool, is_valid: bool, position) -> str:

        # if not is_valid:
        #     print("clicked in the 'dead space'...")
        #     return ""

        suffix = path.suffix

        menu: QMenu = QMenu()

        if not is_valid:
            new_menu = self._make_new_menu(menu)
            menu.addMenu(new_menu)
            return self.exec(menu, position)

        open_with: QMenu = self._make_open_with_menu(menu, suffix)
        menu.addMenu(open_with)

        new_menu: QMenu = self._make_new_menu(menu)
        menu.addMenu(new_menu)

        duplicate = self._add_action("Duplicate", "duplicate", "duplicate.png", menu)
        self._add_action("Move", "move", "move.png", menu)
        self._add_action("Rename", "rename", "rename.png", menu)
        self._add_action("Copy", "copy", "copy-to-clipboard.png", menu)

        icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_DialogDiscardButton)
        self._add_action("Delete", "delete", icon, menu)

        if is_dir:
            menu.removeAction(duplicate)

        return self.exec(menu, position)

    @staticmethod
    def exec(menu: QMenu, position) -> str:
        action = menu.exec(position)
        return action.objectName() if action is not None else ""

    def _make_new_menu(self, parent: QMenu) -> QMenu:
        menu: QMenu = QMenu("New", parent)
        menu.setIcon(QIcon(Paths.icon("plus.png")))

        self._add_action("Folder", "new_folder", "folder.png", menu)
        icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        self._add_action("Text Document", "new_text_file", icon, menu)

        return menu

    def _make_open_with_menu(self, parent: QMenu, suffix: str) -> QMenu:
        menu: QMenu = QMenu("Open With", parent)
        menu.setIcon(QIcon(Paths.icon("open_with.png")))

        if suffix.lower().replace(".", "") in ["pdf"]:
            self._add_action("Adobe Acrobat", "acrobat", "acrobat-logo.png", menu)

        self._add_action("Windows Explorer", "explorer", "explorer.png", menu)

        if suffix.lower().replace(".", "") in ["bmp", "gif", "jpg", "jpeg", "png", "svg", "webp"]:
            self._add_action("MS Paint", "paint", "palette.png", menu)

        return menu

    @staticmethod
    def _add_action(title: str, obj_name: str, icon: str | QIcon, menu: QMenu) -> QAction:
        action = menu.addAction(title)
        action.setObjectName(obj_name)
        if isinstance(icon, str):
            icon = QIcon(Paths.icon(icon))
        action.setIcon(icon)
        return action
