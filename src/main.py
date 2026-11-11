import argparse
import tkinter as tk

from src.clipboard import ClipboardWatcher
from src.database import Database
from src.settings import Settings
from src.startup import is_enabled, set_enabled
from src.tray import Tray
from src.ui import Interface


class MultiCopy:
    def __init__(self, hidden=False):
        self.root = tk.Tk()
        self.db = Database()
        self.settings = Settings()
        self.watcher = ClipboardWatcher(self.root, self.on_new_copy)
        self.interface = Interface(
            self.root, self.db, self.settings,
            self.toggle_monitoring, self.startup, self.quit, self.copy_text,
        )
        self.root.protocol("WM_DELETE_WINDOW", self.hide)
        self.tray = Tray(
            lambda: self.root.after(0, self.show),
            lambda: self.root.after(0, self.toggle_monitoring),
            lambda: self.root.after(0, self.quit),
            lambda: self.settings.values["monitoring"],
        )
        self.tray.start()
        self.watcher.set_enabled(self.settings.values["monitoring"])
        self.watcher.start()
        if hidden:
            self.hide()

    def on_new_copy(self, text):
        if self.db.add(text, self.settings.values["history_limit"]):
            self.interface.refresh()

    def copy_text(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.watcher.copied_by_app(text)

    def toggle_monitoring(self):
        enabled = not self.settings.values["monitoring"]
        self.settings.set("monitoring", enabled)
        self.watcher.set_enabled(enabled)
        self.interface.set_monitoring(enabled)
        self.tray.refresh()

    def startup(self, enabled):
        if enabled is None:
            return is_enabled()
        set_enabled(enabled)

    def show(self):
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def hide(self):
        self.root.withdraw()

    def quit(self):
        self.watcher.stop()
        self.tray.stop()
        self.db.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hidden", action="store_true")
    args = parser.parse_args()
    MultiCopy(hidden=args.hidden).run()


if __name__ == "__main__":
    main()
