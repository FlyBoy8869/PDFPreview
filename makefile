ui_files:
	/Users/charles/pyvenvs/general-dev/bin/pyside6-uic -o ./PDFPreview/gui/ui_mainwindow.py ./PDFPreview/gui/ui_mainwindow.ui

mac_clean:
	rm -rf ./dist
	rm -rf ./build
