from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QDir, QEvent, QModelIndex, QObject, Qt, QUrl, Signal
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QDragEnterEvent,
    QDropEvent,
    QKeySequence,
    QShortcut, QIcon, QPixmap,
)
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWidgets import (
    QFileSystemModel,
    QInputDialog,
    QMainWindow,
    QMenu,
    QMessageBox, QStyle, QGraphicsBlurEffect
)

import config.config
from config.config import config
from PDFPreview.gui.dialogs import about
from PDFPreview.helpers import bookmarks, fileoperations, gui, recents
from PDFPreview.services.bookmark_service import update_bookmark_order, load_bookmarks

from .ui_mainwindow import Ui_MainWindow
from PDFPreview.eventfilters.about_eventfilter import AboutDialogFilter
from PDFPreview.eventfilters.bookmark_eventfilter import BookmarkListEventFilter

if TYPE_CHECKING:
    from PySide6.QtGui import QKeyEvent

    from PDFPreview.gui.widgets.listwidget import VListWidgetItem

from config.config import PATH_PREFIX, SPLASH_FILE, TITLE, IMAGES

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
        self.lw_bookmarks_eventfilter: BookmarkListEventFilter = (
            BookmarkListEventFilter(self.lw_bookmarks, self.model)
        )
        self.lw_bookmarks.installEventFilter(self.lw_bookmarks_eventfilter)
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

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        return super().closeEvent(event)

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
        qm_index = self.model.index(path).parent()
        self.treeView.setRootIndex(qm_index)
        self.treeView.setCurrentIndex(qm_index)
        # self.view_file(self.model.index(self.recents_tracker.item_data(index)))
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
        index: QModelIndex = self.treeView.indexAt(position)
        if not index.isValid():
            return

        menu: QMenu = QMenu()

        open_with: QMenu = QMenu("Open With", menu)
        open_with.setIcon(QIcon((IMAGES / "open_with.ico").resolve().as_posix()))
        menu.addMenu(open_with)

        acrobat: QAction = open_with.addAction("Adobe Acrobat")
        acrobat.setObjectName("acrobat")
        acrobat.setIcon(QPixmap((IMAGES / "acrobat-logo.png").resolve().as_posix()))

        explorer: QAction = open_with.addAction("Windows Explorer")
        explorer.setObjectName("explorer")
        explorer.setIcon(
            QPixmap((IMAGES / "explorer-1.png").resolve().as_posix())
        )

        if self.model.filePath(index).rsplit(".", 1)[-1].lower() in ["bmp", "gif", "jpg", "jpeg", "png", "svg", "webp"]:
            paint: QAction = open_with.addAction("MS Paint")
            paint.setObjectName("paint")
            paint.setIcon(
                QPixmap((IMAGES / "palette.png").resolve().as_posix())
            )

        rename: QAction = menu.addAction("Rename")
        rename.setObjectName("rename")
        rename.setIcon(
            QPixmap((IMAGES / "rename.png").resolve().as_posix())
        )

        delete: QAction = menu.addAction("Delete")
        delete.setObjectName("delete")
        delete.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogDiscardButton))

        if self.model.isDir(index):
            open_with.removeAction(acrobat)

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
                    self.update_title_bar(str(path))
                else:
                    self.treeView.setRootIndex(self.model.index(path.parent.as_posix()))
                    self.view_file(new_index)

                event.accept()
                return event.isAccepted()

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

    # Context Menu Actions

    def _create_context_menu_dispatch_table(self) -> dict:
        return {
            "acrobat": self._do_acrobat_action,
            "explorer": self._do_explorer_action,
            "rename": self._do_rename_action,
            "delete": self._do_delete_action,
            "paint": self._do_paint_action,
        }

    def _create_and_set_blur_effects(self) -> None:
        self.blur_effects = (
            QGraphicsBlurEffect(self.gb_bookmarks),
            QGraphicsBlurEffect(self.gb_file_browser),
            QGraphicsBlurEffect(self.browser),
            QGraphicsBlurEffect(self.statusbar),
            QGraphicsBlurEffect(self.menubar),
        )
        [effect.setBlurRadius(7) for effect in self.blur_effects]
        [effect.setEnabled(False) for effect in self.blur_effects]

        widgets = (self.gb_bookmarks, self.gb_file_browser, self.browser, self.statusbar, self.menubar)
        [widget.setGraphicsEffect(effect) for widget, effect in zip(widgets, self.blur_effects)]

    def _do_acrobat_action(self, index: QModelIndex) -> None:
        path = Path(self.model.filePath(index))
        if path.suffix.lower() == ".pdf":
            # sneaky behavior; open a non-pdf in a hopefully appropriate system program
            fileoperations.open_with_acrobat(self.model.filePath(index))
        else:
            fileoperations.open_file(path.as_posix())

    def _do_delete_action(self, index: QModelIndex) -> None:
        if self._ask_yes_or_no(self, "Delete", "This action can not be undone.\nAre you sure?"):
            if fileoperations.delete_file(self.model, index):
                self.fileDeleted.emit(self.model.filePath(index))

    def _do_explorer_action(self, index: QModelIndex) -> None:
        fileoperations.open_file_location(self.model.filePath(index))

    def _do_rename_action(self, index: QModelIndex) -> None:
        if new_name := QInputDialog.getText(
                self,
                "Rename File",
                "Enter a new name for this file:",
                text=index.data(),
        )[0]:
            if fileoperations.rename_file(self.model, index, new_name):
                self.update_title_bar(self.model.filePath(self.treeView.currentIndex()))

    def _do_paint_action(self, index: QModelIndex) -> None:
        fileoperations.open_with_mspaint(self.model.filePath(index))

    @staticmethod
    def _ask_yes_or_no(parent, title: str, message: str) -> bool:
        return QMessageBox.question(
            parent,
            title,
            message
        ) == QMessageBox.StandardButton.Yes
