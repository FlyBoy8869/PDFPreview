import sys

from PySide6.QtWidgets import QApplication

from .helpers.paths import Paths
from .gui import MainWindow
from .database.db import db

from config.config import DATABASE_FILE, DATABASE_PATH
from PDFPreview.eventfilters.global_filter import GlobalEventFilter


def cleanup():
    db.close()

    if Paths.network_shares_available:
        backup_name = f'{DATABASE_FILE.rsplit(".", 1)[0]}.bak'
        dest = DATABASE_PATH / backup_name
        (DATABASE_PATH / DATABASE_FILE).copy(dest)


def main() -> int:
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(cleanup)
    app.setStyle("Fusion")

    window = MainWindow()

    global_filter = GlobalEventFilter(window.show_wallpaper)
    app.installEventFilter(global_filter)

    window.show()

    return app.exec()
