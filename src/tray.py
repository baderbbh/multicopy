import threading

import pystray
from PIL import Image, ImageDraw


def tray_image():
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((15, 14, 49, 54), radius=7, fill="#c4c9cc")
    draw.rounded_rectangle((22, 8, 42, 20), radius=4, fill="#e8f2ef")
    draw.line((23, 30, 42, 30), fill="#18211f", width=3)
    draw.line((23, 38, 39, 38), fill="#18211f", width=3)
    return image


class Tray:
    def __init__(self, on_open, on_pause, on_exit, is_monitoring):
        self.icon = pystray.Icon(
            "MultiCopy", tray_image(), "MultiCopy",
            menu=pystray.Menu(
                pystray.MenuItem("Open MultiCopy", lambda *_: on_open(), default=True),
                pystray.MenuItem(
                    lambda _: "Pause monitoring" if is_monitoring() else "Resume monitoring",
                    lambda *_: on_pause(),
                ),
                pystray.MenuItem("Exit", lambda *_: on_exit()),
            ),
        )
        self.thread = None

    def start(self):
        self.thread = threading.Thread(target=self.icon.run, daemon=True)
        self.thread.start()

    def stop(self):
        self.icon.stop()

    def refresh(self):
        self.icon.update_menu()
