from PySide6.QtCore import QObject, QEvent


class AboutDialogFilter(QObject):
    def __init__(self, source):
        self.source = source
        super().__init__()

    def eventFilter(self, source: QObject, event: QEvent) -> bool:  # noqa: N802
        if (
                event.type() == QEvent.Type.MouseButtonRelease
                or event.type() == QEvent.Type.KeyRelease
        ):
            self.source.close()
            event.accept()
            return event.isAccepted()

        return False
