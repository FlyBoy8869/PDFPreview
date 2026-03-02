@echo off

echo Bumping Patch Version...
CALL .\scripts\_bump.bat %1

echo Inserting new version number into __version__.py...
CALL .\scripts\_insertversion.bat

echo Building application with pyinstaller...
CALL .\scripts\_build.bat

