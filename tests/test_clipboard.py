import unittest

try:
    from PySide6.QtCore import QBuffer, QByteArray, QIODevice
    from PySide6.QtGui import QImage
    from src.clipboard import MAX_IMAGE_BYTES, image_to_png
    AVAILABLE = True
except ImportError:
    AVAILABLE = False


@unittest.skipUnless(AVAILABLE, "PySide6 is not installed")
class ClipboardTests(unittest.TestCase):
    def test_convert_image_to_png(self):
        image = QImage(4, 4, QImage.Format.Format_ARGB32)
        image.fill(0xffcc3322)
        png = image_to_png(image)
        self.assertTrue(png.startswith(b"\x89PNG"))

    def test_empty_image_is_ignored(self):
        self.assertIsNone(image_to_png(QImage()))
