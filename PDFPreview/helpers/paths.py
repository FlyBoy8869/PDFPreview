from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
RESOURCES: Path = BASE_DIR / "Resources"
FILES: Path = RESOURCES / "Files"
IMAGES: Path = RESOURCES / "Images"
ICONS: Path = IMAGES / "Icons"


class Paths:
    @classmethod
    def file(cls, file: str) -> str:
        return (FILES / file).resolve().as_posix()

    @classmethod
    def icon(cls, icon: str) -> str:
        return (ICONS / icon).resolve().as_posix()

    @classmethod
    def image(cls, image: str) -> str:
        return (IMAGES / image).resolve().as_posix()
