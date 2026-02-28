from pathlib import Path
from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QDir, QEvent, QModelIndex, QObject, Qt, QUrl, Signal
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
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
    QMessageBox,
)

from PDFPreview.gui.dialogs import about
from PDFPreview.helpers import bookmarks, fileoperations, gui
from PDFPreview.services.bookmark_service import update_bookmark_order, load_bookmarks

from .ui_mainwindow import Ui_MainWindow
from PDFPreview.eventfilters.about_eventfilter import AboutDialogFilter
from PDFPreview.eventfilters.bookmark_eventfilter import BookmarkListEventFilter

if TYPE_CHECKING:
    from PySide6.QtGui import QKeyEvent

    from PDFPreview.gui.widgets.listwidget import VListWidgetItem

from config.config import PATH_PREFIX, SPLASH_FILE, TITLE, VERSION, IMAGES

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
    file_loaded: Signal = Signal(str)
    path_changed: Signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pbBack.setText("")
        self.pbBack.setToolTip("back")
        self.pbBack.setIcon(QIcon((IMAGES / "back-arrow.png").resolve().as_posix()))
        self.pb_root.setText("")
        self.pb_root.setToolTip("My Computer")
        self.pb_root.setIcon(QIcon((IMAGES / "my_computer.png").resolve().as_posix()))
        self.setWindowTitle(f"{TITLE} [{VERSION}]")

        self.path_changed.connect(self.update_title_bar)

        self.help_shortcut = QShortcut(QKeySequence("h"), self)
        self.help_shortcut.activated.connect(self.show_help)

        self.help_save: QModelIndex | None = None

        # this string gets appended to the url to show or hide the PDF viewer toolbar
        self.HIDE_TOOLBAR = ""

        self.about_window = about.create_about_dialog()
        self.about_event_filter = AboutDialogFilter(self.about_window)
        self.about_window.installEventFilter(self.about_event_filter)

        self.actionHide_Toolbar.toggled.connect(self.toggle_toolbar)
        self.action_hide_files.toggled.connect(self.handle_action_hide_files)
        self.actionAbout.triggered.connect(self.show_about)

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
        self.file_loaded.connect(self.update_title_bar)

        self.model: QFileSystemModel = QFileSystemModel()
        self.model.setFilter(file_filters[self.action_hide_files.isChecked()])
        self.model.setRootPath("")

        self.top_level_index: QModelIndex = self.model.index(self.model.rootPath())

        self.lw_bookmarks_eventfilter: BookmarkListEventFilter = (
            BookmarkListEventFilter(self.lw_bookmarks, self.model)
        )
        self.lw_bookmarks.installEventFilter(self.lw_bookmarks_eventfilter)
        self.lw_bookmarks.itemClicked.connect(self.handle_bookmark_clicked)
        self.lw_bookmarks.model().rowsMoved.connect(self.update_bookmarks)
        self.lw_bookmarks.model().dataChanged.connect(self.update_bookmarks)

        self.treeView.setModel(self.model)
        self.treeView.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.treeView.setRootIndex(self.model.index(""))
        for i in range(1, 4):
            self.treeView.header().hideSection(i)
        self.treeView.currentIndexChanged.connect(self.view_file)
        self.treeView.doubleClicked.connect(self.handle_treeview_double_click)
        self.treeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(
            self.handle_treeview_context_menu_request,
        )
        self.treeView.setItemsExpandable(False)
        self.treeView.setRootIsDecorated(False)
        self.treeView.installEventFilter(self)

        self.pbBack.clicked.connect(self.handle_back_button_clicked)
        self.pb_root.clicked.connect(self.handle_root_button_clicked)

        self.load_favorites()

        self.context_menu_actions = self._create_context_menu_dispatch_table()

        self.load_splash()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        return super().closeEvent(event)

    def handle_back_button_clicked(self, _) -> None:
        current_index: QModelIndex = self.treeView.currentIndex()
        if current_index.parent().data() == self.top_level_index.data():
            self.treeView.collapseAll()
            self.treeView.setCurrentIndex(self.top_level_index)
            self.treeView.setRootIndex(self.top_level_index)
            self.path_changed.emit(self.model.filePath(current_index.parent()))
            return

        new_index: QModelIndex = (
            current_index.parent()
            if self.model.isDir(current_index)
            else current_index.parent().parent()
        )

        self.treeView.setCurrentIndex(new_index)
        self.treeView.setRootIndex(new_index)
        self.treeView.collapseAll()

        if new_index.data() != self.model.rootPath():
            self.path_changed.emit(self.model.filePath(new_index))

    def handle_root_button_clicked(self, _) -> None:
        self.treeView.setRootIndex(self.top_level_index)
        self.treeView.setCurrentIndex(self.top_level_index)
        self.path_changed.emit(self.model.filePath(self.top_level_index))

    def handle_action_hide_files(self, checked: bool) -> None:  # noqa: FBT001
        self.model.setFilter(file_filters[checked])

    def handle_bookmark_clicked(self, list_item: VListWidgetItem) -> None:
        bookmark_index: QModelIndex = list_item.bookmark_index
        is_file: bool = not self.model.isDir(bookmark_index)

        # it's a file so let's see it (don't want to see directory listings in the browser)
        if is_file:
            self.view_file(list_item.bookmark_index)
            bookmark_index = bookmark_index.parent()

        self.treeView.setRootIndex(bookmark_index)
        self.treeView.setCurrentIndex(bookmark_index)
        self.treeView.collapseAll()

        path = self.model.filePath(list_item.bookmark_index) if is_file else self.model.filePath(bookmark_index)
        self.path_changed.emit(path)

    def handle_treeview_double_click(self, index: QModelIndex) -> None:
        if self.model.isDir(index):
            self.treeView.setRootIndex(index)
            self.path_changed.emit(self.model.filePath(index))

    def handle_treeview_context_menu_request(self, position) -> None:
        index: QModelIndex = self.treeView.indexAt(position)
        if not index.isValid():
            return

        menu: QMenu = QMenu()
        open_with: QMenu = QMenu("Open...", menu)
        menu.addMenu(open_with)

        acrobat: QAction = open_with.addAction("with Adobe Acrobat")
        acrobat.setObjectName("acrobat")
        explorer: QAction = open_with.addAction("Location in Windows Explorer")
        explorer.setObjectName("explorer")
        rename: QAction = menu.addAction("Rename")
        rename.setObjectName("rename")
        delete: QAction = menu.addAction("Delete")
        delete.setObjectName("delete")

        if self.model.isDir(index):
            open_with.removeAction(acrobat)
            menu.removeAction(delete)

        if action := menu.exec(self.treeView.viewport().mapToGlobal(position)):
            self.context_menu_actions[action.objectName()](index)

    def eventFilter(self, source: QObject, event: QEvent) -> bool:  # noqa: N802
        if source is self.treeView and (
                event.type() == QEvent.Type.KeyPress
                and cast("QKeyEvent", event).key() == Qt.Key.Key_Space
        ):
            # open selected file when the spacebar is pressed
            fileoperations.open_file(self.model.filePath(self.treeView.currentIndex()))
            event.accept()
            return event.isAccepted()

        if source is self.browser:
            if event.type() == QEvent.Type.DragEnter:
                event = cast("QDragEnterEvent", event)

                # allow drops if they have urls attached
                if (
                        event.proposedAction() == Qt.DropAction.CopyAction
                        and event.mimeData().hasUrls()
                ):
                    event.accept()
                else:
                    event.ignore()

                return event.isAccepted()

            # handle drops on the preview pane
            if event.type() == QEvent.Type.Drop:
                path = Path(
                    cast("QDropEvent", event)
                    .mimeData()
                    .text()
                    .replace("%23", "#")  # dirty workaround
                    .replace(PATH_PREFIX, ""),
                )
                new_index: QModelIndex = self.model.index(path.as_posix())

                self.treeView.collapseAll()
                self.treeView.setCurrentIndex(new_index)

                if self.model.isDir(new_index):
                    self.treeView.setRootIndex(self.model.index(path.as_posix()))
                    self.update_title_bar(path.as_posix())
                else:
                    self.treeView.setRootIndex(self.model.index(path.parent.as_posix()))
                    self.view_file(new_index)

                event.accept()
                return event.isAccepted()

        return super().eventFilter(source, event)

    def load_favorites(self) -> None:
        bookmarks.load_bookmarks(load_bookmarks(), self.lw_bookmarks, self.model)

    def load_splash(self) -> None:
        index: QModelIndex = self.model.index(SPLASH_FILE.as_posix())
        self.view_file(index)

    def show_about(self) -> None:
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

    def update_bookmarks(self) -> None:
        lw = self.lw_bookmarks
        bookmarks_ = []
        for row in range(lw.count()):
            bookmarks_.append((lw.item(row).text(), self.model.filePath(lw.item(row).extra), row))

        update_bookmark_order(bookmarks_)

    def update_title_bar(self, path: str) -> None:
        separator = " - " if path else ""
        self.setWindowTitle(f"{TITLE}{separator}{path}")

    def view_file(self, index: QModelIndex) -> None:
        """Loads the file pointed to by index into the viewing pane."""
        # do not load directories into the viewer i.e., navigable elements
        if self.model.isDir(index):
            return

        file_path = self.model.filePath(index)

        url: QUrl = QUrl.fromLocalFile(file_path)
        url.setFragment(f"{self.HIDE_TOOLBAR}&navpanes=0")

        self.browser.setUrl(url)

        if file_path.rsplit(".", 1)[1] in ["bmp", "gif", "jpg", "jpeg", "png", "svg", "webp"]:
            self.browser.setZoomFactor(1.00)

        self.file_loaded.emit(file_path)

    # Context Menu Actions

    def _create_context_menu_dispatch_table(self) -> dict:
        return {
            "acrobat": self._do_acrobat_action,
            "explorer": self._do_explorer_action,
            "rename": self._do_rename_action,
            "delete": self._do_delete_action,
        }

    def _do_acrobat_action(self, index: QModelIndex) -> None:
        path = Path(self.model.filePath(index))
        if path.suffix.lower() == ".pdf":
            # sneaky behavior; open a non-pdf in a hopefully appropriate system program
            fileoperations.open_with_acrobat(self.model.filePath(index))
        else:
            fileoperations.open_file(path.as_posix())

    def _do_delete_action(self, index: QModelIndex) -> None:
        if (
                QMessageBox.question(self, "Delete", "Are you sure?")
                == QMessageBox.StandardButton.Yes
        ):
            fileoperations.delete_file(self.model, index)

    def _do_explorer_action(self, index: QModelIndex) -> None:
        fileoperations.open_file_location(self.model.filePath(index))

    def _do_rename_action(self, index: QModelIndex) -> None:
        if new_name := QInputDialog.getText(
                self,
                "Rename File",
                "Enter a new name for this file:",
                text=index.data(),
        )[0]:
            fileoperations.rename_file(self.model, index, new_name)
