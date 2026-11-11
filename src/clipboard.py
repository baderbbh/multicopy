import tkinter as tk


class ClipboardWatcher:
    def __init__(self, root, on_copy, interval=600):
        self.root = root
        self.on_copy = on_copy
        self.interval = interval
        self.enabled = True
        self.last_text = None
        self.job = None

    def start(self):
        self.check()

    def check(self):
        try:
            text = self.root.clipboard_get()
        except (tk.TclError, UnicodeError):
            text = None
        if text != self.last_text:
            self.last_text = text
            if self.enabled and text and text.strip():
                self.on_copy(text)
        self.job = self.root.after(self.interval, self.check)

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)
        if self.enabled:
            self.last_text = self.read_current()

    def read_current(self):
        try:
            return self.root.clipboard_get()
        except (tk.TclError, UnicodeError):
            return None

    def copied_by_app(self, text):
        self.last_text = text

    def stop(self):
        if self.job:
            self.root.after_cancel(self.job)
            self.job = None
