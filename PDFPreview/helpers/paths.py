from pathlib import Path
from config import FILES, IMAGES, ICONS


class Paths:
    DESIGNHISTORY: Path = Path(r"\\walfs02\designhistory$")
    PROE: Path = Path(r"\\b2srvproe01\server")
    WALLPAPER: Path =  IMAGES / "wallpaper.png"
    network_shares_available: bool = DESIGNHISTORY.exists() and PROE.exists()

    @classmethod
    def file(cls, file: str) -> str:
        return (FILES / file).resolve().as_posix()

    @classmethod
    def icon(cls, icon: str) -> str:
        return (ICONS / icon).resolve().as_posix()

    @classmethod
    def image(cls, image: str) -> str:
        return (IMAGES / image).resolve().as_posix()

    @staticmethod
    def validate_path(path: Path) -> bool:
        return path.exists()
