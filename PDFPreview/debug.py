import inspect
import io
from pprint import pprint
from typing import TYPE_CHECKING, Any, cast

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


def detail_variable(var: Any) -> None:
    current_frame: FrameType | None = inspect.currentframe()
    f_code_obj = current_frame.f_back.f_code  # type: ignore  # noqa: PGH003
    caller: str = f_code_obj.co_name  # type: ignore  # noqa: PGH003
    line_no = f_code_obj.co_firstlineno
    type_ = type(var)
    logger.debug(
        f"\n{caller=} at line {line_no}\nin file: {f_code_obj.co_filename}\n{type_=}\n",
    )
