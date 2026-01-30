ui_files:
	pyside6-uic -o ./PDFPreview/gui/ui_mainwindow.py ./PDFPreview/gui/ui_mainwindow.ui

mac_clean:
	rm -rf ./dist
	rm -rf ./build

build_no_upx:
	pyinstaller --add-data PDFPreview\gui\ui_about.ui:PDFPreview\gui\ --add-data PDFPreview\gui\logo.png:PDFPreview\gui --onedir --windowed --noconfirm --name FileViewer app.py

build:
	pyinstaller --add-data PDFPreview\gui\ui_about.ui:PDFPreview\gui\ --add-data PDFPreview\gui\logo.png:PDFPreview\gui --add-data .\FileViewerSplash.html:. --upx-dir C:\Users\charles.cognato\upx-5.1.0-win64\upx-5.1.0-win64 --onedir --windowed --noconfirm --name FileViewer app.py
