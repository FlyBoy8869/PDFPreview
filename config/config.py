import platform
from pathlib import Path
from typing import Literal

import tomllib

from __version__ import VERSION  # noqa: F401

TITLE = "FileViewer"

PATH_PREFIX: Literal["file://", "file:///"] = (
    "file://" if "macOS" in platform.platform() else "file:///"
)

ROOT = Path(__file__).resolve().parent.parent
RESOURCES = ROOT / "Resources"

FILES = RESOURCES / "Files"
FAVORITES: Path = FILES / "favorites.dat"
SPLASH_FILE: Path = FILES / "FileViewerSplash.html"

IMAGES = RESOURCES / "Images"
LOGO: Path = IMAGES / "logo.png"

with (FILES / "config.toml").open(
    mode="rb",
) as config_file:
    config = tomllib.load(config_file)

ADOBE_ACROBAT_PATH = config["paths"]["acrobat"]
