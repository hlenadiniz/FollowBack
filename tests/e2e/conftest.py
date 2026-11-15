import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from api.analyze import handler as ApiHandler


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_DIR = ROOT / "public"


class FollowBackHandler(SimpleHTTPRequestHandler):
    do_POST = ApiHandler.do_POST

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def log_message(self, format, *args):
        pass


@pytest.fixture
def app_url():
    server = ThreadingHTTPServer(("127.0.0.1", 0), FollowBackHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
