import argparse
import hashlib
import os
import sys

from PySide6.QtNetwork import QLocalServer, QLocalSocket

from PySide6.QtCore import QObject, QTimer
from PySide6.QtGui import QAction, QIcon, QImage
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon

from src.clipboard import ClipboardWatcher
from src.database import Database
from src.hotkeys import Hotkeys, paste_shortcut
from src.settings import Settings
from src.startup import is_enabled, set_enabled
from src.resources import asset_path
from src.ui import Interface


class SingleInstance(QObject):
    def __init__(self, name, on_open):
        super().__init__()
        self.name = name
        self.on_open = on_open
        self.server = QLocalServer(self)
        self.server.newConnection.connect(self.handle_connection)

    def notify_existing(self):
        socket = QLocalSocket(self)
        socket.connectToServer(self.name)
        if not socket.waitForConnected(300):
            socket.abort()
            return False
        socket.write(b"open")
        socket.waitForBytesWritten(300)
        socket.disconnectFromServer()
        return True

    def listen(self):
        if self.server.listen(self.name):
            return True
        QLocalServer.removeServer(self.name)
        return self.server.listen(self.name)

    def handle_connection(self):
        while self.server.hasPendingConnections():
            connection = self.server.nextPendingConnection()
            connection.readyRead.connect(lambda conn=connection: self.read_request(conn))
            connection.disconnected.connect(connection.deleteLater)
            if connection.bytesAvailable():
                self.read_request(connection)

    def read_request(self, connection):
        if b"open" in bytes(connection.readAll()):
            self.on_open()
        connection.disconnectFromServer()


def instance_name():
    identity = os.environ.get("USERNAME") or os.environ.get("USER") or str(os.getuid() if hasattr(os, "getuid") else "user")
    key = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    return f"MultiCopy-{key}"


class MultiCopy(QObject):
    def __init__(self, app, hidden=False):
        super().__init__()
        self.app = app
        self.app.setQuitOnLastWindowClosed(False)
        self.db = Database()
        self.settings = Settings()
        self.db.delete_older_than(self.settings.values["auto_delete_days"])
        self.window = Interface(self.db, self.settings, is_enabled, set_enabled)
        self.window.copy_requested.connect(self.copy_item)
        self.window.monitoring_requested.connect(self.toggle_monitoring)
        self.window.exit_requested.connect(self.quit)
        self.window.on_close = self.close_window
        self.clipboard = ClipboardWatcher(app.clipboard())
        self.clipboard.set_enabled(self.settings.values["monitoring"])
        self.clipboard.copied.connect(self.save_copy)
        self.hotkeys = Hotkeys()
        self.hotkeys.open_requested.connect(self.show)
        self.hotkeys.start()
        self.build_tray()
        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.timeout.connect(self.cleanup)
        self.cleanup_timer.start(60 * 60 * 1000)
        if not hidden or not self.tray.isSystemTrayAvailable():
            self.show()

    def build_tray(self):
        tray_icon = QIcon(str(asset_path("src", "assets", "multicopy-logo.png")))
        if tray_icon.isNull():
            tray_icon = self.app.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        self.tray = QSystemTrayIcon(tray_icon, self.app)
        menu = QMenu()
        open_action = QAction("Open MultiCopy", self.app)
        open_action.triggered.connect(self.show)
        menu.addAction(open_action)
        self.pause_action = QAction("Pause monitoring", self.app)
        self.pause_action.triggered.connect(self.toggle_monitoring)
        menu.addAction(self.pause_action)
        exit_action = QAction("Exit", self.app)
        exit_action.triggered.connect(self.quit)
        menu.addAction(exit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.tray_clicked)
        if self.tray.isSystemTrayAvailable():
            self.tray.show()
        self.update_monitoring()

    def tray_clicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()

    def close_window(self, event):
        if self.tray.isSystemTrayAvailable():
            event.ignore()
            self.window.hide()
        else:
            event.accept()
            self.quit()

    def show(self):
        self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()
        self.window.search.setFocus()

    def save_copy(self, kind, value):
        if self.db.add(value, self.settings.values["history_limit"], kind):
            self.window.refresh()

    def copy_item(self, item, paste):
        kind, text, image = item
        self.clipboard.ignore_own_copy()
        if kind == "image":
            copied = QImage.fromData(image, "PNG")
            if copied.isNull():
                return
            self.app.clipboard().setImage(copied)
        else:
            self.app.clipboard().setText(text)
        if paste:
            self.window.hide()
            paste_shortcut()

    def toggle_monitoring(self):
        enabled = not self.settings.values["monitoring"]
        self.settings.set("monitoring", enabled)
        self.clipboard.set_enabled(enabled)
        self.update_monitoring()

    def update_monitoring(self):
        enabled = self.settings.values["monitoring"]
        self.window.set_monitoring(enabled)
        self.pause_action.setText("Pause monitoring" if enabled else "Resume monitoring")

    def cleanup(self):
        self.db.delete_older_than(self.settings.values["auto_delete_days"])
        self.window.refresh()

    def quit(self):
        self.hotkeys.stop()
        self.tray.hide()
        self.db.close()
        self.app.quit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hidden", action="store_true")
    args = parser.parse_args()
    app = QApplication(sys.argv[:1])
    app.setApplicationName("MultiCopy")
    icon = QIcon(str(asset_path("src", "assets", "multicopy-logo.png")))
    if not icon.isNull():
        app.setWindowIcon(icon)
    app.setOrganizationName("MultiCopy")
    instance = SingleInstance(instance_name(), lambda: None)
    if instance.notify_existing():
        return 0
    if not instance.listen():
        print("MultiCopy could not start its background service.", file=sys.stderr)
        return 1
    manager = MultiCopy(app, hidden=args.hidden)
    instance.on_open = manager.show
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
