# MkTask

<img width="150" height="150" align="left" style="float: left; margin: 0 10px 0 0;" alt="MS-DOS logo" src="./etc/MkTask.png">

MkTask is a lightweight code editor for Batch. Execute scripts on the go, with syntax highlighting and the ability to run scripts on startup with our tasking features!

Built with Tkinter and Python.

![Preview](http://jansel.pages.dev/img/mktask/preview.png)

## Manual

Once you've loaded MkTask, you will see two sections - the **Coding** section and the **Output** section. The output section is not frequently used.

### Context Menu

To access the context menu, right-click on the coding section. The following commands are available:
* **Run file (CTRL+R):** Runs the script.
* **Run here (ALT+R):** Runs the script inside MkTask (Not recommended - may crash).
* **Open file (CTRL+O):** Opens a file to edit, run, and view its content.
* **Open script location (CTRL+F):** Opens the directory where the default code is stored.
* **Add to startup (CTRL+M):** Adds the current script to startup.
* **View startup tasks (ALT+T):** Shows all startup tasks.
* **Save file as (CTRL+S):** Saves the file with a new name.
* **Save (ALT+S):** Saves the file to the current codespace (learn more below).
* **Build EXE (ALT+B):** Builds an EXE file (learn more below).

### Code Spaces

"Codespace" refers to the current file you have open. To open a new codespace, select "Open file." To view the location of your codespace, select "Open script location."

To return to the default codespace, just open the context menu and select the relevant option.

### Building EXE

When you build an EXE, a window will open with your executable. Make sure to copy that executable to a safe location, as building again will overwrite the existing EXE.

**Important:** When running these executables, the current directory will be something like `C:\Users\user\AppData\Local\Temp\IXP001.TMP`. You will need to manually change the directory in your script. A feature to automatically set the directory is in development.

### Miscellaneous

* **Copy all (CTRL+X):** Copies all text.
* **Clear all (CTRL+B):** Clears all text.

*Note:* MkTask is a quick Batch editor and executor and should not be used as a full-fledged IDE. The most commonly used commands are Run, Make Task, and Open File.

*Another note:* MkTask automatically adds `@echo off` at the start of every script (not shown in the editor), and `pause` at the end.

### Custom Commands

We have implemented some custom Batch commands (place these commands anywhere inside your script, **must be compiled with MkTask**):
* `$noauto:` Disables auto `@echo off` and auto `pause` at the end.
* `$error:` Prints "there's been an error".

## Notes

Currently, features like undo and redo are developed but disabled due to numerous bugs (which will be fixed).

MkTask is made using Python 3.11 and compiled with PyInstaller. This means the program is somewhat heavy and slow, but optimizations are being added. **Feel free to help out and discuss!**

### Compilation Notes

If you decide to compile MkTask yourself, make sure to remove unused libraries from the `_internal` folder in the PyInstaller output. Unused libraries include:
* PIL
* Qt5
* PySide6
* SetupTools
* Numpy (& numpylibs)

These libraries are not used and are included by default in PyInstaller. Removing them will make the program faster and lighter.

Also, make sure to include the `chlorophyll` folder (located in this GitHub) inside the `_internal` folder, or the program won't start!

## Visit My Page

Visit my [page](https://jansel.pages.dev) to view my other projects. Soon I'll be hosting all binaries there, including a standalone binary.