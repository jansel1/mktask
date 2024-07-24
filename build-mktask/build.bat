
@echo off
REM 		MADE FOR BUILDING MKTASK
REM		FACILITATES IT
REM 		WRITTEN WITH MKTASK : )


pyinstaller --onedir --windowed --icon ..\mktask\MkTask.ico "..\mktask\core.py"

cls
echo Done with PyInstaller - copying required files

xcopy ".\chlorophyll" ".\dist\core\_internal"
xcopy "..\mktask\MkTask.ico" ".\dist\core"
xcopy "..\mktask\MkExe.bat" ".\dist\core"

cls
echo Done copying files, deleting useless libraries
cd .\dist\core

del ".\_internal\numpy"
del ".\_internal\numpy.libs"
del ".\_internal\PIL"
del ".\_internal\PyQt5"

pause