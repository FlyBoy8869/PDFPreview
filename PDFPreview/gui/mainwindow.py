from pathlib import Path
from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QDir, QEvent, QModelIndex, QObject, Qt, QUrl, Signal, QMimeData
from PySide6.QtGui import (
    QDragEnterEvent,
    QDropEvent,
    QKeySequence,
    QShortcut, QIcon,
)
from PySide6.QtWidgets import (
    QFileSystemModel,
    QInputDialog,
    QMainWindow,
    QMessageBox, QStyle, QFileDialog, QApplication, QAbstractItemView, QListWidgetItem
)

import PDFPreview.helpers.sound as sound
from config.config import config
from config.config import SPLASH_FILE, TITLE
from PDFPreview.gui.dialogs import about
from PDFPreview.helpers import bookmarks, fileoperations, gui
import PDFPreview.recents as recents
from PDFPreview.services.bookmark_service import update_bookmark_order, load_bookmarks
from PDFPreview.helpers.paths import Paths
import PDFPreview.effects as effects
from PDFPreview.viewer import ViewerManager

from .ui_mainwindow import Ui_MainWindow
from PDFPreview.eventfilters.about_filter import AboutDialogFilter
from PDFPreview.eventfilters.bookmark_filter import BookmarkListEventFilter
from ..contextmenu import ContextMenu
from ..helpers.gui import yes_or_no, MessageType

if TYPE_CHECKING:
    from PySide6.QtGui import QKeyEvent

# noinspection PyTypeChecker
file_filters: dict[bool, QDir.Filter] = {
    True: QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot,
    False: QDir.Filter.AllDirs
           | QDir.Filter.AllEntries
           | QDir.Filter.Drives
           | QDir.Filter.Hidden
           | QDir.Filter.NoDotAndDotDot,
}


