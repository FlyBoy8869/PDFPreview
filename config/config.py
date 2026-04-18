import os
import platform
from pathlib import Path
from typing import Literal

import tomllib

from __version__ import VERSION  # noqa: F401

TITLE = "FileViewer"

_OS = "macOS" if "macOS" in platform.platform() else "windows"

PATH_PREFIX: Literal["file://", "file:///"] = (
    "file://" if _OS == "macOS" else "file:///"
)

ROOT = Path(__file__).resolve().parent.parent
RESOURCES = ROOT / "Resources"

FILES = RESOURCES / "Files"
SPLASH_FILE: Path = FILES / "FileViewerSplash.html"

IMAGES = RESOURCES / "Images"
LOGO: Path = IMAGES / "logo.png"

if _OS == "macOS":
    _config_path = Path(os.path.expanduser(Path("~/Library/Preferences/FileViewer")))
    DATABASE_PATH = Path(os.path.expanduser(Path("~/Library/Application Support/FileViewer")))
else:
    _config_path = Path(os.path.expandvars(Path("%APPDATA%/FileViewer")))
    DATABASE_PATH = Path(os.path.expandvars(Path("%APPDATA%/FileViewer")))

if not DATABASE_PATH.exists():
    DATABASE_PATH.mkdir(parents=True)

with (_config_path / "config.toml").open(
        mode="rb",
) as config_file:
    config = tomllib.load(config_file)

ADOBE_ACROBAT_PATH = config["paths"]["acrobat"]
