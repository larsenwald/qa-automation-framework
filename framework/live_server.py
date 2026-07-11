"""Runs ShopLite in a background thread against a throwaway SQLite database."""
import threading

from werkzeug.serving import make_server

from shoplite import create_app
from shoplite.seed import seed


class LiveServer:
    def __init__(self, db_path, host="127.0.0.1", port=0):
        self.app = create_app({"TESTING": True, "DATABASE": str(db_path), "SECRET_KEY": "test-secret"})
        self.reset_data()
        self._server = make_server(host, port, self.app, threaded=True)
        self.url = f"http://{host}:{self._server.server_port}"
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def start(self):
        self._thread.start()
        return self

    def stop(self):
        self._server.shutdown()
        self._thread.join(timeout=5)

    def reset_data(self):
        with self.app.app_context():
            seed()
