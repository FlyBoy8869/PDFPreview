@echo off

CALL .\scripts\_bump.bat %1

CALL .\scripts\_insertversion.bat

CALL .\scripts\_build.bat

CALL .\scripts\_cleandist.bat

CALL .\scripts\_makedeploy.bat

CALL .\scripts\_copyfiles.bat
