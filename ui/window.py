"""Main window: 16:9 layout, log bridge."""
import webbrowser
import urllib.parse

import customtkinter as ctk

from .theme import theme
from .background import Background
from .pages import ProxyPage, LogsPage
from . import log_bridge
from .proxy_store import read_link, save_link
from .tray import TrayIcon


W, H = 1100, 620


class MainWindow(ctk.CTk):
    def __init__(self, config, on_start, on_stop, get_stats=None):
        super().__init__(fg_color=theme.BG_APP)
        self.config = config
        self.on_start = on_start
        self.on_stop = on_stop
        self._get_stats = get_stats or (lambda: None)
        self._running = False
        self._current = "proxy"

        self.title("TG WS Proxy")
        self.geometry(f"{W}x{H}")
        self.minsize(960, 540)
        self.configure(fg_color=theme.BG_APP)

        self._center_window()
        self._set_window_icon()
        self.protocol("WM_DELETE_WINDOW", self.withdraw_to_tray)
        self.attributes("-alpha", 0.0)
        self._fade_in()

        self._pages = {}
        self._flashing = False

        self._build_background()
        self._build_topbar()
        self._build_body()
        self._build_settings_button()

        log_bridge.install(self._on_log_line)
        self._really_quit = False
        self._tray = TrayIcon(
            on_show=self._restore_window,
            on_connect=self._tray_connect,
            on_quit=self._real_quit,
        )
        self._tray.start()

        self.show_page("proxy")
        self.after(200, self._refresh_link)

    def _center_window(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - W) // 2
        y = max(20, (sh - H) // 2 - 30)
        self.geometry(f"{W}x{H}+{x}+{y}")

    def _fade_in(self, alpha: float = 0.0):
        if alpha >= 1.0:
            self.attributes("-alpha", 1.0)
            return
        self.attributes("-alpha", alpha)
        self.after(16, lambda: self._fade_in(alpha + 0.07))

    def _set_window_icon(self):
        """Иконка окна: сначала .ico (Windows), потом PNG."""
        import os
        assets = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets")

        # 1. Сначала ICO — на Windows работает надёжнее всего
        for name in ("cbuild_logo.ico", "logo_tg.ico", "telegram.ico"):
            path = os.path.join(assets, name)
            if not os.path.exists(path):
                continue
            try:
                self.iconbitmap(path)
                return
            except Exception:
                pass

        # 2. Потом PNG через iconphoto
        try:
            from PIL import Image, ImageTk
        except Exception:
            return

        for name in ("cbuild_logo.png", "logo_tg.png"):
            path = os.path.join(assets, name)
            if not os.path.exists(path):
                continue
            try:
                img = Image.open(path).convert("RGBA")
                side = min(img.size)
                left = (img.size[0] - side) // 2
                top = (img.size[1] - side) // 2
                img = img.crop((left, top, left + side, top + side))
                img = img.resize((64, 64), Image.LANCZOS)
                self._icon_photo = ImageTk.PhotoImage(img)
                try:
                    self.iconphoto(True, self._icon_photo)
                except Exception:
                    pass
                try:
                    self.wm_iconphoto(True, self._icon_photo)
                except Exception:
                    pass
                return
            except Exception:
                continue


    def _build_background(self):
        self.bg = Background(self)
        self.bg.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        self.bg.start()

    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent", height=44)
        bar.place(x=0, y=0, relwidth=1.0)
        bar.pack_propagate(False)

        ctk.CTkLabel(
            bar, text="TG WS Proxy",
            font=("Segoe UI", 12, "bold"),
            text_color=theme.TEXT_DIM,
        ).pack(side="left", padx=22, pady=12)

        self.tab_proxy_btn = ctk.CTkButton(
            bar, text="PROXY", width=96, height=30,
            corner_radius=999,
            fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            text_color="#FFFFFF", font=("Segoe UI", 10, "bold"),
            command=lambda: self.show_page("proxy"),
        )
        self.tab_proxy_btn.pack(side="right", padx=(4, 22))

        self.tab_logs_btn = ctk.CTkButton(
            bar, text="LOGS", width=96, height=30,
            corner_radius=999,
            fg_color=theme.BG_HOVER, hover_color=theme.ACCENT_SOFT,
            text_color=theme.TEXT_DIM, font=("Segoe UI", 10, "bold"),
            command=lambda: self.show_page("logs"),
        )
        self.tab_logs_btn.pack(side="right", padx=4)

    def _build_settings_button(self):
        # Settings removed. Nothing to build.
        self.settings_btn = None


    def _toggle_settings(self):
        pass


    def show_connect_flash(self):
        """Белая вспышка сверху, плавно исчезает. Запускается только одна."""
        if self._flashing:
            return
        self._flashing = True
        try:
            self.flash = ctk.CTkFrame(self, fg_color="#ffffff",
                                       corner_radius=0, height=3)
            self.flash.place(x=0, y=44, relwidth=1.0)
            self._flash_alpha = 1.0
            self._flash_step()
        except Exception:
            self._flashing = False

    def _flash_step(self):
        try:
            alpha = getattr(self, "_flash_alpha", 0.0)
            if alpha <= 0:
                try:
                    self.flash.destroy()
                except Exception:
                    pass
                self._flashing = False
                return
            h = int(3 + 90 * (1.0 - alpha))
            col = self._blend_white(alpha)
            self.flash.configure(height=h, fg_color=col)
            self.flash.place(x=0, y=44, relwidth=1.0)
            self._flash_alpha = alpha - 0.04
            self.after(30, self._flash_step)
        except Exception:
            self._flashing = False

    @staticmethod
    def _blend_white(t):
        v = max(0, min(255, int(35 + (255 - 35) * t)))
        return "#%02x%02x%02x" % (v, v, v)


    def _flash_step(self):
        try:
            alpha = getattr(self, "_flash_alpha", 0.0)
            if alpha <= 0:
                try:
                    self.flash.destroy()
                except Exception:
                    pass
                return
            # высота растёт, цвет уходит в фон
            h = int(3 + 90 * (1.0 - alpha))
            col = self._blend_white(alpha)
            self.flash.configure(height=h, fg_color=col)
            self.flash.place(x=0, y=44, relwidth=1.0)
            self._flash_alpha = alpha - 0.04
            self.after(30, self._flash_step)
        except Exception:
            pass

    @staticmethod
    def _blend_white(t):
        v = max(0, min(255, int(35 + (255 - 35) * t)))
        return "#%02x%02x%02x" % (v, v, v)


    def _build_body(self):
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.place(x=0, y=48, relwidth=1.0, relheight=1.0)

        self._pages["proxy"] = ProxyPage(
            self.content, self.config,
            on_start=self._on_start,
            on_stop=self._on_stop,
            on_open_telegram=self._open_in_telegram,
            on_copy=self._copy_to_clipboard,
            get_stats=self._get_stats,
            on_show_logs=lambda: self.show_page("logs"),
            on_toggle_flash=self._toggle_flash,
        )
        self._pages["logs"] = LogsPage(
            self.content,
            on_back=lambda: self.show_page("proxy"),
        )

    def show_page(self, key: str):
        if key not in self._pages:
            return
        for p in self._pages.values():
            p.pack_forget()
        page = self._pages[key]
        page.pack(fill="both", expand=True)
        self._current = key

        for k, btn in (("proxy", self.tab_proxy_btn),
                        ("logs", self.tab_logs_btn)):
            if k == key:
                btn.configure(fg_color=theme.ACCENT,
                              text_color="#FFFFFF",
                              hover_color=theme.ACCENT_HOVER)
            else:
                btn.configure(fg_color=theme.BG_HOVER,
                              text_color=theme.TEXT_DIM,
                              hover_color=theme.ACCENT_SOFT)

        if key == "proxy":
            self._refresh_link()

    def _refresh_link(self):
        try:
            self._pages["proxy"].refresh_link()
        except Exception:
            pass

    def _apply_theme(self, mode=None):
        # Theme is always blue now.
        try:
            self.configure(fg_color=theme.BG_APP)
            self.bg.configure(bg=theme.BG_APP)
        except Exception:
            pass
    def _toggle_flash(self, on: bool):
        try:
            if on:
                self.bg.resume()
            else:
                self.bg.pause()
        except Exception:
            pass

    def _on_start(self):
        self.on_start()
        self._running = True
        self._pages["proxy"].set_state(True)
        self._refresh_link()

    def _on_stop(self):
        self.on_stop()
        self._running = False
        self._pages["proxy"].set_state(False)
        self._refresh_link()

    def _on_stop(self):
        self.on_stop()
        self._running = False
        self._pages["proxy"].set_state(False)

    def set_state(self, running: bool):
        self._running = running
        self._pages["proxy"].set_state(running)

    def _open_in_telegram(self):
        """Открывает tg://proxy?... — Windows вызовет Telegram, а не браузер."""
        secret = getattr(self.config, "secret", "")
        host = getattr(self.config, "host", "127.0.0.1")
        port = getattr(self.config, "port", 1443)

        if not secret:
            self.log("no proxy secret available")
            return

        # Готовим и https-ссылку (для копирования / файла), и tg:// (для запуска)
        https_url = save_link(secret, host, port)

        # tg:// — этот протокол зарегистрирован Telegram Desktop
        query = urllib.parse.urlencode({
            "server": host,
            "port": port,
            "secret": "dd" + secret,
        })
        tg_url = "tg://proxy?" + query

        self.log("open: " + tg_url[:70])

        # Способ 1: os.startfile — Windows сам найдёт обработчик протокола tg://
        try:
            import os as _os
            _os.startfile(tg_url)
            return
        except Exception as e:
            self.log("os.startfile error: " + str(e))

        # Способ 2: через subprocess cmd /c start
        try:
            import subprocess as _sp
            _sp.Popen(["cmd", "/c", "start", "", tg_url], shell=False)
            return
        except Exception as e:
            self.log("subprocess error: " + str(e))

        # Способ 3: fallback — откроем https-ссылку в браузере
        self.log("fallback to browser")
        try:
            webbrowser.open(https_url)
        except Exception as e:
            self.log("webbrowser error: " + str(e))


    def _copy_to_clipboard(self, text: str):
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.log("copied")
        except Exception as e:
            self.log("copy error: " + str(e))

    def _on_log_line(self, text: str):
        try:
            self.after(0, lambda t=text: self._append_log(t))
        except Exception:
            pass

    def _append_log(self, text: str):
        try:
            self._pages["logs"].log(text)
        except Exception:
            pass

    def log(self, text: str):
        self._on_log_line(text)


    def _restore_window(self):
        try:
            self.after(0, self.deiconify)
            self.after(0, self.lift)
            self.after(0, lambda: self.attributes("-topmost", True))
            self.after(100, lambda: self.attributes("-topmost", False))
        except Exception:
            pass

    def _tray_connect(self):
        try:
            self.after(0, self._open_in_telegram)
        except Exception:
            pass

    def _real_quit(self):
        try:
            self._really_quit = True
        except Exception:
            pass
        try:
            if getattr(self, "_tray", None):
                self._tray.stop()
        except Exception:
            pass
        try:
            self.after(0, self.destroy)
        except Exception:
            pass

    def withdraw_to_tray(self):
        """Свернуть окно в трей, не закрывая приложение."""
        try:
            self.withdraw()
        except Exception:
            pass


    def destroy(self):
        try:
            if self._running:
                self.on_stop()
        except Exception:
            pass
        try:
            self.bg.stop()
        except Exception:
            pass
        super().destroy()
