"""Pages."""
import time
import customtkinter as ctk

from .theme import theme
from .proxy_store import read_link
from .widgets import (
    TelegramLogoButton,
    Logo, Pill, SearchBox, CardRow,
    SoftEntry, SegmentedControl, BigButton,
)


class ProxyPage(ctk.CTkFrame):
    def __init__(self, master, config,
                 on_start, on_stop, on_open_telegram, on_copy,
                 get_stats, on_show_logs, on_toggle_flash, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.config = config
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_open_telegram = on_open_telegram
        self.on_copy = on_copy
        self.get_stats = get_stats
        self.on_show_logs = on_show_logs
        self.on_toggle_flash = on_toggle_flash
        self._running = False
        self._build()

    def _build(self):
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True)

        col = ctk.CTkFrame(outer, fg_color="transparent")
        col.place(relx=0.5, rely=0.5, anchor="center")

        logo_row = ctk.CTkFrame(col, fg_color="transparent")
        logo_row.pack()
        self.logo_btn = TelegramLogoButton(
            logo_row, size=96,
            on_click=self._logo_clicked,
        )
        self.logo_btn.pack()

        ctk.CTkLabel(
            col, text="TG WS PROXY",
            font=("Segoe UI", 30, "bold"),
            text_color=theme.TEXT,
        ).pack(pady=(8, 0))

        ctk.CTkLabel(
            col, text="Local MTProto to WebSocket",
            font=("Segoe UI", 11),
            text_color=theme.TEXT_DIM,
        ).pack(pady=(4, 18))

        status = ctk.CTkFrame(col, fg_color=theme.BG_CARD,
                               corner_radius=16,
                               border_width=1, border_color=theme.BORDER,
                               width=520, height=54)
        status.pack(pady=(0, 14))
        status.pack_propagate(False)
        si = ctk.CTkFrame(status, fg_color="transparent")
        si.pack(fill="x", padx=20, pady=14)
        self.dot = ctk.CTkLabel(si, text="\u25cf",
                                 font=("Segoe UI", 18),
                                 text_color=theme.RED)
        self.dot.pack(side="left", padx=(0, 10))
        self.state_label = ctk.CTkLabel(
            si, text="Offline", font=("Segoe UI", 14, "bold"),
            text_color=theme.TEXT,
        )
        self.state_label.pack(side="left")


        link_wrap = ctk.CTkFrame(col, fg_color="transparent", width=520,
                                  height=64)
        link_wrap.pack(pady=(14, 0))
        link_wrap.pack_propagate(False)

        self.link_box = SearchBox(
            link_wrap,
            on_primary=self._do_copy,
            primary_text="COPY",
            on_secondary=self._do_open_tg,
            secondary_text="OPEN",
        )
        self.link_box.pack(fill="x")
        self.link_box.entry.configure(state="readonly")

    def _logo_clicked(self):
        """Клик по логотипу: открыть Telegram и обновить статус."""
        try:
            self.on_open_telegram()
        except Exception:
            pass
        try:
            self.set_state(True)
        except Exception:
            pass

    def _make_link(self):
        # Читаем из proxy_link.txt — ссылка постоянная
        url = read_link()
        if url:
            return url
        # fallback: соберём из config (на случай первого запуска)
        secret = getattr(self.config, "secret", "") or ""
        host = getattr(self.config, "host", "127.0.0.1")
        port = getattr(self.config, "port", 1443)
        return ("https://t.me/proxy?server=" + host +
                "&port=" + str(port) + "&secret=dd" + secret)


    def refresh_link(self):
        try:
            self.link_box.set(self._make_link())
        except Exception:
            pass

    def _do_copy(self):
        self.on_copy(self._make_link())

    def _do_open_tg(self):
        self.on_open_telegram()

    def _on_start(self):
        pass

    def _on_stop(self):
        pass

    def set_state(self, running):
        self._running = running
        if running:
            self.dot.configure(text_color=theme.GREEN)
            self.state_label.configure(text="Online")
        else:
            self.dot.configure(text_color=theme.RED)
            self.state_label.configure(text="Offline")

    def _toggle_flash(self):
        pass


