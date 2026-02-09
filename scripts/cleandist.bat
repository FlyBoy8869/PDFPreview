@echo off

REM Enable delayed expansion to handle variables correctly within the loop
setlocal EnableDelayedExpansion

REM Define the name of the file you want to read
set "filename=Files Safe to Delete from dist.txt"

echo Removing unneeded distribution files...

REM Loop through each line in the file
for /f "tokens=*" %%a in ('type "%filename%"') do (
    set "line=%%a"
    echo deleting !line!
    IF EXIST ".\dist\FileViewer\_internal\PySide6\%%a" ( del /Q .\dist\FileViewer\_internal\PySide6\%%a )
)

echo deleting qml folder...
IF EXIST ".\dist\FileViewer\_internal\PySide6\qml" ( RMDIR /S /Q ".\dist\FileViewer\_internal\PySide6\qml" )
echo deleting translations folder...
IF EXIST ".\dist\FileViewer\_internal\PySide6\translations" ( RMDIR /S /Q ".\dist\FileViewer\_internal\PySide6\translations" )

endlocal
