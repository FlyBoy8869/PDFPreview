@ECHO off

SET /p version_string=<__version__.py
SET VERSION=%version_string:~11,6%

ECHO Copying CHANGELOG.md...
COPY .\CHANGELOG.md C:\Users\charles.cognato\PyApps\FileViewer-%VERSION%

IF NOT EXIST %APPDATA%\FileViewer (
    ECHO %APPDATA%\FileViewer does not exist... creating
    MKDIR %APPDATA%\FileViewer
)

IF NOT EXIST %APPDATA%\FileViewer\config.toml (
    ECHO copying configuration file to %APPDATA%\FileViewer
    COPY .\Resources\Files\config.toml %APPDATA%\FileViewer\config.toml
)

ECHO ... End _copyfiles.bat