class LogsPage(ctk.CTkFrame):
    def __init__(self, master, on_back=None, **kw):
        super().__init__(master, fg_color="transparent", **kw)

        head = ctk.CTkFrame(self, fg_color="transparent")
        head.pack(fill="x", padx=20, pady=(16, 8))
        ctk.CTkLabel(head, text="Logs",
                     font=("Segoe UI", 22, "bold"),
                     text_color=theme.TEXT).pack(side="left")

        if on_back:
            ctk.CTkButton(
                head, text="Back", width=80, height=30,
                corner_radius=999,
                fg_color=theme.BG_HOVER, hover_color=theme.ACCENT_SOFT,
                text_color=theme.TEXT, font=("Segoe UI", 10),
                command=on_back,
            ).pack(side="right")

        self.log_box = ctk.CTkTextbox(
            self, fg_color=theme.BG_CARD, corner_radius=16,
            text_color="#C8FF8D",
            font=("Consolas", 10),
            border_width=1, border_color=theme.BORDER, wrap="word",
        )
        self.log_box.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.log_box.insert("end", "  Ready\n")
        self.log_box.configure(state="disabled")

    def log(self, text):
        ts = time.strftime("%H:%M:%S")
        try:
            self.log_box.configure(state="normal")
            self.log_box.insert("end", "[" + ts + "] " + str(text) + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        except Exception:
            pass

    def clear(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, config, on_theme_change=None, **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.config = config
        self.on_theme_change = on_theme_change

        ctk.CTkLabel(self, text="Settings",
                     font=("Segoe UI", 22, "bold"),
                     text_color=theme.TEXT).pack(anchor="w", padx=20,
                                                  pady=(16, 10))

        c0 = CardRow(self, "Theme")
        c0.pack(fill="x", padx=16, pady=5)
        self.theme_seg = SegmentedControl(
            c0.body, options=["Blue", "Dark"],
            default_index=0 if theme.mode == "blue" else 1,
            command=self._switch_theme,
        )
        self.theme_seg.pack(anchor="w")

        c1 = CardRow(self, "Port")
        c1.pack(fill="x", padx=16, pady=5)
        self.port_entry = SoftEntry(
            c1.body,
            textvariable=ctk.StringVar(
                value=str(getattr(config, "port", 1443))))
        self.port_entry.pack(fill="x")

        c2 = CardRow(self, "WS Pool")
        c2.pack(fill="x", padx=16, pady=5)
        self.pool_seg = SegmentedControl(
            c2.body, options=[2, 4, 6, 8], default_index=2)
        self.pool_seg.pack(anchor="w")

        c3 = CardRow(self, "Secret")
        c3.pack(fill="x", padx=16, pady=5)
        key_row = ctk.CTkFrame(c3.body, fg_color="transparent")
        key_row.pack(fill="x")
        secret = getattr(config, "secret", "") or ""
        self.secret_entry = SoftEntry(
            key_row,
            textvariable=ctk.StringVar(value=secret))
        self.secret_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(
            key_row, text="R", width=42, height=42,
            fg_color=theme.BG_INPUT, hover_color=theme.ACCENT_SOFT,
            text_color=theme.TEXT_DIM, corner_radius=14,
            font=("Segoe UI", 14),
            command=self._regen_secret,
        ).pack(side="right", padx=(8, 0))

    def _switch_theme(self, idx):
        mode = "blue" if idx == 0 else "dark"
        theme.set_mode(mode)
        if self.on_theme_change:
            self.on_theme_change(mode)


    def _regen_secret(self):
        import secrets as _s
        new = _s.token_hex(16)
        try:
            self.config.secret = new
        except Exception:
            pass
        self.secret_entry.delete(0, "end")
        self.secret_entry.insert(0, new)


class InfoPage(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, fg_color="transparent", **kw)

        ctk.CTkLabel(self, text="Info",
                     font=("Segoe UI", 22, "bold"),
                     text_color=theme.TEXT).pack(anchor="w", padx=20,
                                                  pady=(16, 10))

        card = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=18,
                            border_width=1, border_color=theme.BORDER)
        card.pack(fill="x", padx=16)

        rows = [
            ("Name",    "TG-WS-PROXY Custom Build"),
            ("Version", "1.0.0"),
            ("Core",    "proxy (fork)"),
            ("License", "MIT"),
            ("Python",  "3.14"),
        ]
        for label, value in rows:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=10)
            ctk.CTkLabel(row, text=label, font=("Segoe UI", 10),
                         text_color=theme.TEXT_DIM,
                         anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, font=("Segoe UI", 11),
                         text_color=theme.TEXT).pack(side="right")
