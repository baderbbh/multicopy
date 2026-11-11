
# MultiCopy

A lightweight clipboard history manager for Windows.

MultiCopy saves copied text so you can easily find and reuse it later. It runs in the background and stores your clipboard history locally.

## Features

- Automatically saves copied text
- Search clipboard history
- Pin important entries
- Copy saved text again
- Delete individual entries
- Clear clipboard history
- Pause and resume monitoring
- Run in the Windows system tray
- Start automatically with Windows
- Set a limit for saved history

## Built With

- Python
- Tkinter
- SQLite
- pystray
- Pillow

## Getting Started

### Requirements

- Windows 10 or 11
- Python 3.11 or newer
- Git

### Installation

1. Clone the repository:

   ```powershell
   git clone https://github.com/baderbbh/multicopy.git
   cd multicopy
   ```

2. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

3. Install the required packages:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
   ```

### Running MultiCopy

Run the application from the project folder:

```powershell
.\.venv\Scripts\python.exe run.py
```

MultiCopy will open in a desktop window. You can close the window to keep it running in the system tray.

To stop MultiCopy completely, select Exit from the system tray menu.

### Running Tests

Run the automated tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

If everything works, the tests should finish with `OK`.

## Troubleshooting

### Python is not recognized

Make sure Python is installed and added to your system PATH.

You can check your Python version using:

```powershell
python --version
```

### The .venv Python executable is not recognized

This usually means the virtual environment has not been created in the project folder.

Run:

```powershell
python -m venv .venv
```

Then install the packages again:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

### Missing Python packages

If the application reports a missing module, install the requirements again:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## Privacy

MultiCopy stores clipboard history locally on your computer. It does not upload copied text to a server.

Clipboard history may contain sensitive information, so you can pause monitoring or delete saved entries when needed.

The local database is not encrypted.

## Project Status

MultiCopy is currently in development. Features and behavior may change as the project is tested and improved.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
