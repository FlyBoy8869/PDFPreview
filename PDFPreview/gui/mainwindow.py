from pathlib import Path
from typing import TYPE_CHECKING, Literal, Tuple, cast

from PySide6.QtCore import QEvent, QFile, QModelIndex, QObject, QPoint, Qt, QUrl
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QColor,
    QDragEnterEvent,
    QDropEvent,
    QKeyEvent,
    QKeySequence,
    QPalette,
    QPixmap,
    QShortcut,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWidgets import (
    QFileSystemModel,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QWidget,
)

from PDFPreview.gui.customwidgets import MyListWidgetItem
from PDFPreview.helpers import eventfilters, favorites, fileoperations

from .ui_mainwindow import Ui_MainWindow

if TYPE_CHECKING:
    from PySide6.QtGui import QKeyEvent

from PDFPreview import (
    ABOUT_UI_PATH,
    FAVORITES,
    LOGO,
    PATH_PREFIX,
    SPLASH_FILE,
    TITLE,
    VERSION,
)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(f"{TITLE} [{VERSION}]")
        self.help_shortcut = QShortcut(QKeySequence("h"), self)
        self.help_shortcut.activated.connect(self.show_help)

        self.help_save: QModelIndex | None = None

        # this string gets appended to the url to show or hide the pdf viewer toolbar
        self.HIDE_TOOLBAR = ""

        self.create_about_dialog()

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

        self.top_level_index: QModelIndex = self.model.index(self.model.rootPath())

        self.lw_favorites_eventfilter: eventfilters.FavoritesListFilter = (
            eventfilters.FavoritesListFilter(self.lw_favorites, self.model)
        )
        self.lw_favorites.installEventFilter(self.lw_favorites_eventfilter)
        self.lw_favorites.itemClicked.connect(self.handle_favorite_clicked)

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

        self.load_favorites()

        self.load_splash()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self.save_favorites()
        return super().closeEvent(event)

    def handle_back_button_clicked(self, _) -> None:
        current_index: QModelIndex = self.treeView.currentIndex()
        if not current_index.isValid():
            return
        if current_index == self.top_level_index:
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
            self.update_title_bar_for_folder(new_index)

    def handle_favorite_clicked(self, index: MyListWidgetItem) -> None:
        extra_copy: QModelIndex = index.extra
        if not self.model.isDir(index.extra):
            self.view_file(index.extra)
            folder_index: QModelIndex = index.extra.parent()
            extra_copy = folder_index

        self.treeView.setRootIndex(extra_copy)
        self.treeView.setCurrentIndex(extra_copy)
        self.treeView.collapseAll()
        self.update_title_bar_for_folder(extra_copy)

    def handle_treeview_double_click(self, index: QModelIndex) -> None:
        if self.model.isDir(index):
            self.treeView.setRootIndex(index)
            self.update_title_bar_for_folder(index)

    def handle_treeview_context_menu_request(self, position) -> None:
        index: QModelIndex = self.treeView.indexAt(position)
        if not index.isValid():
            return

        menu: QMenu = QMenu()

        rename: QAction = menu.addAction("Rename")
        delete: QAction = menu.addAction("Delete")

        if self.model.isDir(index):
            delete.setEnabled(False)

        global_position: QPoint = self.treeView.viewport().mapToGlobal(position)
        action: QAction = menu.exec(global_position)

        if action == rename:
            if new_name := QInputDialog.getText(
                self,
                "Rename File",
                "Enter a new name for this file.",
                text=index.data(),
            )[0]:
                fileoperations.rename_file(self.model, index, new_name)
        elif action == delete and (
            QMessageBox.question(self, "Delete", "Are you sure?")
            == QMessageBox.StandardButton.Yes
        ):
            fileoperations.delete_file(self.model, index)

    def open_file(self, index) -> None:
        """Open file in the default application."""
        fileoperations.open_file(self.model.filePath(index))

    def view_file(self, index: QModelIndex) -> None:
        """Loads the file pointed to by index into the viewing pane."""
        if self.model.isDir(index):
            return

        url: QUrl = QUrl.fromLocalFile(self.model.filePath(index))
        url.setFragment(f"{self.HIDE_TOOLBAR}&navpanes=0")
        self.browser.page().setUrl(url)

        self.update_title_bar_from_index(index)

    def show_about(self) -> None:
        self.about_window.move(self.center_window(self, self.about_window))
        self.about_window.show()

    def center_window(self, parent, sibling) -> QPoint:
        return QPoint(
            parent.x() + ((parent.width() - sibling.width()) // 2),
            parent.y() + ((parent.height() - sibling.height()) // 2),
        )

    def toggle_toolbar(self, checked: bool) -> None:  # noqa: FBT001
        self.HIDE_TOOLBAR: Literal["toolbar=0", ""] = "toolbar=0" if checked else ""
        self.view_file(self.treeView.currentIndex())

    def eventFilter(self, source: QObject, event: QEvent) -> bool:  # noqa: N802
        if source is self.treeView and (
            event.type() == QEvent.Type.KeyPress
            and cast("QKeyEvent", event).key() == Qt.Key.Key_Space
        ):
            self.open_file(self.treeView.currentIndex())
            event.accept()
            # this and the others below are vital to the proper handling of these events
            return event.isAccepted()

        if source is self.browser:
            # handle the dropping of files and folder onto the preview pane
            if event.type() == QEvent.Type.DragEnter:
                event = cast("QDragEnterEvent", event)
                if (
                    event.proposedAction() == Qt.DropAction.CopyAction
                    and event.mimeData().hasUrls()
                ):
                    event.accept()
                else:
                    event.ignore()
                return event.isAccepted()

            if event.type() == QEvent.Type.Drop:
                mime_text: str = cast("QDropEvent", event).mimeData().text()
                path = Path(mime_text.replace(PATH_PREFIX, ""))
                new_index: QModelIndex = self.model.index(path.as_posix())

                self.treeView.collapseAll()
                self.treeView.setCurrentIndex(new_index)
                self.treeView.setRootIndex(self.model.index(path.parent.as_posix()))

                if self.model.isDir(new_index):
                    self.update_title_bar_from_index(
                        self.model.index(path.parent.as_posix()),
                    )

                self.view_file(new_index)

                event.accept()
                return event.isAccepted()

        return super().eventFilter(source, event)

    def create_about_dialog(self) -> None:
        p = QPalette()
        r, g, b, a = cast("tuple", p.color(QPalette.ColorRole.Window).toRgb().toTuple())
        color = f"rgba({r},{g},{b},{a})"
        dialog_stylesheet = f"QWidget {{background-color: {color}; border-radius: 20px;}}"

        about_file = QFile(ABOUT_UI_PATH)
        loader = QUiLoader()
        about_file.open(QFile.OpenModeFlag.ReadOnly)
        self.about_window: QWidget = loader.load(about_file)
        about_file.close()

        self.about_window.setWindowFlags(
            self.about_window.windowFlags() | Qt.WindowType.FramelessWindowHint,
        )
        self.about_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.about_window.setStyleSheet(dialog_stylesheet)
        self.about_window.setWindowTitle(TITLE)
        self.about_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.about_window_filter: eventfilters.AboutDialogFilter = (
            eventfilters.AboutDialogFilter(self.about_window)
        )
        self.about_window.installEventFilter(self.about_window_filter)

        if logo_label := self.about_window.findChild(QLabel, "lbl_logo"):
            logo_label.setPixmap(QPixmap(LOGO.as_posix()))

        if version_label := self.about_window.findChild(QLabel, "lbl_about"):
            version_label.setTextFormat(Qt.TextFormat.RichText)
            version_label.setText(
                f"<center><h1>{TITLE}</h1></center><center>Version: {VERSION}</center><center>Author: Charles Cognato</center>",
            )

    def load_splash(self) -> None:
        index: QModelIndex = self.model.index(SPLASH_FILE.as_posix())
        self.view_file(index)

    def show_help(self) -> None:
        if self.help_save is None:
            self.help_save = self.treeView.currentIndex()
            self.load_splash()
        else:
            self.view_file(self.help_save)
            self.help_save = None

    def save_favorites(self) -> None:
        favorites.save_favorites_from(
            widget=self.lw_favorites,
            to_file_path=FAVORITES,
            using_model=self.model,
        )

    def load_favorites(self) -> None:
        favorites.load_favorites_to(
            widget=self.lw_favorites,
            from_file_path=FAVORITES,
            using_model=self.model,
        )

    def update_title_bar_for_folder(self, index) -> None:
        if self.model.isDir(index):
            self.update_title_bar_from_index(index)

    def update_title_bar_from_index(self, index) -> None:
        self.setWindowTitle(f"{TITLE} - {self.model.filePath(index)}")
