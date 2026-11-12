import os
import plistlib
import subprocess
import sys
from pathlib import Path

APP_NAME = "MultiCopy"
LABEL = "com.multicopy.app"


def executable_arguments():
    if getattr(sys, "frozen", False):
        return [sys.executable, "--hidden"]
    return [sys.executable, str(Path(__file__).resolve().parents[1] / "run.py"), "--hidden"]


def startup_command():
    return subprocess.list2cmdline(executable_arguments())


def launch_agent():
    return Path.home() / "Library" / "LaunchAgents" / (LABEL + ".plist")


def is_enabled():
    if sys.platform == "darwin":
        return launch_agent().exists()
    if os.name == "nt":
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
                current, _ = winreg.QueryValueEx(key, APP_NAME)
                return current == startup_command()
        except OSError:
            return False
    return False


def set_enabled(enabled):
    if sys.platform == "darwin":
        path = launch_agent()
        if enabled:
            path.parent.mkdir(parents=True, exist_ok=True)
            content = {"Label": LABEL, "ProgramArguments": executable_arguments(), "RunAtLoad": True}
            path.write_bytes(plistlib.dumps(content))
        else:
            path.unlink(missing_ok=True)
        return
    if os.name == "nt":
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as key:
            if enabled:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, startup_command())
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
        return
    raise RuntimeError("Automatic startup is supported on Windows and macOS.")
