import tkinter as tk
from tkinter import messagebox

BG = "#191b1e"
PANEL = "#25282c"
TEXT = "#ededed"
MUTED = "#a5abb0"
ACCENT = "#dedede"


class Interface:
    def __init__(self, root, database, settings, on_pause, on_startup, on_exit, on_copy):
        self.root = root
        self.db = database
        self.settings = settings
        self.on_pause = on_pause
        self.on_startup = on_startup
        self.on_exit = on_exit
        self.on_copy = on_copy
        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *_: self.refresh())
        self.build()
        self.refresh()

    def button(self, parent, label, action, muted=False):
        return tk.Button(
            parent, text=label, command=action, bg=PANEL,
            fg=MUTED if muted else ACCENT,
            activebackground="#33383c", activeforeground=TEXT,
            relief="flat", bd=0, padx=11, pady=7,
            font=("Segoe UI", 10), cursor="hand2",
        )

    def build(self):
        self.root.configure(bg=BG)
        self.root.title("MultiCopy")
        self.root.geometry("760x620")
        self.root.minsize(480, 400)

        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=22, pady=(18, 10))
        tk.Label(header, text="MultiCopy", bg=BG, fg=TEXT, font=("Segoe UI", 19, "bold")).pack(side="left")
        self.pause_button = self.button(header, "Pause", self.on_pause)
        self.pause_button.pack(side="right")

        search_box = tk.Frame(self.root, bg=PANEL)
        search_box.pack(fill="x", padx=22, pady=(0, 12))
        tk.Entry(
            search_box, textvariable=self.search, bg=PANEL, fg=TEXT,
            insertbackground=TEXT, relief="flat", font=("Segoe UI", 11),
            bd=0,
        ).pack(fill="x", padx=12, pady=12)

        self.canvas = tk.Canvas(self.root, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True, padx=(22, 0))
        self.items = tk.Frame(self.canvas, bg=BG)
        self.window_id = self.canvas.create_window((0, 0), window=self.items, anchor="nw")
        self.items.bind("<Configure>", lambda _: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfigure(self.window_id, width=event.width))

        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=22, pady=14)
        self.status = tk.Label(footer, bg=BG, fg=MUTED, font=("Segoe UI", 9))
        self.status.pack(side="left")
        self.button(footer, "Exit", self.on_exit, True).pack(side="right", padx=(6, 0))
        self.button(footer, "Clear", self.clear_history, True).pack(side="right", padx=(6, 0))
        self.button(footer, "Settings", self.show_settings, True).pack(side="right")
        self.set_monitoring(self.settings.values["monitoring"])

    def refresh(self):
        for widget in self.items.winfo_children():
            widget.destroy()
        entries = self.db.get_all(self.search.get())
        if not entries:
            tk.Label(
                self.items, text="No items found", bg=BG, fg=MUTED,
                font=("Segoe UI", 11), pady=50,
            ).pack(fill="x")
        for item_id, content, pinned, created_at in entries:
            box = tk.Frame(self.items, bg=PANEL)
            box.pack(fill="x", pady=(0, 9), padx=(0, 14))
            preview = content.replace("\n", " ").strip()
            if len(preview) > 160:
                preview = preview[:157] + "..."
            tk.Label(
                box, text=preview, bg=PANEL, fg=TEXT,
                font=("Segoe UI", 10), justify="left", anchor="w",
                wraplength=570, padx=12, pady=10,
            ).pack(fill="x")
            actions = tk.Frame(box, bg=PANEL)
            actions.pack(fill="x", padx=6, pady=(0, 5))
            tk.Label(actions, text=created_at, fg=MUTED, bg=PANEL, font=("Segoe UI", 8)).pack(side="left", padx=6)
            self.button(actions, "Delete", lambda i=item_id: self.delete(i), True).pack(side="right")
            self.button(actions, "Unpin" if pinned else "Pin", lambda i=item_id: self.pin(i)).pack(side="right")
            self.button(actions, "Copy", lambda c=content: self.on_copy(c)).pack(side="right")
        self.status.configure(text=f"{self.db.count()} items saved")

    def set_monitoring(self, enabled):
        self.pause_button.configure(text="Pause" if enabled else "Resume")

    def pin(self, item_id):
        self.db.toggle_pin(item_id)
        self.refresh()

    def delete(self, item_id):
        self.db.delete(item_id)
        self.refresh()

    def clear_history(self):
        if messagebox.askyesno("Clear history", "Delete all unpinned items?", parent=self.root):
            self.db.clear()
            self.refresh()

    def show_settings(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("340x250")
        dialog.resizable(False, False)
        dialog.configure(bg=BG)
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text="Settings", fg=TEXT, bg=BG, font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=20, pady=(16, 14))
        startup = tk.BooleanVar(value=self.on_startup(None))
        tk.Checkbutton(
            dialog, text="Start with Windows", variable=startup,
            command=lambda: self._change_startup(startup),
            bg=BG, fg=TEXT, selectcolor=PANEL,
            activebackground=BG, activeforeground=TEXT,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=20)
        row = tk.Frame(dialog, bg=BG)
        row.pack(fill="x", padx=20, pady=(15, 4))
        tk.Label(row, text="History limit", bg=BG, fg=TEXT, font=("Segoe UI", 10)).pack(side="left")
        limit = tk.StringVar(value=str(self.settings.values["history_limit"]))
        tk.Entry(row, textvariable=limit, width=8, bg=PANEL, fg=TEXT, relief="flat", insertbackground=TEXT).pack(side="right")

        def save():
            try:
                value = int(limit.get())
                if value < 50 or value > 5000:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid limit", "Choose a number from 50 to 5000.", parent=dialog)
                return
            self.settings.set("history_limit", value)
            self.db.trim(value)
            self.refresh()
            dialog.destroy()

        self.button(dialog, "Save", save).pack(anchor="e", padx=20, pady=16)

    def _change_startup(self, variable):
        try:
            self.on_startup(variable.get())
        except (OSError, RuntimeError) as error:
            variable.set(self.on_startup(None))
            messagebox.showerror("Startup", str(error), parent=self.root)
