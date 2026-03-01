from pathlib import Path

from PySide6.QtCore import QFile, Qt
from PySide6.QtGui import QColor, QPalette, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QLabel, QWidget

from config.config import LOGO, TITLE, VERSION

ABOUT_UI_PATH = Path(__file__).resolve().parent / "ui_about.ui"


def create_about_dialog() -> QWidget:
    p = QPalette()
    color: str = p.color(QPalette.ColorRole.Window).name(QColor.NameFormat.HexArgb)
    dialog_stylesheet: str = (
        f"QWidget {{background-color: {color}; border-radius: 20px;}}"
    )

    about_file = QFile(ABOUT_UI_PATH)
    loader = QUiLoader()
    about_file.open(QFile.OpenModeFlag.ReadOnly)
    about_window = loader.load(about_file)
    about_file.close()

    about_window.setWindowFlags(
        about_window.windowFlags() | Qt.WindowType.FramelessWindowHint,
    )
    about_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    about_window.setStyleSheet(dialog_stylesheet)
    about_window.setWindowTitle(TITLE)
    about_window.setWindowModality(Qt.WindowModality.ApplicationModal)

    if logo_label := about_window.findChild(QLabel, "lbl_logo"):
        logo_label.setPixmap(QPixmap(LOGO.as_posix()))

    if version_label := about_window.findChild(QLabel, "lbl_about"):
        version_label.setTextFormat(Qt.TextFormat.RichText)
        version_label.setText(
            f"<center><h1>{TITLE}</h1></center>"
            f"<center><h4>Version: {VERSION}</h4></center>"
            "<center>Author: Charles Cognato</center>"
            "<center>Email: charlescognato@gmail.com</center>"
            "<center>Copyright \u00A9 2026 CharlesIndustries</center>",
        )

    return about_window
