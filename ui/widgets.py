"""Widgets: oversized buttons, ripple, Russian labels."""
import os
import customtkinter as ctk
from PIL import Image

from .theme import theme
from .animations import lerp_color


ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


# ───────────────────────────────────────────────────────────
#  Logo
# ───────────────────────────────────────────────────────────
class Logo(ctk.CTkLabel):
    def __init__(self, master, size: int = 72, **kw):
        self._image = None
        path = os.path.join(ASSETS_DIR, "logo_tg.png")
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA")
                side = min(img.size)
                left = (img.size[0] - side) // 2
                top = (img.size[1] - side) // 2
                img = img.crop((left, top, left + side, top + side))
                img = img.resize((size, size))
                self._image = ctk.CTkImage(light_image=img, dark_image=img,
                                            size=(size, size))
            except Exception:
                self._image = None
        if self._image is not None:
            super().__init__(master, image=self._image, text="", **kw)
        else:
            super().__init__(master, text="T",
                             font=("Segoe UI", int(size * 0.5), "bold"),
                             text_color=theme.ACCENT, **kw)


# ───────────────────────────────────────────────────────────
#  Big button with ripple + hover animation
# ───────────────────────────────────────────────────────────
class TelegramLogoButton(ctk.CTkLabel):
    """Кликабельный логотип TG: серый → цветной при клике."""

    def __init__(self, master, size: int = 96, on_click=None, **kw):
        self._size = size
        self._on_click = on_click
        self._clicked = False
        self._color_img = None
        self._gray_img = None

        self._load_images()
        super().__init__(master, image=self._gray_img,
                          text="", cursor="hand2", **kw)

        self.bind("<Button-1>", self._handle_click)

    def _load_images(self):
        import os
        path = os.path.join(ASSETS_DIR, "logo_tg.png")
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA")
                side = min(img.size)
                left = (img.size[0] - side) // 2
                top = (img.size[1] - side) // 2
                img = img.crop((left, top, left + side, top + side))
                img = img.resize((self._size, self._size), Image.LANCZOS)

                # Цветная
                self._color_img = ctk.CTkImage(
                    light_image=img, dark_image=img,
                    size=(self._size, self._size))

                # Серая — конвертим в grayscale
                gray = img.convert("LA").convert("RGBA")
                self._gray_img = ctk.CTkImage(
                    light_image=gray, dark_image=gray,
                    size=(self._size, self._size))
            except Exception:
                self._color_img = None
                self._gray_img = None

    def _handle_click(self, _event=None):
        if self._clicked:
            return
        self._clicked = True
        # Сначала цвет
        if self._color_img is not None:
            self.configure(image=self._color_img)
        # Затем — действие
        if self._on_click:
            try:
                self._on_click()
            except Exception:
                pass

    def reset(self):
        """Вернуть в серое состояние (при перезапуске)."""
        self._clicked = False
        if self._gray_img is not None:
            self.configure(image=self._gray_img)


class BigButton(ctk.CTkFrame):
    def __init__(self, master, text: str,
                 fg: str = None, hover: str = None,
                 text_color: str = "#FFFFFF",
                 command=None,
                 height: int = 52, radius: int = 16,
                 font_size: int = 13, **kw):
        super().__init__(master, fg_color="transparent",
                         height=height, **kw)
        self.pack_propagate(False)
        self.command = command
        self._base = fg or theme.ACCENT
        self._hover = hover or theme.ACCENT_HOVER

        self.btn = ctk.CTkButton(
            self, text=text, height=height, corner_radius=radius,
            fg_color=self._base, hover_color=self._base,
            text_color=text_color,
            font=("Segoe UI", font_size, "bold"),
            command=self._fire,
        )
        self.btn.pack(fill="both", expand=True)

        self.btn.bind("<Enter>", self._on_enter, add="+")
        self.btn.bind("<Leave>", self._on_leave, add="+")

    def _on_enter(self, e):
        self._animate(self._base, self._hover)

    def _on_leave(self, e):
        self._animate(self._hover, self._base)

    def _animate(self, c1: str, c2: str, steps: int = 8):
        for i in range(steps + 1):
            t = i / steps
            col = lerp_color(c1, c2, t)
            self.after(i * 14, lambda c=col: self.btn.configure(fg_color=c))

    def _fire(self):
        if self.command:
            self.command()

    def set_text(self, text: str):
        self.btn.configure(text=text)



