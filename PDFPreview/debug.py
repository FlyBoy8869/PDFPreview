import inspect
import io
from pprint import pprint
from typing import TYPE_CHECKING, cast

from loguru import logger
from PySide6.QtCore import QModelIndex

if TYPE_CHECKING:
    from types import FrameType

    from PySide6.QtWidgets import QFileSystemModel

logger.remove()
logger.add("debug.log", level="DEBUG", mode="w")


def log_qmodelindex(index: QModelIndex, dir_dump: bool = False) -> None:  # noqa: FBT001, FBT002
    current_frame: FrameType | None = inspect.currentframe()
    name = current_frame.f_back.f_code.co_name  # type: ignore  # noqa: PGH003
    model_path = cast("QFileSystemModel", index.model()).filePath(index)
    logger.debug(
        f"\ncaller: {name}\n{type(index)=}\n{index.data()=}\n{type(index.data())=}\n{model_path=}",
    )
    dump = io.StringIO()
    dump.write("\n")
    pprint(dir(index), dump)
    if dir_dump:
        logger.debug(f"\ndir(index): {dump.getvalue()}")
