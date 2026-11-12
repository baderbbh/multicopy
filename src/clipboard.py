from PySide6.QtCore import QByteArray, QBuffer, QIODevice, QObject, Signal
from PySide6.QtGui import QImage


MAX_IMAGE_BYTES = 10 * 1024 * 1024


def image_to_png(image):
    if image.isNull():
        return None
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not image.save(buffer, "PNG") or data.size() > MAX_IMAGE_BYTES:
        return None
    return bytes(data)


class ClipboardWatcher(QObject):
    copied = Signal(str, object)

    def __init__(self, clipboard):
        super().__init__()
        self.clipboard = clipboard
        self.enabled = True
        self.ignore_next = False
        self.clipboard.dataChanged.connect(self.check)

    def check(self):
        if self.ignore_next:
            self.ignore_next = False
            return
        if not self.enabled:
            return
        mime = self.clipboard.mimeData()
        if mime is None:
            return
        if mime.hasImage():
            image = self.clipboard.image()
            if isinstance(image, QImage):
                content = image_to_png(image)
                if content:
                    self.copied.emit("image", content)
                    return
        if mime.hasText():
            text = mime.text()
            if text and text.strip():
                self.copied.emit("text", text)

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)

    def ignore_own_copy(self):
        self.ignore_next = True
