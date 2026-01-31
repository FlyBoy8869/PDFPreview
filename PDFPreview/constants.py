import platform
from pathlib import Path
from typing import Literal

RESOURCES = Path(__file__).parent.parent / "Resources"
FILES = RESOURCES / "Files"
IMAGES = RESOURCES / "Images"

TITLE = "FileViewer"

FAVORITES: Path = FILES / "favorites.dat"
ABOUT_UI_PATH: Path = Path(__file__).parent / "gui/ui_about.ui"

SPLASH_FILE: Path = FILES / "FileViewerSplash.html"
LOGO: Path = IMAGES / "logo.png"
print(f"{LOGO=}")

PATH_PREFIX: Literal["file://", "file:///"] = (
    "file://" if "macOS" in platform.platform() else "file:///"
)
