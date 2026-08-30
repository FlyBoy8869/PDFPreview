import os
import sys

from PDFPreview.main import main

if __name__ == "__main__":
    os.environ["QT_LOGGING_RULES"] = "qt.gui.icc=false"
    sys.exit(main())
