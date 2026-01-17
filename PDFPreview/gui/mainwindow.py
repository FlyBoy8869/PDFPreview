try:
    from os import startfile  # type: ignore  # noqa: PGH003
except ImportError:
    import webbrowser
    from collections.abc import Callable

    startfile: Callable[..., bool] = webbrowser.open_new_tab

import platform
from pathlib import Path
from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QEvent, QFile, QModelIndex, QObject, Qt, QUrl
from PySide6.QtGui import QCloseEvent, QDropEvent
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWidgets import QFileSystemModel, QLabel, QMainWindow

from PDFPreview.gui.customwidgets import MyCustomTreeView, MyListWidgetItem

from .ui_mainwindow import Ui_MainWindow

if TYPE_CHECKING:
    from PySide6.QtGui import QKeyEvent

VERSION = "0.1.7"
TITLE = "PDFPreview"

PATH_PREFIX = "file://" if "macOS" in platform.platform() else "file:///"

FAVORITES = Path(__file__).parent / "favorites.dat"
ABOUT_UI_PATH = Path(__file__).parent / "ui_about.ui"


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(TITLE)

        # this string gets appended to the url to show or hide the pdf viewer toolbar
        self.HIDE_TOOLBAR = ""

        self._create_about_dialog()

        self.actionHide_Toolbar.toggled.connect(self.toggle_toolbar)
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

        self.model: QFileSystemModel = QFileSystemModel()
        self.model.setRootPath("")

        self.top_level_index = self.model.index(self.model.rootPath())

        self.lw_favorites.installEventFilter(self)
        self.lw_favorites.itemClicked.connect(self.handle_favorite_clicked)

        self.treeView.setModel(self.model)
        self.treeView.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.treeView.setRootIndex(self.model.index(""))
        for i in range(1, 4):
            self.treeView.header().hideSection(i)
        self.treeView.currentIndexChangedAsString.connect(self.preview)
        self.treeView.doubleClicked.connect(self.handle_treeview_double_click)
        self.treeView.installEventFilter(self)
        self.treeView.setItemsExpandable(False)
        self.treeView.setRootIsDecorated(False)

        self.pbBack.clicked.connect(self.handle_back_button_clicked)

        self.load_favorites()

    def handle_back_button_clicked(self, _) -> None:
        current_index: QModelIndex = self.treeView.currentIndex()
        if current_index == self.top_level_index:
            return

        new_index = (
            current_index.parent()
            if self.model.isDir(current_index)
            else current_index.parent().parent()
        )
        self.treeView.setCurrentIndex(new_index)
        self.treeView.setRootIndex(new_index)
        self.treeView.collapseAll()
        if new_index.data() != self.model.rootPath():
            self.update_title_bar_for_folder(new_index)

    def handle_favorite_clicked(self, index: MyListWidgetItem) -> None:
        self.treeView.setRootIndex(index.extra)
        self.treeView.setCurrentIndex(index.extra)
        self.treeView.collapseAll()
        self.update_title_bar_for_folder(index.extra)

    def handle_treeview_double_click(self, index: QModelIndex) -> None:
        if self.model.isDir(index):
            self.treeView.setRootIndex(index)
            self.update_title_bar_for_folder(index)

    def open_file(self, index) -> None:
        """Open file in the default application."""
        file: str = self.model.filePath(index)
        startfile(QUrl.fromLocalFile(file).url())

    def preview(self, path: str, index: QModelIndex) -> None:
        self.setWindowTitle(f"PDFPreview - {path}")
        self._update_title_bar_from_index(index)
        if not self.model.isDir(index):
            self.browser.page().setUrl(
                f"{QUrl.url(QUrl.fromLocalFile(f'{path}'))}{self.HIDE_TOOLBAR}",
            )

    def show_about(self) -> None:
        self.about_window.show()

    def toggle_toolbar(self, checked: bool) -> None:  # noqa: FBT001
        self.HIDE_TOOLBAR = "#toolbar=0" if checked else ""
        self.preview(
            self.model.filePath(self.treeView.currentIndex()),
            self.treeView.currentIndex(),
        )

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._save_favorites()
        return super().closeEvent(event)

    def eventFilter(self, source: QObject, event: QEvent) -> bool:  # noqa: N802
        if isinstance(source, MyCustomTreeView) and (
            event.type() == QEvent.Type.KeyPress
            and cast("QKeyEvent", event).key() == Qt.Key.Key_Space
        ):
            self.open_file(self.treeView.currentIndex())
            event.accept()

        if source is self.browser:
            if event.type() == QEvent.Type.DragEnter:
                print("drag enter event")
                event.accept()

            if event.type() == QEvent.Type.Drop:
                print("drop on browser...")
                mime_text = cast("QDropEvent", event).mimeData().text()
                path = Path(mime_text.replace(PATH_PREFIX, ""))
                new_index = self.model.index(path.as_posix())
                self.preview(path.as_posix(), new_index)
                self.treeView.collapseAll()
                self.treeView.setCurrentIndex(new_index)
                self.treeView.setRootIndex(self.model.index(path.parent.as_posix()))
                print(f"{path=}")
                event.accept()

        if source is self.lw_favorites:
            if event.type() == QEvent.Type.DragEnter:
                event.accept()

            if event.type() == QEvent.Type.Drop:
                event = cast("QDropEvent", event)
                folder = event.mimeData().text()
                folder = folder.replace(PATH_PREFIX, "")
                if self.model.isDir(self.model.index(folder)):
                    base = folder.split("/")[-1]
                    item = MyListWidgetItem(base, extra=self.model.index(folder))
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                    self.lw_favorites.addItem(item)

                event.accept()

            if (
                event.type() == QEvent.Type.KeyPress
                and cast("QKeyEvent", event).key() == Qt.Key.Key_Delete
            ):
                item = self.lw_favorites.currentItem()
                self.lw_favorites.takeItem(self.lw_favorites.row(item))
                event.accept()

        return super().eventFilter(source, event)

    def _create_about_dialog(self) -> None:
        about_file = QFile(ABOUT_UI_PATH)
        loader = QUiLoader()
        about_file.open(QFile.OpenModeFlag.ReadOnly)
        self.about_window = loader.load(about_file)
        if version_label := self.about_window.findChild(QLabel, "lbl_about"):
            version_label.setTextFormat(Qt.TextFormat.RichText)
            version_label.setText(
                f"<center><h2>PDFPreview</h2></center><center>version: {VERSION}</center><center>author: Charles Cognato</center>"
            )
        about_file.close()

    def _save_favorites(self) -> None:
        favorites = Path(__file__).parent / FAVORITES
        favorites.touch()
        with favorites.open(mode="w", encoding="utf-8") as of:
            for index in range(self.lw_favorites.count()):
                item: MyListWidgetItem = cast(
                    "MyListWidgetItem",
                    self.lw_favorites.item(index),
                )
                extra: QModelIndex = item.extra
                of.write(
                    f"{item.data(Qt.ItemDataRole.DisplayRole)}|{self.model.filePath(extra)}\n",
                )

    def load_favorites(self) -> None:
        try:
            with FAVORITES.open("r", encoding="utf-8") as inputfile:
                for line in inputfile:
                    display_role, extra = line.split("|")
                    # make sure to strip the "extra" or else the QFileSystemModel won't find the path due to the "\n"
                    item = MyListWidgetItem(
                        display_role,
                        extra=self.model.index(extra.strip()),
                    )
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                    self.lw_favorites.addItem(item)
        except FileNotFoundError:
            pass

    def update_title_bar_for_folder(self, index) -> None:
        if self.model.isDir(index):
            self._update_title_bar_from_index(index)

    def _update_title_bar_from_index(self, index) -> None:
        self.setWindowTitle(f"{TITLE} - {self.model.filePath(index)}")
