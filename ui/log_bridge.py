"""Forward everything logged to stdout/stderr into the UI log box."""
import logging
import sys
import threading


class UiLogHandler(logging.Handler):
    """A logging handler that pushes records into a UI callback."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self._lock = threading.Lock()

    def emit(self, record):
        try:
            msg = self.format(record)
        except Exception:
            return
        try:
            with self._lock:
                self.callback(msg)
        except Exception:
            pass


class StreamTee:
    """Replacement for sys.stdout / sys.stderr that forwards to a callback."""

    def __init__(self, original, callback):
        self._original = original
        self._callback = callback
        self._buf = ""

    def write(self, text):
        try:
            if self._original:
                self._original.write(text)
        except Exception:
            pass
        if not text:
            return
        self._buf += text
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            if line.strip():
                try:
                    self._callback(line)
                except Exception:
                    pass

    def flush(self):
        try:
            if self._original:
                self._original.flush()
        except Exception:
            pass

    def isatty(self):
        return False




class _NoiseFilter(logging.Filter):
    def filter(self, record):
        try:
            msg = record.getMessage().strip()
        except Exception:
            return True
        if not msg:
            return False
        if set(msg) <= set("= "):
            return False
        if set(msg) <= set("="):
            return False
        # Скрыть шумные stats-строки
        if msg.startswith("stats: total="):
            return False
        return True


_installed = False


def install(callback):
    """Install a logging handler + stdout/stderr tee once."""
    global _installed
    if _installed:
        return
    _installed = True

    fmt = logging.Formatter("%(asctime)s  %(levelname)-5s  %(message)s",
                            datefmt="%H:%M:%S")

    handler = UiLogHandler(callback)
    handler.setFormatter(fmt)
    handler.setLevel(logging.INFO)

    root = logging.getLogger()
    handler.addFilter(_NoiseFilter())
    root.addHandler(handler)
    if root.level > logging.INFO:
        root.setLevel(logging.INFO)

    # Tee stdout / stderr (catches print() and tracebacks too)
    sys.stdout = StreamTee(sys.stdout, callback)
    sys.stderr = StreamTee(sys.stderr, callback)
