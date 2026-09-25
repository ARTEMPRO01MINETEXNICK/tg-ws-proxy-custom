"""System tray icon for TG WS Proxy."""
import os
import threading

import pystray
from PIL import Image, ImageDraw


ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


def _load_icon_image(size=64):
    for name in ("cbuild_logo.png", "cbuild_logo.ico",
                 "logo_tg.png", "logo_tg.ico", "telegram.ico"):
        path = os.path.join(ASSETS_DIR, name)
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA")
                side = min(img.size)
                left = (img.size[0] - side) // 2
                top = (img.size[1] - side) // 2
                img = img.crop((left, top, left + side, top + side))
                return img.resize((size, size), Image.LANCZOS)
            except Exception:
                pass
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((4, 4, size - 4, size - 4), fill=(42, 171, 238, 255))
    return img



class TrayIcon:
    def __init__(self, on_show=None, on_connect=None, on_quit=None):
        self.on_show = on_show
        self.on_connect = on_connect
        self.on_quit = on_quit
        self._icon = None
        self._thread = None

    def start(self):
        image = _load_icon_image(64)

        def _show(icon, item):
            try:
                if self.on_show:
                    self.on_show()
            except Exception:
                pass

        def _connect(icon, item):
            try:
                if self.on_connect:
                    self.on_connect()
            except Exception:
                pass

        def _quit(icon, item):
            try:
                if self.on_quit:
                    self.on_quit()
            except Exception:
                pass
            try:
                icon.stop()
            except Exception:
                pass

        menu = pystray.Menu(
            pystray.MenuItem("Открыть", _show, default=True),
            pystray.MenuItem("Подключить", _connect),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Выход", _quit),
        )

        self._icon = pystray.Icon("tg_ws_proxy", image,
                                   "TG WS Proxy", menu)

        def runner():
            try:
                self._icon.run()
            except Exception:
                pass

        self._thread = threading.Thread(target=runner, daemon=True,
                                         name="tray-icon")
        self._thread.start()

    def stop(self):
        try:
            if self._icon:
                self._icon.stop()
        except Exception:
            pass
