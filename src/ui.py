import base64
import json
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QFileDialog, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QMenu, QMessageBox, QPushButton,
    QScrollArea, QSizePolicy, QSpinBox, QVBoxLayout, QWidget,
)

from src.icons import app_icon, icon_pixmap
from src.resources import asset_path


STYLE = """
QWidget {
    color: #f1f2f3;
    font-family: 'Segoe UI', 'Arial';
    font-size: 13px;
}
QMainWindow, QDialog, QWidget#shell, QWidget#mainContent { background: #111316; }
QLabel, QWidget#entryDetails { background: transparent; }
QFrame#sidebar {
    background: #191b1f;
    border-right: 1px solid #292c31;
}
QLabel#brand { font-size: 23px; font-weight: 700; }
QLabel#brandIcon { background: transparent; }
QLabel#caption, QLabel#muted, QLabel#meta { color: #9a9da5; }
QLabel#heading { font-size: 26px; font-weight: 700; }
QLabel#itemTitle { font-size: 15px; font-weight: 600; }
QLabel#itemBody { color: #afb2ba; font-size: 12px; }
QLabel#sectionLabel { color: #9a9da5; font-size: 11px; font-weight: 600; }
QLabel#count { color: #a8adb5; font-size: 12px; }
QLineEdit, QComboBox, QSpinBox {
    background: #24272c;
    border: 1px solid #363a40;
    border-radius: 13px;
    padding: 11px 13px;
    selection-background-color: #347b77;
}
QLineEdit:focus { border: 1px solid #5cbdb6; }
QPushButton {
    border: none;
    background: transparent;
    border-radius: 11px;
    padding: 9px 12px;
}
QPushButton:hover { background: #30343a; }
QPushButton#nav {
    text-align: left;
    padding: 11px 13px;
    color: #d4d6da;
    font-size: 14px;
}
QPushButton#nav:checked {
    background: #294a47;
    color: #eafdfa;
    font-weight: 600;
}
QPushButton#nav:hover:!checked { background: #282c30; }
QPushButton#action {
    background: #2d3036;
    border-radius: 11px;
    min-width: 19px;
    min-height: 22px;
    font-size: 17px;
    padding: 7px 9px;
}
QPushButton#action:hover { background: #40454d; }
QPushButton#accent { background: #376f6a; font-weight: 600; }
QPushButton#accent:hover { background: #438982; }
QPushButton#danger:hover { background: #4a292b; }
QFrame#entry { background: #1d2025; border: 1px solid #30343a; border-radius: 19px; }
QWidget#entryDetails QLabel { background: transparent; }
QFrame#tile { background: #2b3036; border-radius: 12px; }
QLabel#tag { background: #2e3239; border-radius: 7px; padding: 4px 8px; color: #c5ced1; font-size: 11px; }
QFrame#rule { background: #35393e; max-height: 1px; }
QScrollArea { border: none; background: transparent; }
QScrollArea QWidget#historyContent { background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; }
QScrollBar:vertical { background: transparent; width: 9px; }
QScrollBar::handle:vertical { background: #434850; border-radius: 4px; min-height: 28px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QCheckBox { spacing: 10px; }
QMenu { background: #26292e; border: 1px solid #3b4046; padding: 6px; }
QMenu::item { padding: 8px 20px; border-radius: 5px; }
QMenu::item:selected { background: #37534f; }
"""


def line():
    rule = QFrame()
    rule.setObjectName("rule")
    rule.setFixedHeight(1)
    return rule


def label(text, role=None):
    widget = QLabel(text)
    if role:
        widget.setObjectName(role)
    return widget


def button(text, callback, role=None, tip=None):
    widget = QPushButton(text)
    if role:
        widget.setObjectName(role)
    if tip:
        widget.setToolTip(tip)
        widget.setAccessibleName(tip)
    widget.clicked.connect(callback)
    return widget


def sidebar_button(name, title, callback):
    item = button(title, callback, "nav")
    item.setIcon(app_icon(name))
    item.setIconSize(QSize(22, 22))
    item.setMinimumHeight(48)
    return item


def timestamp(value):
    try:
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return date.astimezone().strftime("%b %d, %I:%M %p").replace(" 0", " ")
    except (TypeError, ValueError):
        return str(value or "")[:16]


