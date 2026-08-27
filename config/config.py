import os
import platform
from pathlib import Path
from typing import Literal, Any

import tomllib

from __version__ import VERSION  # noqa: F401

TITLE = "FileViewer"
DATABASE_FILE = "database.json"

OS = "macOS" if "macOS" in platform.platform() else "Windows"

PATH_PREFIX: Literal["file://", "file:///"] = (
    "file://" if OS == "macOS" else "file:///"
)

ROOT: Path = Path(__file__).resolve().parent.parent
RESOURCES: Path = ROOT / "Resources"

FILES: Path = RESOURCES / "Files"
SPLASH_FILE: Path = FILES / "FileViewerSplash.html"

IMAGES: Path = RESOURCES / "Images"
ICONS: Path = IMAGES / "Icons"
LOGO: Path = IMAGES / "logo.png"

if OS == "macOS":
    _config_path = Path(os.path.expanduser(Path("~/Library/Preferences/FileViewer")))
    SUPPORT_PATH = Path(os.path.expanduser(Path("~/Library/Application Support/FileViewer")))
else:
    _config_path = Path(os.path.expandvars(Path("%APPDATA%/FileViewer")))
    SUPPORT_PATH = Path(os.path.expandvars(Path("%APPDATA%/FileViewer")))

if not SUPPORT_PATH.exists():
    SUPPORT_PATH.mkdir(parents=True)

with (_config_path / "config.toml").open(
        mode="rb",
) as config_file:
    config: dict[str, Any] = tomllib.load(config_file)

config["OS"] = OS

ADOBE_ACROBAT_PATH = config["paths"]["acrobat"]
WALLPAPER = IMAGES / "wallpaper.png"

__all__ = [
    "VERSION",
    "TITLE",
    "DATABASE_FILE",
    "DATABASE_PATH",
    "OS",
    "PATH_PREFIX",
    "ROOT",
    "RESOURCES",
    "FILES",
    "SPLASH_FILE",
    "IMAGES",
    "ICONS",
    "LOGO",
    "ADOBE_ACROBAT_PATH",
    "WALLPAPER",
    "config"
]
