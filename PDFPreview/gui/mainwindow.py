from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QDir, QEvent, QModelIndex, QObject, Qt, QUrl, Signal
from PySide6.QtGui import (
    QAction,
    QDragEnterEvent,
    QDropEvent,
    QKeySequence,
    QShortcut, QIcon,
)
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWidgets import (
    QFileSystemModel,
    QInputDialog,
    QMainWindow,
    QMenu,
    QMessageBox, QStyle, QGraphicsBlurEffect, QFileDialog
)

# import config.config
from config.config import config
from config.config import SPLASH_FILE, TITLE, IMAGES
from PDFPreview.gui.dialogs import about
from PDFPreview.helpers import bookmarks, fileoperations, gui, recents
from PDFPreview.services.bookmark_service import update_bookmark_order, load_bookmarks

from .ui_mainwindow import Ui_MainWindow
from PDFPreview.eventfilters.about_eventfilter import AboutDialogFilter
from PDFPreview.eventfilters.bookmark_eventfilter import BookmarkListEventFilter
from ..services.recent_service import delete_recent

if TYPE_CHECKING:
    from PySide6.QtGui import QKeyEvent

    from PDFPreview.gui.widgets.listwidget import VListWidgetItem


# noinspection PyTypeChecker
file_filters: dict[bool, QDir.Filter] = {
    True: QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot,
    False: QDir.Filter.AllDirs
           | QDir.Filter.AllEntries
           | QDir.Filter.Drives
           | QDir.Filter.Hidden
           | QDir.Filter.NoDotAndDotDot,
}
pdf_toolbar: dict[bool, str] = {
    True: "toolbar=0",
    False: "",
}