class ElidedLabel(QLabel):
    def __init__(self, text, role=None):
        super().__init__()
        self.full_text = text
        if role:
            self.setObjectName(role)
        self.setMinimumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setToolTip(text)
        self.update_text()

    def update_text(self):
        width = max(0, self.contentsRect().width())
        self.setText(self.fontMetrics().elidedText(
            self.full_text, Qt.TextElideMode.ElideRight, width
        ))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_text()


class SettingsDialog(QDialog):
    def __init__(self, settings, startup_get, startup_set, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.startup_set = startup_set
        self.setWindowTitle("Settings")
        self.setMinimumWidth(420)
        self.setStyleSheet(STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(15)
        heading = label("Settings", "heading")
        layout.addWidget(heading)
        self.startup = QCheckBox("Launch when I sign in")
        self.startup.setChecked(startup_get())
        layout.addWidget(self.startup)
        layout.addWidget(label("Maximum unpinned items", "muted"))
        self.limit = QSpinBox()
        self.limit.setRange(50, 5000)
        self.limit.setValue(settings.values["history_limit"])
        layout.addWidget(self.limit)
        layout.addWidget(label("Remove unpinned items after", "muted"))
        self.age = QComboBox()
        for title, days in [("Never", 0), ("1 day", 1), ("7 days", 7), ("30 days", 30), ("90 days", 90)]:
            self.age.addItem(title, days)
        self.age.setCurrentIndex(self.age.findData(settings.values["auto_delete_days"]))
        layout.addWidget(self.age)
        save = button("Save settings", self.save, "accent")
        layout.addWidget(save)

    def save(self):
        try:
            self.startup_set(self.startup.isChecked())
            self.settings.set("history_limit", self.limit.value())
            self.settings.set("auto_delete_days", self.age.currentData())
        except (OSError, RuntimeError) as error:
            QMessageBox.warning(self, "Settings", str(error))
            return
        self.accept()


class Interface(QMainWindow):
    copy_requested = Signal(object, bool)
    monitoring_requested = Signal()
    exit_requested = Signal()

    SECTIONS = (
        ("all", "copy", "All copies"),
        ("favorites", "star", "Favorites"),
        ("link", "link", "Links"),
        ("image", "image", "Images"),
        ("text", "text", "Text"),
    )

    def __init__(self, database, settings, startup_get, startup_set):
        super().__init__()
        self.db = database
        self.settings = settings
        self.startup_get = startup_get
        self.startup_set = startup_set
        self.on_close = None
        self.section = "all"
        self.setWindowTitle("MultiCopy")
        self.resize(1180, 760)
        self.setMinimumSize(850, 560)
        self.setStyleSheet(STYLE)
        self.build()
        self.refresh()

    def build(self):
        shell = QWidget()
        shell.setObjectName("shell")
        self.setCentralWidget(shell)
        body = QHBoxLayout(shell)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(282)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(24, 39, 20, 24)
        side.setSpacing(8)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(12)
        brand_icon = QLabel()
        brand_icon.setObjectName("brandIcon")
        brand_icon.setFixedSize(42, 42)
        logo = QPixmap(str(asset_path("src", "assets", "multicopy-logo.png")))
        if not logo.isNull():
            brand_icon.setPixmap(logo.scaled(42, 42, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        brand_text = QVBoxLayout()
        brand_text.setSpacing(2)
        brand_text.addWidget(label("MultiCopy", "brand"))
        brand_text.addWidget(label("Clipboard History Manager", "caption"))
        brand_row.addWidget(brand_icon, 0, Qt.AlignmentFlag.AlignTop)
        brand_row.addLayout(brand_text, 1)
        side.addLayout(brand_row)
        side.addSpacing(30)

        self.navigation = {}
        for key, icon_name, title in self.SECTIONS:
            entry = sidebar_button(icon_name, title, lambda checked=False, k=key: self.select_section(k))
            entry.setCheckable(True)
            self.navigation[key] = entry
            side.addWidget(entry)

        side.addSpacing(23)
        side.addWidget(line())
        side.addSpacing(20)
        monitor = QHBoxLayout()
        monitor.setSpacing(9)
        self.monitor_dot = label("●")
        monitor.addWidget(self.monitor_dot)
        self.monitor_text = label("Monitoring")
        monitor.addWidget(self.monitor_text)
        monitor.addStretch()
        self.monitor_button = button("", self.monitoring_requested.emit, "accent")
        monitor.addWidget(self.monitor_button)
        side.addLayout(monitor)
        self.monitor_caption = label("Auto-saving copies", "caption")
        side.addWidget(self.monitor_caption)
        side.addSpacing(13)
        side.addWidget(label("Ctrl   +   Shift   +   V", "muted"))
        side.addWidget(label("Open MultiCopy", "caption"))
        side.addStretch()
        side.addWidget(line())
        side.addSpacing(10)
        side.addWidget(sidebar_button("settings", "Settings", self.open_settings))
        side.addWidget(sidebar_button("export", "Export history", self.export_history))
        side.addWidget(sidebar_button("about", "About", self.open_about))
        body.addWidget(sidebar)

        content = QWidget()
        content.setObjectName("mainContent")
        main = QVBoxLayout(content)
        main.setContentsMargins(30, 43, 24, 18)
        main.setSpacing(20)
        header = QHBoxLayout()
        header.setSpacing(25)
        titles = QVBoxLayout()
        titles.setSpacing(6)
        self.heading = label("All copies", "heading")
        titles.addWidget(self.heading)
        self.subheading = label("", "muted")
        titles.addWidget(self.subheading)
        header.addLayout(titles, 2)
        self.search = QLineEdit()
        self.search.setPlaceholderText("⌕   Search copied text...")
        self.search.setMinimumHeight(49)
        self.search.textChanged.connect(self.refresh)
        header.addWidget(self.search, 3)
        main.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.inner = QWidget()
        self.inner.setObjectName("historyContent")
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.entries = QVBoxLayout(self.inner)
        self.entries.setSpacing(12)
        self.entries.setContentsMargins(0, 3, 6, 3)
        self.scroll.setWidget(self.inner)
        main.addWidget(self.scroll)
        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(button("Clear unpinned history", self.clear_history))
        main.addLayout(footer)
        body.addWidget(content, 1)
        self.set_monitoring(self.settings.values["monitoring"])
        self.update_navigation()

    def update_navigation(self):
        for key, entry in self.navigation.items():
            entry.setChecked(key == self.section)

    def select_section(self, section):
        self.section = section
        self.update_navigation()
        self.refresh()

    def set_monitoring(self, enabled):
        self.monitor_dot.setStyleSheet("color: #5fca79;" if enabled else "color: #8e9199;")
        self.monitor_text.setText("Monitoring" if enabled else "Paused")
        self.monitor_caption.setText("Auto-saving copies" if enabled else "Clipboard capture is paused")
        self.monitor_button.setText("Pause" if enabled else "Resume")

    def refresh(self):
        while self.entries.count():
            entry = self.entries.takeAt(0)
            if entry.widget():
                entry.widget().deleteLater()
        kind = self.section if self.section not in ("all", "favorites") else "all"
        rows = self.db.get_all(self.search.text(), kind, self.section == "favorites")
        names = {item[0]: item[2] for item in self.SECTIONS}
        self.heading.setText(names[self.section])
        self.subheading.setText(f"{len(rows)} items  ·  History limit: {self.settings.values['history_limit']}")
        for entry in rows:
            self.add_entry(entry)
        if not rows:
            empty = label("No copied items here yet", "muted")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setMinimumHeight(140)
            self.entries.addWidget(empty)
        self.entries.addStretch()

    def add_entry(self, entry):
        item_id, content, pinned, created_at, kind, image, last_used = tuple(entry)
        is_image = kind == "image"
        is_link = not is_image and content.strip().lower().startswith(("https://", "http://"))
        item_type = "Image" if is_image else ("Link" if is_link else "Text")

        frame = QFrame()
        frame.setObjectName("entry")
        outer = QHBoxLayout(frame)
        outer.setContentsMargins(17, 16, 17, 16)
        outer.setSpacing(16)

        tile = QFrame()
        tile.setObjectName("tile")
        tile.setFixedSize(50, 50)
        tile_layout = QVBoxLayout(tile)
        tile_layout.setContentsMargins(0, 0, 0, 0)
        tile_icon = QLabel()
        tile_icon.setPixmap(icon_pixmap("image" if is_image else ("link" if is_link else "text"), "#8ad3ce", 26))
        tile_icon.setFixedSize(28, 28)
        tile_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tile_layout.addWidget(tile_icon, 0, Qt.AlignmentFlag.AlignCenter)
        outer.addWidget(tile, 0, Qt.AlignmentFlag.AlignTop)

        details_widget = QWidget()
        details_widget.setObjectName("entryDetails")
        details_widget.setMinimumWidth(0)
        details_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        details = QVBoxLayout(details_widget)
        details.setContentsMargins(0, 0, 0, 0)
        details.setSpacing(7)
        if is_image:
            title = label("Copied image", "itemTitle")
            details.addWidget(title)
            if image:
                pixmap = QPixmap()
                if pixmap.loadFromData(image, "PNG"):
                    thumbnail = QLabel()
                    thumbnail.setPixmap(pixmap.scaled(170, 95, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                    thumbnail.setFixedHeight(96)
                    thumbnail.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    details.addWidget(thumbnail)
                    details.addWidget(label(f"{pixmap.width()} × {pixmap.height()}", "itemBody"))
        else:
            pieces = content.strip().splitlines()
            title_text = pieces[0] if pieces else "Copied text"
            title = ElidedLabel(title_text, "itemTitle")
            title.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            details.addWidget(title)
            if len(pieces) > 1:
                body_text = " ".join(pieces[1:])
                subtitle = ElidedLabel(body_text, "itemBody")
                details.addWidget(subtitle)
        details.addWidget(ElidedLabel(f"{item_type}    ·    {timestamp(last_used or created_at)}", "meta"))
        outer.addWidget(details_widget, 1)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addWidget(button("★" if pinned else "☆", lambda checked=False, i=item_id: self.change_pin(i),
                                 "action", "Remove favorite" if pinned else "Add to favorites"))
        value = (kind, content, image)
        actions.addWidget(button("▢", lambda checked=False, v=value: self.copy_requested.emit(v, False), "action", "Copy"))
        actions.addWidget(button("⇥", lambda checked=False, v=value: self.copy_requested.emit(v, True), "action", "Quick paste"))
        actions.addWidget(button("×", lambda checked=False, i=item_id: self.delete_item(i), "action", "Delete"))
        more = button("···", lambda checked=False, i=item_id, v=value: self.entry_menu(i, v), "action", "More options")
        actions.addWidget(more)
        outer.addLayout(actions)
        self.entries.addWidget(frame)

    def entry_menu(self, item_id, value):
        menu = QMenu(self)
        menu.addAction("Copy", lambda: self.copy_requested.emit(value, False))
        menu.addAction("Paste", lambda: self.copy_requested.emit(value, True))
        menu.addSeparator()
        menu.addAction("Delete", lambda: self.delete_item(item_id))
        menu.exec(self.cursor().pos())

    def change_pin(self, item_id):
        self.db.toggle_pin(item_id)
        self.refresh()

    def delete_item(self, item_id):
        self.db.delete(item_id)
        self.refresh()

    def clear_history(self):
        if QMessageBox.question(self, "Clear history", "Delete all unpinned items?") == QMessageBox.StandardButton.Yes:
            self.db.clear()
            self.refresh()

    def open_settings(self):
        dialog = SettingsDialog(self.settings, self.startup_get, self.startup_set, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.db.trim(self.settings.values["history_limit"])
            self.db.delete_older_than(self.settings.values["auto_delete_days"])
            self.refresh()

    def open_about(self):
        QMessageBox.information(self, "About MultiCopy", "MultiCopy\nClipboard history for Windows and macOS.\nHistory is stored locally on this computer.")

    def export_history(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export history", "multicopy-history.json", "JSON (*.json);;Text (*.txt)")
        if not path:
            return
        rows = self.db.get_all()
        try:
            if Path(path).suffix.lower() == ".txt":
                lines = [row[1] if row[4] == "text" else "[Image omitted from text export]" for row in rows]
                Path(path).write_text("\n\n---\n\n".join(lines), encoding="utf-8")
            else:
                output = []
                for row in rows:
                    item = {"type": row[4], "text": row[1], "pinned": bool(row[2]), "created_at": row[3]}
                    if row[4] == "image":
                        item["image_png_base64"] = base64.b64encode(row[5]).decode("ascii")
                    output.append(item)
                Path(path).write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
        except OSError as error:
            QMessageBox.warning(self, "Export failed", str(error))

    def closeEvent(self, event):
        if self.on_close:
            self.on_close(event)
        else:
            super().closeEvent(event)
