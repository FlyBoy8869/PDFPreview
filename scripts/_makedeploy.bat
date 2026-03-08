@echo off

SET /p version_string=<__version__.py
SET VERSION=%version_string:~11,6%

echo Deploying new distribution...
XCOPY .\dist\FileViewer C:\Users\charles.cognato\PyApps\FileViewer-%VERSION% /E /I /F /Y

echo ... End _makedeploy.bat