class MainWindow(QMainWindow, Ui_MainWindow):
    # emitted when a file has been loaded in to the viewer
    fileDeleted: Signal = Signal(str)
    fileLoaded: Signal = Signal(str)
    pathChanged: Signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(f"{TITLE}")

        self._create_and_set_blur_effects()

        self.pathChanged.connect(self.update_title_bar)

        # NAVIGATION BUTTONS
        self.pbBack.setText("")
        self.pbBack.setToolTip("Back")
        self.pbBack.setIcon(QIcon((IMAGES / "back-arrow.png").resolve().as_posix()))

        self.pb_root.setText("")
        self.pb_root.setToolTip("My Computer")
        self.pb_root.setIcon(QIcon((IMAGES / "my_computer.png").resolve().as_posix()))

        self.pbBack.clicked.connect(self.handle_back_button_clicked)
        self.pb_root.clicked.connect(self.handle_root_button_clicked)
        # -----------------------------------------------------------

        self.help_shortcut = QShortcut(QKeySequence("h"), self)
        self.help_shortcut.activated.connect(self.show_help)
        self.help_save: QModelIndex | None = None

        # ABOUT WINDOW
        self.about_window = about.create_about_dialog()
        self.about_event_filter = AboutDialogFilter(self.about_window)
        self.about_window.installEventFilter(self.about_event_filter)
        self.about_event_filter.window_closing.connect(
            lambda: [effect.setEnabled(False) for effect in self.blur_effects]
        )
        self.actionAbout.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        )

        # this string gets appended to the url to show or hide the PDF viewer toolbar
        self.HIDE_TOOLBAR = ""

        self.actionHide_Toolbar.toggled.connect(self.toggle_toolbar)
        self.action_hide_files.toggled.connect(self.handle_action_hide_files)
        self.actionAbout.triggered.connect(self.show_about)

        # FILE VIEWER
        # must have in order for PDF viewing to work
        self.browser.page().settings().setAttribute(
            QWebEngineSettings.WebAttribute.PluginsEnabled,
            True,
        )
        self.browser.page().settings().setAttribute(
            QWebEngineSettings.WebAttribute.PdfViewerEnabled,
            True,
        )
        self.browser.installEventFilter(self)
        self.fileLoaded.connect(self.update_title_bar)

        # WINDOW INTO THE FILE SYSTEM
        self.model: QFileSystemModel = QFileSystemModel()
        self.model.setReadOnly(False)
        self.model.setFilter(file_filters[self.action_hide_files.isChecked()])
        self.model.setRootPath("")
        self.model.fileRenamed.connect(lambda p, o, n: self.update_title_bar(f"{p}/{n}"))
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
        self.treeView.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.treeView.setRootIndex(self.model.index(""))
        for i in range(1, 4):
            self.treeView.header().hideSection(i)
        self.treeView.currentIndexChanged.connect(self.handle_treeview_current_index_changed)
        self.treeView.clicked.connect(self.handle_treeview_current_index_changed)
        self.treeView.doubleClicked.connect(self.handle_treeview_double_click)
        self.treeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(
            self.handle_treeview_context_menu_request,
        )
        self.treeView.setItemsExpandable(False)
        self.treeView.setRootIsDecorated(False)
        self.treeView.installEventFilter(self)

        # RECENTS
        self.cb_recents.setToolTip("Recents")
        self.cb_recents.activated.connect(self.handle_recents_clicked)
        self.recents_tracker: recents.RecentsManager = recents.RecentsManager(
            self.cb_recents,
            config["general"]["recents_limit"]
        )
        self.fileDeleted.connect(self.recents_tracker.remove)
        self.model.fileRenamed.connect(self.recents_tracker.rename)
        self.actionClear_Recents.triggered.connect(self.recents_tracker.clear_recents)

        self.load_bookmarks()

        self.context_menu_actions = self._create_context_menu_dispatch_table()

        self.load_splash()

    def close(self) -> bool:
        return super().close()

    def handle_back_button_clicked(self, _) -> None:
        current_index: QModelIndex = self.treeView.currentIndex()

        if current_index.parent() == self.top_level_index:
            self.setWindowTitle(f'{TITLE} - "This PC"')

        new_index: QModelIndex = (
            current_index.parent()
            if self.model.isDir(current_index)
            else current_index.parent().parent()
        )

        self.treeView.setCurrentIndex(new_index)
        self.treeView.setRootIndex(new_index)
        self.treeView.collapseAll()

        if new_index != self.top_level_index:
            self.pathChanged.emit(str(Path(self.model.filePath(new_index))))

    def handle_root_button_clicked(self, _) -> None:
        self.treeView.setRootIndex(self.top_level_index)
        self.treeView.setCurrentIndex(self.top_level_index)
        self.setWindowTitle(f'{TITLE} - "This PC"')

    def handle_action_hide_files(self, checked: bool) -> None:  # noqa: FBT001
        self.model.setFilter(file_filters[checked])

    def handle_bookmark_clicked(self, list_item: VListWidgetItem) -> None:
        bookmark_index: QModelIndex = list_item.bookmark_index
        if not Path(list_item.path).exists():
            QMessageBox.information(self, "Info", f"File no longer exists:\n\n{list_item.path}")

            return

        is_file: bool = not self.model.isDir(bookmark_index)

        # it's a file so let's see it (don't want to see directory listings in the browser)
        if is_file:
            self.view_file(list_item.bookmark_index)
            bookmark_index = bookmark_index.parent()

        self.treeView.setRootIndex(bookmark_index)
        self.treeView.setCurrentIndex(bookmark_index)
        self.treeView.collapseAll()

        path = Path(
            self.model.filePath(list_item.bookmark_index) if is_file else self.model.filePath(bookmark_index)
        )
        self.pathChanged.emit(str(path))

    def handle_recents_clicked(self, index: int) -> None:
        path = self.recents_tracker.item_data(index)
        if not Path(path).exists():
            delete_recent(Path(path).resolve().name)
            self.recents_tracker.remove(Path(path).resolve().name)
            self.statusBar().showMessage(f"Recent not found: {path}", 3000)
            return

        qm_index = self.model.index(path).parent()
        self.treeView.setRootIndex(qm_index)
        self.treeView.setCurrentIndex(qm_index)
        self.view_file(self.model.index(path))

    def handle_treeview_current_index_changed(self, index: QModelIndex) -> None:
        if not self.model.isDir(index):
            self._add_recent(Path(self.model.filePath(index)))
        self.view_file(index)

    def handle_treeview_double_click(self, index: QModelIndex) -> None:
        if self.model.isDir(index):
            self.treeView.setRootIndex(index)
            self.pathChanged.emit(str(Path(self.model.filePath(index))))

    def handle_treeview_context_menu_request(self, position) -> None:
        """Creates a dynamic menu based on the file type."""
        index: QModelIndex = self.treeView.indexAt(position)
        print(f"index points to {self.model.filePath(index)}")

        if not index.isValid():
            print("clicked in the 'dead space'...")
            return

        suffix = self.model.filePath(index).rsplit(".", 1)[-1].lower()

        menu: QMenu = QMenu()

        open_with: QMenu = QMenu("Open With", menu)
        open_with.setIcon(QIcon((IMAGES / "open_with.ico").resolve().as_posix()))

        new_menu: QMenu = QMenu("New", menu)

        menu.addMenu(open_with)
        menu.addMenu(new_menu)

        if suffix in ["pdf"]:
            self._add_action("Adobe Acrobat", "acrobat", "acrobat-logo.png", open_with)

        self._add_action("Windows Explorer", "explorer", "explorer.png", open_with)

        if self.model.filePath(index).rsplit(".", 1)[-1].lower() in ["bmp", "gif", "jpg", "jpeg", "png", "svg", "webp"]:
            self._add_action("MS Paint", "paint", "palette.png", open_with)

        icon = QIcon((IMAGES / "folder.png").resolve().as_posix())
        self._add_action("Folder", "new_folder", icon, new_menu)
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        self._add_action("Text Document", "new_text_file", icon, new_menu)

        duplicate = self._add_action("Duplicate", "duplicate", "copy.png", menu)
        self._add_action("Move", "move", "move.png", menu)
        self._add_action("Rename", "rename", "rename.png", menu)

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogDiscardButton)
        self._add_action("Delete", "delete", icon, menu)

        if self.model.isDir(index):
            menu.removeAction(duplicate)

        # let's figure out what we're doing... and then do it!
        if action := menu.exec(self.treeView.viewport().mapToGlobal(position)):
            self._dispatch_action(action.objectName(), index)

    @staticmethod
    def _add_action(title: str, obj_name: str, icon: str | QIcon, menu: QMenu) -> QAction:
        action = menu.addAction(title)
        action.setObjectName(obj_name)
        if isinstance(icon, str):
            icon = QIcon((IMAGES / icon).resolve().as_posix())
        action.setIcon(icon)
        return action

    def eventFilter(self, source: QObject, event: QEvent) -> bool:  # noqa: N802
        if source is self.treeView and (
                event.type() == QEvent.Type.KeyPress
                and cast("QKeyEvent", event).key() == Qt.Key.Key_Space
        ):
            # open selected file when the spacebar is pressed
            fileoperations.open_file(self.model.filePath(self.treeView.currentIndex()))
            event.accept()
            return True

        if source is self.browser:
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
                new_index: QModelIndex = self.model.index(path.as_posix())

                self.treeView.collapseAll()
                self.treeView.setCurrentIndex(new_index)

                if self.model.isDir(new_index):
                    self.treeView.setRootIndex(self.model.index(path.as_posix()))
                    self.update_title_bar(str(path))
                else:
                    self.treeView.setRootIndex(self.model.index(path.parent.as_posix()))
                    self.view_file(new_index)

                event.accept()
                return True

        return super().eventFilter(source, event)

    def load_bookmarks(self) -> None:
        bookmarks.load_bookmarks(load_bookmarks(), self.lw_bookmarks, self.model)

    def load_splash(self) -> None:
        index: QModelIndex = self.model.index(SPLASH_FILE.as_posix())
        self.view_file(index)

    def show_about(self) -> None:
        [effect.setEnabled(True) for effect in self.blur_effects]

        self.about_window.move(
            gui.center_window_on_parent(parent=self, child=self.about_window),
        )
        self.about_window.show()

    def show_help(self) -> None:
        if self.help_save is None:
            self.help_save = self.treeView.currentIndex()
            self.load_splash()
        else:
            self.view_file(self.help_save)
            self.help_save = None

    def toggle_toolbar(self, checked: bool) -> None:  # noqa: FBT001
        self.HIDE_TOOLBAR = pdf_toolbar[checked]
        self.view_file(self.treeView.currentIndex())

    def update_title_bar(self, path: str) -> None:
        separator = " - " if path else ""
        self.setWindowTitle(f"{TITLE}{separator}{path}")

    def view_file(self, index: QModelIndex) -> None:
        """Loads the file pointed to by index into the viewing pane."""
        # do not load directories into the viewer i.e., navigable elements
        if self.model.isDir(index):
            return

        file_path = Path(self.model.filePath(index))

        url: QUrl = QUrl.fromLocalFile(str(file_path))
        url.setFragment(f"{self.HIDE_TOOLBAR}&navpanes=0")

        self.browser.setUrl(url)

        with suppress(IndexError):
            if file_path.as_posix().rsplit(".", 1)[1].lower() in ["bmp", "gif", "jpg", "jpeg", "png", "svg", "webp"]:
                self.browser.setZoomFactor(1.00)

        self.fileLoaded.emit(str(file_path))

    def _add_recent(self, path: Path) -> None:
        self.recents_tracker.add(str(path))

    def _update_bookmarks(self) -> None:
        lw = self.lw_bookmarks
        bookmarks_ = []
        for row in range(lw.count()):
            bookmarks_.append((lw.item(row).text(), self.model.filePath(lw.item(row).bookmark_index), row))

        update_bookmark_order(bookmarks_)

    def _create_and_set_blur_effects(self) -> None:
        widgets = (self.gb_bookmarks, self.gb_file_browser, self.browser, self.statusbar, self.menubar)
        self.blur_effects = [QGraphicsBlurEffect(widget) for widget in widgets]
        [(effect.setBlurRadius(7), effect.setEnabled(False)) for effect in self.blur_effects]
        [widget.setGraphicsEffect(effect) for widget, effect in zip(widgets, self.blur_effects)]

    # Context Menu Actions

    def _create_context_menu_dispatch_table(self) -> dict:
        return {
            "acrobat": self._do_acrobat_action,
            "explorer": self._do_explorer_action,
            "rename": self._do_rename_action,
            "delete": self._do_delete_action,
            "paint": self._do_paint_action,
            "project": self._do_project_action,
            "duplicate": self._do_duplicate_action,
            "move": self._do_move_action,
            "new_folder": self._do_new_folder_action,
            "new_text_file": self._do_new_text_file_action,
        }

    def _dispatch_action(self, action: str, index: QModelIndex) -> None:
        if not index.isValid():
            return
        self.context_menu_actions[action](index)

    def _do_acrobat_action(self, index: QModelIndex) -> None:
        path = Path(self.model.filePath(index))
        if path.suffix.lower() == ".pdf":
            fileoperations.open_with_acrobat(self.model.filePath(index))

    def _do_delete_action(self, index: QModelIndex) -> None:
        if self._ask_yes_or_no(self, "Delete", f"Deleting '{self.model.fileName(index)}'.\n\nThis action can not be undone.\nAre you sure?"):
            if self.model.isDir(index):
                path = Path(self.model.filePath(index))
                result = fileoperations.delete_folder(path)
                if not result.success and result.message == "Not Empty":
                    if self._ask_yes_or_no(self, "Warning", "Folder is not empty. Continue?"):
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

    def _do_move_action(self, index: QModelIndex) -> None:
        if folder := QFileDialog.getExistingDirectory(self):
            source_path = Path(self.model.filePath(index))
            result = fileoperations.move_file(source_path, Path(folder) / source_path.name)
            if not result.success:
                QMessageBox.warning(self, "Warning", result.message)

    def _do_new_folder_action(self, index: QModelIndex) -> None:
        result = fileoperations.mkdir(Path(self.model.filePath(index)).parent)
        if not result.success:
            QMessageBox.warning(self, "Warning", result.message)

    def _do_new_text_file_action(self, index: QModelIndex) -> None:
        result = fileoperations.new_txt_file(Path(self.model.filePath(index)).parent)
        if not result.success:
            QMessageBox.warning(self, "Warning", result.message)

    def _do_explorer_action(self, index: QModelIndex) -> None:
        fileoperations.open_file_location(self.model.filePath(index))

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
                self.update_title_bar(self.model.filePath(self.treeView.currentIndex()))
            else:
                QMessageBox.warning(self, "Rename Failed", f"{result.message}\n\nUnable to rename this file.")

    def _do_paint_action(self, index: QModelIndex) -> None:
        fileoperations.open_with_mspaint(self.model.filePath(index))

    def _do_project_action(self, index: QModelIndex) -> None:
        QMessageBox.information(self, "Open as Project", "Option currently not implemented.")
        # get a list of all files in folder and subfolders, etc.
        # open each file in the browser

    @staticmethod
    def _ask_yes_or_no(parent, title: str, message: str) -> bool:
        return QMessageBox.question(
            parent,
            title,
            message
        ) == QMessageBox.StandardButton.Yes
