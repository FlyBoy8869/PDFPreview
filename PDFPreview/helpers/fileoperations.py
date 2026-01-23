try:
    from os import startfile  # type: ignore  # noqa: PGH003
except ImportError:
    import webbrowser
    from collections.abc import Callable

    startfile: Callable[..., bool] = webbrowser.open_new_tab

from PySide6.QtCore import QUrl


def open_file(path: str) -> None:
    """Open file in the default application."""
    startfile(QUrl.fromLocalFile(path).url())
