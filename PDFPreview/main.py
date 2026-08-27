import sys

from PySide6.QtWidgets import QApplication

from .helpers.paths import Paths
from .gui import MainWindow
from .database.db import db

from config.config import DATABASE_FILE, SUPPORT_PATH


def cleanup():
    db.close()

    if Paths.network_shares_available:
        backup_name = f'{DATABASE_FILE.rsplit(".", 1)[0]}.bak'
        dest = SUPPORT_PATH / backup_name
        (SUPPORT_PATH / DATABASE_FILE).copy(dest)


def main() -> int:
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(cleanup)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    return app.exec()
