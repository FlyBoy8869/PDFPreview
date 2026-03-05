@echo off

echo Deploying new distribution...
XCOPY .\dist\FileViewer C:\Users\charles.cognato\PyApps\FileViewer /E /I /F /Y
