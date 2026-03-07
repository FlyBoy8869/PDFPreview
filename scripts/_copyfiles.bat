@echo off

SET /p version_string=<__version__.py
SET VERSION=%version_string:~11,6%

echo Copying additional files...
COPY .\CHANGELOG.md C:\Users\charles.cognato\PyApps\FileViewer-%VERSION%

echo ... End _copyfiles.bat
