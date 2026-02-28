# C:\Users\charles.cognato\AppData\Roaming\Python\Scripts\uv.exe run
win_activate:
	cmd.exe /K .venv\Scripts\activate

ui_files:
	pyside6-uic -o ./PDFPreview/gui/ui_mainwindow.py ./PDFPreview/gui/ui_mainwindow.ui

win_ui_files:
	pyside6-uic -o PDFPreview\gui\ui_mainwindow.py PDFPreview\gui\ui_mainwindow.ui

clean:
	rm -rf ./dist
	rm -rf ./build

win_clean:
	@echo Removing pyinstaller folders...
	@IF EXIST "dist" echo Found dist folder, removing
	@IF EXIST "dist" ( RMDIR /S /Q "dist" )
	@IF EXIST "build" echo Found build folder, removing
	@IF EXIST "build" ( RMDIR /S /Q "build" )

build_no_upx:
	pyinstaller --add-data PDFPreview\gui\dialogs\ui_about.ui:PDFPreview\gui\dialogs\ --add-data Resources:.\Resources --add-data .\CHANGELOG.md:. --onedir --windowed --noconfirm --name FileViewer app.py

build:
	pyinstaller --add-data PDFPreview\gui\dialogs\ui_about.ui:PDFPreview\gui\dialogs\ --add-data Resources:.\Resources --add-data .\CHANGELOG.md:. --upx-dir C:\Users\charles.cognato\upx-5.1.0-win64\upx-5.1.0-win64 --onedir --windowed --noconfirm --name FileViewer app.py

bumppatch:
	uv version --bump patch
	uv run ./scripts/_insertversion.py

bumpminor:
	uv version --bump minor
	uv run ./scripts/_insertversion.py

bumpmajor:
	uv version --bump major
	uv run ./scripts/_insertversion.py
