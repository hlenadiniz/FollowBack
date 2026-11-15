import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from followback.analyzer import analyze  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            size = int(self.headers.get("content-length", 0))
            body = json.loads(self.rfile.read(size))
            status, payload = 200, analyze(body["followers"], body["following"])
        except ValueError as error:
            status, payload = 400, {"error": str(error) or "Arquivos inválidos."}
        except (KeyError, TypeError, AttributeError):
            status, payload = 400, {
                "error": "Arquivos inválidos. Confira os formatos selecionados."
            }
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))
