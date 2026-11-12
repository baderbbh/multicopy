# MultiCopy

MultiCopy is a small clipboard history manager for Windows and macOS. It saves copied text and images so you can find and use them again.

## Features

- Save text and images automatically
- Search copied text
- Browse all copies, favorites, links, images, or text
- Pin, delete, copy, or paste saved items
- Keep one entry per unique copy, moving it to the top when copied again
- Clean desktop interface with a custom MultiCopy app icon
- Pause and resume monitoring
- Open the window with `Ctrl + Shift + V`
- Keep running in the system tray or macOS menu bar
- Optionally launch when you sign in
- Set a history limit and automatically remove older unpinned items
- Export history as text or JSON

## Requirements

- Windows 10/11 or macOS
- Python 3.11 or newer

## Setup

Clone the repository:

```bash
git clone https://github.com/baderbbh/multicopy.git
cd multicopy
```

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

**macOS Terminal**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run.py
```

Closing the window keeps MultiCopy in the system tray or menu bar, where supported. Use **Exit** to stop it completely.

On macOS, allow the application under **System Settings → Privacy & Security → Accessibility** if you want global shortcuts and quick paste to work. You may also need to approve input monitoring. If the shortcut does not work, open MultiCopy from the menu bar instead.

Quick paste copies the selected item to the clipboard, hides MultiCopy, then sends the paste shortcut to the active application. Some applications or macOS permissions can prevent the automatic paste; the item will still be on the clipboard to paste manually.

## Tests

Windows:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## Use MultiCopy without a terminal

Build a desktop app once, move it to a permanent folder, and enable startup from Settings.
You need Python only to build MultiCopy, not to run the finished app.

**Windows**

In PowerShell, from the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
powershell -ExecutionPolicy Bypass -File scripts\build_windows.ps1
```

The build is saved as `dist\MultiCopy.exe`. Copy the executable to a permanent location such as `%LOCALAPPDATA%\Programs\MultiCopy\MultiCopy.exe`. Double-click it to launch. Once it is running, close the window to keep it in the system tray. The tray menu has **Open MultiCopy**, **Pause monitoring**, and **Exit**.

In **Settings**, select **Launch when I sign in** and save. MultiCopy will then start quietly when you next sign in to Windows. You can disable it from the same settings page. If you move or rename the executable, disable startup first and enable it again from its new location. Keep the executable rather than moving it out of its permanent folder.

Windows may show a SmartScreen warning for an unsigned application built locally. Only run executables you've built yourself or obtained from a source you trust.

**macOS**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
sh scripts/build_macos.sh
```

Move `dist/MultiCopy.app` to Applications and launch it. You can enable sign-in startup in Settings. macOS may require Accessibility and Input Monitoring permission for keyboard shortcuts and quick paste. The macOS build must be made on a Mac; a Windows build cannot produce a macOS application.

**Only one copy runs at a time.** Opening MultiCopy again asks the existing app to show its window. When MultiCopy is running, its keyboard shortcut does not require VS Code or a terminal.

The app must stay running in the tray or menu bar for clipboard monitoring and the global shortcut to work. Exit stops both. Launch at sign-in is optional and is disabled by default.

## Data and privacy

Clipboard history is saved locally and is **not encrypted**. Be careful copying passwords, recovery codes, or other private text. Images are stored as PNG data in the database. MultiCopy does not sync anything online.

Windows data folder: `%LOCALAPPDATA%\MultiCopy`

macOS data folder: `~/Library/Application Support/MultiCopy`

To delete all saved data, disable launch at sign-in, exit MultiCopy, and delete the data folder.

Images larger than 10 MB after PNG conversion are skipped. The text export marks images as omitted; the JSON export includes images as base64-encoded PNG data. Deleted unpinned entries cannot be restored from the app.

## Notes

- Only content copied while MultiCopy is running can be saved.
- Startup must be enabled in settings; it is not enabled by default.
- Clipboard images and global shortcuts depend on operating-system permissions and clipboard formats.

## License

MIT. See [LICENSE](LICENSE).
