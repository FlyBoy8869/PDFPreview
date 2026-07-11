from pathlib import Path

from PySide6.QtCore import QObject, Signal, QUrl
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebEngineWidgets import QWebEngineView

pdf_toolbar: dict[bool, str] = {
    True: "toolbar=0",
    False: "",
}

image_extensions: list[str] = [".bmp", ".gif", ".jpg", ".jpeg", ".png", ".svg", ".webp"]


class ViewerManager(QObject):
    fileLoaded = Signal(str)

    def __init__(self, viewer: QWebEngineView):
        super().__init__()
        self.browser = viewer

        # this string gets appended to the url to show or hide the PDF viewer toolbar
        self.hide_toolbar: str = ""

        self.browser.page().settings().setAttribute(
            QWebEngineSettings.WebAttribute.PluginsEnabled,
            True,
        )
        self.browser.page().settings().setAttribute(
            QWebEngineSettings.WebAttribute.PdfViewerEnabled,
            True,
        )

    def view_file(self, path: Path):
        """Loads the file pointed to by index into the viewing pane."""
        # do not load directories into the viewer i.e., navigable elements
        if path.is_dir():
            return

        url: QUrl = QUrl.fromLocalFile(path)
        url.setFragment(f"{self.hide_toolbar}&navpanes=0")

        self.browser.setUrl(url)

        if path.suffix.lower() in image_extensions:
            self.browser.setZoomFactor(1.00)

        self.fileLoaded.emit(str(path))

    def toggle_toolbar(self, visible: bool) -> None:
        self.hide_toolbar = pdf_toolbar[visible]