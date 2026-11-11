import os
import subprocess
import sys
from pathlib import Path

APP_NAME = "MultiCopy"


def startup_command():
    if getattr(sys, "frozen", False):
        return subprocess.list2cmdline([sys.executable, "--hidden"])
    python = Path(sys.executable)
    pythonw = python.with_name("pythonw.exe")
    if pythonw.exists():
        python = pythonw
    project = Path(__file__).resolve().parents[1]
    return subprocess.list2cmdline([str(python), str(project / "run.py"), "--hidden"])


def is_enabled():
    if os.name != "nt":
        return False
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return value == startup_command()
    except OSError:
        return False


def set_enabled(enabled):
    if os.name != "nt":
        raise RuntimeError("Automatic startup is available on Windows only.")
    import winreg
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
        if enabled:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, startup_command())
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
