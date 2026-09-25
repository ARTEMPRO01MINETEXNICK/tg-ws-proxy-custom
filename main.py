"""TG WS Proxy Custom — UI + прокси в одном event loop."""
import asyncio
import logging
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import log_bridge


def _noop_log(msg):
    try:
        print(msg)
    except Exception:
        pass


log_bridge.install(_noop_log)

from proxy import proxy_config
from proxy.stats import stats as proxy_stats
from proxy.tg_ws_proxy import _run
from ui.window import MainWindow
from ui.proxy_store import ensure_secret

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("main")


class ProxyRunner:
    """Пересоздаёт loop при каждом старте — чтобы Стоп→Старт работало."""

    def __init__(self, ui):
        self.ui = ui
        self._loop = None
        self._thread = None
        self._stop_event = None
        self._task = None
        self._running = False
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            if self._running:
                self.ui.log("proxy already running")
                return

            self._loop = asyncio.new_event_loop()
            self._stop_event = asyncio.Event()

            def runner():
                try:
                    asyncio.set_event_loop(self._loop)
                    self._loop.run_until_complete(_run(self._stop_event))
                except OSError as e:
                    self.ui.log("PORT ERROR: " + str(e))
                except Exception as e:
                    self.ui.log("PROXY ERROR: " + str(e))
                finally:
                    try:
                        self._loop.close()
                    except Exception:
                        pass
                    self._loop = None
                    self._running = False

            try:
                self._thread = threading.Thread(target=runner, daemon=True,
                                                name="proxy-runner")
                self._thread.start()
                self._running = True
                self.ui.log("proxy listening on " +
                            str(proxy_config.host) + ":" +
                            str(proxy_config.port))
            except Exception as e:
                self.ui.log("START ERROR: " + str(e))

    def stop(self):
        with self._lock:
            if not self._running:
                return
            try:
                if self._stop_event is not None and self._loop is not None:
                    self._loop.call_soon_threadsafe(self._stop_event.set)
            except Exception as e:
                self.ui.log("STOP ERROR: " + str(e))

        # Подождём завершения потока (максимум 3 сек)
        try:
            if self._thread is not None:
                self._thread.join(timeout=3.0)
        except Exception:
            pass

        # Если поток не завершился — принудительно закрываем loop
        try:
            if self._thread is not None and self._thread.is_alive():
                if self._loop is not None:
                    try:
                        self._loop.call_soon_threadsafe(self._loop.stop)
                    except Exception:
                        pass
                self._thread.join(timeout=1.0)
        except Exception:
            pass

        with self._lock:
            self._running = False
            self._thread = None
            self._loop = None
            self.ui.log("proxy stopped")




def get_stats():
    return proxy_stats


def main():
    proxy_config.host = "127.0.0.1"
    proxy_config.port = 1443

    # Постоянный secret — читается из proxy_link.txt,
    # генерируется один раз и больше не меняется.
    try:
        secret = ensure_secret(proxy_config.host, proxy_config.port)
        proxy_config.secret = secret
    except Exception as e:
        log.error("cannot load secret: %s", e)

    app = MainWindow(proxy_config, on_start=lambda: None,
                     on_stop=lambda: None, get_stats=get_stats)
    runner = ProxyRunner(app)
    app.on_start = runner.start
    app.on_stop = runner.stop

    # Автозапуск прокси при старте приложения
    try:
        app.after(300, runner.start)
    except Exception:
        pass

    app.mainloop()


if __name__ == "__main__":
    main()
