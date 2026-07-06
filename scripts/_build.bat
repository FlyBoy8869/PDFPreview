@echo off

echo Building application with pyinstaller...
C:\Users\charles.cognato\AppData\Roaming\Python\Scripts\uv.exe run pyinstaller --add-data PDFPreview\gui\dialogs\ui_about.ui:PDFPreview\gui\dialogs\ --add-data Resources:.\Resources --onedir --windowed --noconfirm --name FileViewer app.pyw

echo ... End _build.bat
