"""Static grey background with grid."""
import customtkinter as ctk

from .theme import theme


class Background(ctk.CTkCanvas):
    def __init__(self, master, **kw):
        super().__init__(master, bg=theme.BG_APP,
                         highlightthickness=0, **kw)
        self.bind("<Configure>", lambda e: self._draw())
        self.after(80, self._draw)

    def start(self):
        # nothing to animate anymore
        pass

    def stop(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass

    def _draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 10:
            return

        self.create_rectangle(0, 0, w, h, fill=theme.BG_APP, outline="")

        step = 36
        for x in range(0, w, step):
            self.create_line(x, 0, x, h, fill="#2a2a2a", width=1)
        for y in range(0, h, step):
            self.create_line(0, y, w, y, fill="#2a2a2a", width=1)
