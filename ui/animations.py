"""Easing и анимационные хелперы."""
import math


def ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def ease_in_out_sine(t: float) -> float:
    return -(math.cos(math.pi * t) - 1) / 2


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_color(c1: str, c2: str, t: float) -> str:
    c1 = c1.lstrip("#")
    c2 = c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    r = int(lerp(r1, r2, t))
    g = int(lerp(g1, g2, t))
    b = int(lerp(b1, b2, t))
    return f"#{r:02x}{g:02x}{b:02x}"


class Shimmer:
    """Полоса, пробегающая по виджету (для поля ссылки)."""
    def __init__(self, canvas, width: int, height: int,
                 color: str = "#ffffff", alpha: float = 0.15):
        self.canvas = canvas
        self.w = width
        self.h = height
        self.color = color
        self.alpha = alpha
        self._pos = -0.3
        self._job = None
        self._rect_id = None

    def start(self):
        self._tick()

    def stop(self):
        if self._job:
            try:
                self.canvas.after_cancel(self._job)
            except Exception:
                pass
            self._job = None

    def _tick(self):
        self._pos += 0.02
        if self._pos > 1.3:
            self._pos = -0.3
        self._draw()
        self._job = self.canvas.after(50, self._tick)

    def _draw(self):
        try:
            self.canvas.delete("shimmer")
        except Exception:
            return
        x0 = int(self.w * self._pos)
        x1 = x0 + int(self.w * 0.18)
        try:
            self.canvas.create_rectangle(x0, 0, x1, self.h,
                                          fill=self.color, outline="",
                                          stipple="gray50", tags="shimmer")
        except Exception:
            pass


class RipplePulse:
    """Ripple-эффект на кнопке через Canvas-подложку."""
    def __init__(self, parent, width: int, height: int,
                 color: str, duration_ms: int = 500):
        self.parent = parent
        self.w = width
        self.h = height
        self.color = color
        self.duration = duration_ms

    def fire(self, x: float = None, y: float = None):
        if x is None:
            x = self.w / 2
        if y is None:
            y = self.h / 2

        canvas = getattr(self.parent, "_ripple_canvas", None)
        if canvas is None:
            return

        r0 = 4
        r1 = max(self.w, self.h) * 1.1
        steps = 18
        step_ms = max(16, self.duration // steps)

        def tick(i: int):
            if i > steps:
                canvas.delete("ripple")
                return
            t = ease_out_cubic(i / steps)
            r = r0 + (r1 - r0) * t
            alpha = 1.0 - t
            col = lerp_color(canvas.cget("bg"), self.color, alpha * 0.6)
            canvas.delete("ripple")
            canvas.create_oval(x - r, y - r, x + r, y + r,
                                outline=col, width=2, tags="ripple")
            canvas.after(step_ms, lambda: tick(i + 1))

        tick(0)
