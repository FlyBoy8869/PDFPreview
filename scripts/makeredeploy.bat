@echo off

echo Redeploying application...

CALL .\scripts\_makedeploy.bat

CALL .\scripts\_copyfiles.bat

echo ... End makeredeploy.bat
