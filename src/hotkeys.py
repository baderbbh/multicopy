import sys
import threading

from pynput import keyboard
from PySide6.QtCore import QObject, Signal


class Hotkeys(QObject):
    open_requested = Signal()

    def __init__(self):
        super().__init__()
        self.listener = None

    def start(self):
        try:
            self.listener = keyboard.GlobalHotKeys({"<ctrl>+<shift>+v": self.open_requested.emit})
            self.listener.daemon = True
            self.listener.start()
        except Exception:
            self.listener = None

    def stop(self):
        if self.listener:
            self.listener.stop()


def paste_shortcut():
    def send():
        with keyboard.Controller() as controller:
            modifier = keyboard.Key.cmd if sys.platform == "darwin" else keyboard.Key.ctrl
            controller.press(modifier)
            controller.press("v")
            controller.release("v")
            controller.release(modifier)

    timer = threading.Timer(0.22, send)
    timer.daemon = True
    timer.start()
