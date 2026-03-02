import sys

from PySide6.QtWidgets import QApplication

from .gui import MainWindow
from .database.db import db

def cleanup():
    print("closing database")
    db.close()

def main() -> int:
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(cleanup)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    return app.exec()
