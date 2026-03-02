@echo off

echo Bumping Patch Version...
CALL .\scripts\bump.bat %1

echo Updating __version__.py file...
CALL .\scripts\insertversion.bat

echo Building application with pyinstaller...
CALL .\scripts\build.bat
