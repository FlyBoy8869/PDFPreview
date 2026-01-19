ui_files:
	/Users/charles/pyvenvs/general-dev/bin/pyside6-uic -o ./PDFPreview/gui/ui_mainwindow.py ./PDFPreview/gui/ui_mainwindow.ui

mac_clean:
	rm -rf ./dist
	rm -rf ./build

build_no_upx:
	pyinstaller --add-data PDFPreview\gui\ui_about.ui:PDFPreview\gui\ --onedir --windowed --noconfirm --name PDFViewer app.py

build:
	pyinstaller --add-data PDFPreview\gui\ui_about.ui:PDFPreview\gui\ --upx-dir C:\Users\charles.cognato\upx-5.1.0-win64\upx-5.1.0-win64 --onedir --windowed --noconfirm --name PDFViewer app.py