class Pill(ctk.CTkFrame):
    def __init__(self, master, text: str, active: bool = False,
                 command=None, **kw):
        bg = theme.ACCENT if active else theme.BG_HOVER
        fg = "#FFFFFF" if active else theme.TEXT
        super().__init__(master, fg_color=bg, corner_radius=999, **kw)
        self.command = command
        self._active = active
        self.label = ctk.CTkLabel(self, text=text,
                                   font=("Segoe UI", 10, "bold"),
                                   text_color=fg)
        self.label.pack(padx=16, pady=8)
        if command:
            for w in (self, self.label):
                w.bind("<Button-1>", lambda e: command())
                try:
                    w.configure(cursor="hand2")
                except Exception:
                    pass

    def set_active(self, active: bool):
        self._active = active
        bg = theme.ACCENT if active else theme.BG_HOVER
        fg = "#FFFFFF" if active else theme.TEXT
        self.configure(fg_color=bg)
        self.label.configure(text_color=fg)





class SearchBox(ctk.CTkFrame):
    def __init__(self, master, on_primary=None,
                 primary_text: str = "COPY",
                 on_secondary=None,
                 secondary_text: str = "OPEN", **kw):
        super().__init__(master, fg_color=theme.BG_CARD,
                         corner_radius=999,
                         border_width=1, border_color=theme.BORDER, **kw)

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=8, pady=8)

        ctk.CTkLabel(inner, text="S", font=("Segoe UI", 14),
                     text_color=theme.TEXT_MUTED).pack(side="left",
                                                        padx=(16, 6))

        self.var = ctk.StringVar(value="")
        self.entry = ctk.CTkEntry(
            inner, textvariable=self.var,
            fg_color="transparent", border_width=0,
            text_color=theme.TEXT,
            font=("Segoe UI", 12),
            height=42,
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        if on_secondary:
            ctk.CTkButton(
                inner, text=secondary_text, width=100, height=40,
                corner_radius=999,
                fg_color=theme.BG_HOVER, hover_color=theme.ACCENT_SOFT,
                text_color=theme.TEXT, font=("Segoe UI", 10, "bold"),
                command=on_secondary,
            ).pack(side="right", padx=(6, 0))

        if on_primary:
            ctk.CTkButton(
                inner, text=primary_text, width=100, height=40,
                corner_radius=999,
                fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
                text_color="#FFFFFF", font=("Segoe UI", 10, "bold"),
                command=on_primary,
            ).pack(side="right", padx=6)

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)


class CardRow(ctk.CTkFrame):
    def __init__(self, master, title: str = "", **kw):
        super().__init__(master, fg_color=theme.BG_CARD, corner_radius=18,
                         border_width=1, border_color=theme.BORDER, **kw)
        if title:
            ctk.CTkLabel(self, text=title, font=("Segoe UI", 10, "bold"),
                         text_color=theme.TEXT_DIM,
                         anchor="w").pack(fill="x", padx=18,
                                           pady=(14, 0))
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="x", padx=18, pady=(6, 14))


class SoftEntry(ctk.CTkEntry):
    def __init__(self, master, **kw):
        kw.setdefault("fg_color", theme.BG_INPUT)
        kw.setdefault("border_color", theme.BG_INPUT)
        kw.setdefault("text_color", theme.TEXT)
        kw.setdefault("corner_radius", 14)
        kw.setdefault("height", 42)
        kw.setdefault("font", ("Segoe UI", 11))
        super().__init__(master, **kw)


class SegmentedControl(ctk.CTkFrame):
    def __init__(self, master, options, default_index: int = 0,
                 command=None, **kw):
        super().__init__(master, fg_color=theme.BG_INPUT,
                         corner_radius=16, **kw)
        self.command = command
        self.buttons = []
        self._selected = default_index
        for i, opt in enumerate(options):
            btn = ctk.CTkButton(
                self, text=str(opt), width=80, height=38,
                corner_radius=14, font=("Segoe UI", 11),
                fg_color="transparent", hover_color=theme.ACCENT_SOFT,
                text_color=theme.TEXT_DIM,
                command=lambda idx=i: self.select(idx),
            )
            btn.pack(side="left", padx=3, pady=3)
            self.buttons.append(btn)
        self._apply()

    def select(self, idx: int):
        self._selected = idx
        self._apply()
        if self.command:
            self.command(idx)

    def _apply(self):
        for i, btn in enumerate(self.buttons):
            if i == self._selected:
                btn.configure(fg_color=theme.ACCENT, text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent",
                              text_color=theme.TEXT_DIM)
