"""Persistent proxy link storage."""
import os


STORE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "proxy_link.txt")


def load_secret() -> str:
    """Return existing secret, or empty string."""
    try:
        if os.path.exists(STORE_PATH):
            with open(STORE_PATH, "r", encoding="utf-8") as f:
                line = f.readline().strip()
            if line:
                # line is "https://t.me/proxy?...&secret=ddXXXX"
                if "secret=" in line:
                    s = line.split("secret=", 1)[1]
                    if s.startswith("dd"):
                        s = s[2:]
                    s = s.split("&")[0].strip()
                    if len(s) == 32:
                        return s
    except Exception:
        pass
    return ""


def save_link(secret: str, host: str, port: int) -> str:
    """Write proxy link to file. Returns the URL."""
    url = ("https://t.me/proxy?server=" + host +
           "&port=" + str(port) + "&secret=dd" + secret)
    try:
        with open(STORE_PATH, "w", encoding="utf-8") as f:
            f.write(url + "\n")
    except Exception:
        pass
    return url


def read_link() -> str:
    """Read link from file."""
    try:
        if os.path.exists(STORE_PATH):
            with open(STORE_PATH, "r", encoding="utf-8") as f:
                return f.readline().strip()
    except Exception:
        pass
    return ""


def ensure_secret(host: str, port: int) -> str:
    """Get or create a permanent secret. Writes link file."""
    s = load_secret()
    if not s:
        import secrets as _s
        s = _s.token_hex(16)
    save_link(s, host, port)
    return s
