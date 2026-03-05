@echo off

echo Building application with pyinstaller...
C:\Users\charles.cognato\AppData\Roaming\Python\Scripts\uv.exe run pyinstaller --add-data PDFPreview\gui\dialogs\ui_about.ui:PDFPreview\gui\dialogs\ --add-data Resources:.\Resources --add-data .\CHANGELOG.md:. --upx-dir C:\Users\charles.cognato\upx-5.1.0-win64\upx-5.1.0-win64 --onedir --windowed --noconfirm --name FileViewer app.py