class MainWindow(QMainWindow, Ui_MainWindow):
    # emitted when a file has been loaded in to the viewer
    fileDeleted: Signal = Signal(str)
    pathChanged: Signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(f"{TITLE}")

        self.main_splitter_state = None

        self._create_and_set_blur_effects(
            (self.gb_bookmarks, self.gb_file_browser, self.viewer, self.statusbar, self.menubar))

        self.pathChanged.connect(self._update_title_bar)

        # -----------------------------------------------------------

        self.help_shortcut = QShortcut(QKeySequence("h"), self)
        self.help_shortcut.activated.connect(self._show_help)
        self.help_save: QModelIndex | None = None

        self.wallpaper_shortcut = QShortcut(QKeySequence("Meta+`"), self)
        self.wallpaper_shortcut.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.wallpaper_shortcut.activated.connect(self._show_wallpaper)

        # ABOUT WINDOW
        self.about_window = about.create_about_dialog()
        self.about_event_filter = AboutDialogFilter(self.about_window)
        self.about_window.installEventFilter(self.about_event_filter)
        self.about_event_filter.window_closing.connect(
            lambda: effects.disable_effects(self.blur_effects)
        )
        self.actionAbout.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        )

        # Hide toolbar menu action
        self.actionHide_Toolbar.toggled.connect(self.toggle_toolbar)
        self.action_hide_files.toggled.connect(self.handle_action_hide_files)
        self.actionAbout.triggered.connect(self._show_about)

        # FILE VIEWER
        self.viewer.installEventFilter(self)
        self.viewer_manager = ViewerManager(self.viewer)
        self.viewer_manager.fileLoaded.connect(self._update_title_bar)

        # WINDOW INTO THE FILE SYSTEM
        self.model: QFileSystemModel = QFileSystemModel()
        self.model.setReadOnly(False)
        self.model.setFilter(file_filters[self.action_hide_files.isChecked()])
        root_index = self.model.setRootPath("")
        self.model.fileRenamed.connect(lambda p, o, n: self._update_title_bar(f"{p}/{n}"))
        self.top_level_index: QModelIndex = self.model.index(self.model.rootPath())

        # BOOKMARKS
        self.lw_bookmarks_event_filter: BookmarkListEventFilter = (
            BookmarkListEventFilter(self.lw_bookmarks, self.model)
        )
        self.lw_bookmarks.installEventFilter(self.lw_bookmarks_event_filter)
        self.lw_bookmarks.itemClicked.connect(self.handle_bookmark_clicked)
        self.lw_bookmarks.model().rowsMoved.connect(self._update_bookmarks)
        self.lw_bookmarks.model().dataChanged.connect(self._update_bookmarks)

        # FILE BROWSER
        self.treeView.setModel(self.model)
        self.treeView.installEventFilter(self)
        self.treeView.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        self.treeView.clicked.connect(self.handle_treeview_current_index_changed)
        self.treeView.expanded.connect(lambda index: self._update_title_bar(self.model.filePath(index)))
        self.treeView.currentIndexChanged.connect(
            lambda c, p: self.viewer_manager.view_file(Path(self.model.filePath(c)))
        )

        self.treeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(
            self.handle_treeview_context_menu_request,
        )

        for i in range(1, 4):
            self.treeView.header().hideSection(i)

        self.treeView.setRootIndex(root_index)

        # BUTTONS
        self.pb_collapse_all.setIcon(
            QIcon(Paths.icon("collapse.png"))
        )
        self.pb_collapse_all.clicked.connect(self.treeView.collapseAll)

        # RECENTS
        self.cb_recents.setToolTip("Recents")
        self.cb_recents.setMouseTracking(True)
        self.cb_recents.activated.connect(self.handle_recents_clicked)
        self.recents_manager: recents.RecentsManager = recents.RecentsManager(
            self.cb_recents,
            config["general"]["recents_limit"]
        )
        self.fileDeleted.connect(self.recents_manager.remove)
        self.model.fileRenamed.connect(self.recents_manager.rename)
        self.actionClear_Recents.triggered.connect(self.recents_manager.clear_recents)

        self._load_bookmarks()

        self.context_menu_actions = self._create_context_menu_dispatch_table()

        self._show_splash()

        self.previous_path: str = self.model.filePath(self.treeView.currentIndex())

    def close(self) -> bool:
        return super().close()

    def handle_action_hide_files(self, checked: bool) -> None:  # noqa: FBT001
        self.model.setFilter(file_filters[checked])

    def handle_bookmark_clicked(self, list_item: QListWidgetItem) -> None:
        path = Path(list_item.data(Qt.ItemDataRole.UserRole))
        index = self.model.index(str(path), 0)

        if not path.exists():
            QMessageBox.information(self, "Info", f"File no longer exists:\n\n{str(path)}")
            return

        self.viewer_manager.view_file(path)
        self.treeView.setCurrentIndex(index)

        parent = index.parent()
        while parent.isValid():
            self.treeView.expand(parent)
            parent = parent.parent()
        self.treeView.expand(index)
        self.treeView.scrollTo(self.model.index(str(path)), QAbstractItemView.ScrollHint.PositionAtTop)

        self.pathChanged.emit(str(path))

    def handle_recents_clicked(self, index: int) -> None:
        path = self.recents_manager[index]
        if not path.exists():
            self.recents_manager.remove(path.resolve().name)
            self.statusBar().showMessage(f"Recent not found: {str(path)}", 3000)
            return

        qm_index = self.model.index(str(path))
        self.treeView.setCurrentIndex(qm_index)
        self.treeView.scrollTo(qm_index, QAbstractItemView.ScrollHint.PositionAtTop)
        self.viewer_manager.view_file(path)

    def handle_treeview_current_index_changed(self, index: QModelIndex) -> None:
        if not self.model.isDir(index):
            self._add_recent(Path(self.model.filePath(index)))
        self.viewer_manager.view_file(Path(self.model.filePath(index)))

    def handle_treeview_context_menu_request(self, position) -> None:
        """Creates a dynamic menu based on the file type."""
        index: QModelIndex = self.treeView.indexAt(position)

        context_menu = ContextMenu()
        if action := context_menu.get_menu_action(
                Path(self.model.filePath(index)),
                self.model.isDir(index),
                index.isValid(),
                self.treeView.viewport().mapToGlobal(position)
        ):
            self._dispatch_action(action, index)

    def eventFilter(self, source: QObject, event: QEvent) -> bool:  # noqa: N802
        if source is self.treeView:
            if event.type() == QEvent.Type.KeyPress:
                event = cast("QKeyEvent", event)
                key = event.key()

                if key == Qt.Key.Key_Space:
                    # open selected file when the space bar is pressed
                    fileoperations.open_file(self.model.filePath(self.treeView.currentIndex()))
                    event.accept()
                    return True

        if source is self.viewer:
            if event.type() == QEvent.Type.DragEnter:
                event = cast("QDragEnterEvent", event)

                # allow drops if they have urls attached
                if (
                        event.proposedAction() == Qt.DropAction.CopyAction
                        and event.mimeData().hasUrls()
                ):
                    event.acceptProposedAction()
                    return True

                return source.eventFilter(source, event)

            # handle drops on the preview pane
            if event.type() == QEvent.Type.Drop:
                path = Path.from_uri(cast("QDropEvent", event).mimeData().urls()[0].toString())
                new_index: QModelIndex = self.model.index(str(path))

                self.treeView.setCurrentIndex(new_index)
                self.treeView.scrollTo(new_index, QAbstractItemView.ScrollHint.PositionAtTop)

                if self.model.isDir(new_index):
                    self._update_title_bar(str(path))
                else:
                    self.viewer_manager.view_file(path)

                event.accept()
                return True

        return super().eventFilter(source, event)

    def _add_recent(self, path: Path) -> None:
        self.recents_manager.add(str(path))

    def _create_and_set_blur_effects(self, widgets) -> None:
        self.blur_effects = effects.create_blur_effects(widgets)
        effects.set_blur_effects(widgets, self.blur_effects, 7)

    def _load_bookmarks(self) -> None:
        bookmarks.load_bookmarks(load_bookmarks(), self.lw_bookmarks)

    def _show_about(self) -> None:
        effects.enable_effects(self.blur_effects)

        self.about_window.move(
            gui.center_window_on_parent(parent=self, child=self.about_window),
        )
        self.about_window.show()

    def _show_help(self) -> None:
        if self.help_save is None:
            self.help_save = self.treeView.currentIndex()
            self._show_splash()
        else:
            self.viewer_manager.view_file(Path(self.model.filePath(self.help_save)))
            self.help_save = None

    def _show_splash(self) -> None:
        self.viewer_manager.view_file(SPLASH_FILE)

    def _show_wallpaper(self) -> None:
        if self.main_splitter.sizes()[0] == 0:
            self.main_splitter.restoreState(self.main_splitter_state)
        else:
            self.main_splitter_state = self.main_splitter.saveState()
            self.main_splitter.setSizes([0, 100])
            self.viewer_manager.view_file(Paths.WALLPAPER)

    def toggle_toolbar(self, checked: bool) -> None:  # noqa: FBT001
        self.viewer_manager.toggle_toolbar(checked)
        self.viewer_manager.view_file(Path(self.model.filePath(self.treeView.currentIndex())))

    def _update_bookmarks(self) -> None:
        lw = self.lw_bookmarks
        bookmarks_ = []
        for row in range(lw.count()):
            bookmarks_.append((lw.item(row).text(), lw.item(row).data(Qt.ItemDataRole.UserRole), row))

        update_bookmark_order(bookmarks_)

    def _update_title_bar(self, path: str) -> None:
        separator = " - " if path else ""
        self.setWindowTitle(f"{TITLE}{separator}{path}")

    # Context Menu Actions
    def _create_context_menu_dispatch_table(self) -> dict:
        return {
            "acrobat": self._do_acrobat_action,
            "explorer": self._do_explorer_action,
            "rename": self._do_rename_action,
            "delete": self._do_delete_action,
            "paint": self._do_paint_action,
            "duplicate": self._do_duplicate_action,
            "move": self._do_move_action,
            "new_folder": self._do_new_folder_action,
            "new_text_file": self._do_new_text_file_action,
            "copy": self._do_copy_action,
        }

    def _dispatch_action(self, action: str, index: QModelIndex) -> None:
        sound.message_beep(sound.dialog_sound)
        self.context_menu_actions[action](index)

    def _do_acrobat_action(self, index: QModelIndex) -> None:
        path = Path(self.model.filePath(index))
        if path.suffix.lower() == ".pdf":
            fileoperations.open_with_acrobat(self.model.filePath(index))

    def _do_copy_action(self, index: QModelIndex) -> None:
        mime_data = QMimeData()
        mime_data.setUrls([QUrl.fromLocalFile(self.model.filePath(index))])
        self.clipboard = QApplication.clipboard()
        self.clipboard.setMimeData(mime_data)

    def _do_delete_action(self, index: QModelIndex) -> None:
        if yes_or_no(self, "Delete",
                     f"Deleting '{self.model.fileName(index)}'.\n\nThis action can not be undone.\nAre you sure?"):
            if self.model.isDir(index):
                path = Path(self.model.filePath(index))
                result = fileoperations.delete_folder(path)
                if not result.success and result.message == "Not Empty":
                    if yes_or_no(self, "Warning", "Folder is not empty. Continue?", MessageType.WARNING):
                        result = fileoperations.delete_folder(path, recurse=True)
                        if not result.success:
                            QMessageBox.warning(self, "Warning", result.message)
                elif not result.success:
                    QMessageBox.warning(self, "Warning", result.message)
                return

            result = fileoperations.delete_file(Path(self.model.filePath(index)))
            if not result.success:
                QMessageBox.warning(self, "Warning", result.message)
                return
            self.fileDeleted.emit(self.model.filePath(index))

    def _do_duplicate_action(self, index: QModelIndex) -> None:
        result = fileoperations.duplicate_file(Path(self.model.filePath(index)))
        if not result.success:
            QMessageBox.warning(self, "Warning", result.message)

    def _do_explorer_action(self, index: QModelIndex) -> None:
        fileoperations.open_file_location(self.model.filePath(index))

    def _do_move_action(self, index: QModelIndex) -> None:
        if folder := QFileDialog.getExistingDirectory(self):
            source_path = Path(self.model.filePath(index))
            result = fileoperations.move_file(source_path, Path(folder) / source_path.name)
            if not result.success:
                QMessageBox.warning(self, "Warning", result.message)

    def _do_new_folder_action(self, index: QModelIndex) -> None:
        path = Path(self.model.filePath(index))
        path = path.parent if not path.is_dir() else path

        # Did the right-click occur in the "un-populated" area of the QTreeView?
        if not index.isValid():
            path = Path(self.model.filePath(self.treeView.currentIndex()))

        result = fileoperations.mkdir(path)
        if not result.success:
            QMessageBox.warning(self, "Warning", result.message)

    def _do_new_text_file_action(self, index: QModelIndex) -> None:
        path = Path(self.model.filePath(index))
        path = path if path.is_dir() else path.parent

        # Did the right-click occur in the "un-populated" area of the QTreeView?
        if not index.isValid():
            path = Path(self.model.filePath(self.treeView.currentIndex()))

        result = fileoperations.new_txt_file(path)
        if not result.success:
            QMessageBox.warning(self, "Warning", result.message)

    def _do_paint_action(self, index: QModelIndex) -> None:
        fileoperations.open_with_mspaint(self.model.filePath(index))

    def _do_rename_action(self, index: QModelIndex) -> None:
        # TODO: Look into filing a bug report about the return value of this method.
        if new_name := QInputDialog.getText(
                self,
                "Rename File",
                "Enter a new name for this file:",
                text=index.data(),
        )[0]:
            result = fileoperations.rename_file(self.model, index, new_name)
            if result.success:
                self._update_title_bar(self.model.filePath(self.treeView.currentIndex()))
            else:
                QMessageBox.warning(self, "Rename Failed", f"{result.message}\n\nUnable to rename this file.")
