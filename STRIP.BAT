rem Run this script inside the directory of your compiled MkTask
rem Must be in 'onedir' mode (pyinstaller)

del ./_internal/numpy
del ./_internal/numpylibs
del ./_internal/PIL 
del ./_internal/PyQt5
del ./_internal/PySide6

rem Note: Your executable may not have these libraries in it.
rem It all depends if you have them installed
rem PyInstaller loads a bunch of them, even if you're not using those libraries
rem in your project.