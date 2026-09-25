"""Single blue theme. No switching."""

BLUE = {
    "bg_app":       "#0b1420",
    "bg_card":      "#132033",
    "bg_hover":     "#1a2b42",
    "bg_input":     "#132033",
    "bg_navbar":    "#0f1c2d",
    "border":       "#1e3a5c",
    "text":         "#FFFFFF",
    "text_dim":     "#A8C0DB",
    "text_muted":   "#6b8bab",
    "accent":       "#2AABEE",
    "accent_hover": "#229ED9",
    "accent_dark":  "#1c8ac4",
    "accent_soft":  "#1a3d59",
    "telegram":     "#2AABEE",
    "telegram_hover":"#229ED9",
    "green":        "#4dcd5e",
    "red":          "#e85c7c",
    "yellow":       "#e8b047",
}


class Theme:
    def __init__(self):
        self.mode = "blue"
        self.dark = False
        self._apply()

    def _apply(self):
        for k, v in BLUE.items():
            setattr(self, k.upper(), v)
        self.ACCENT_H = self.ACCENT_HOVER
        self.ACCENT_D = self.ACCENT_DARK

    def set_mode(self, mode):
        # no-op — theme is always blue
        pass

    def toggle(self):
        return "blue"


theme = Theme()


FONT_TITLE  = ("Segoe UI", 13, "bold")
FONT_H1     = ("Segoe UI", 18, "bold")
FONT_H2     = ("Segoe UI", 12, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_TINY   = ("Segoe UI", 8)
FONT_LABEL  = ("Segoe UI", 9, "bold")
FONT_MONO   = ("Consolas", 9)
