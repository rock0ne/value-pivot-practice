"""Local stand-in for three suppliers' stock feeds. Runs on 127.0.0.1 only.

/fast-a and /fast-b answer at once. /slow waits SLOW_SECONDS before answering,
like a supplier whose server is struggling. Nothing leaves this machine.
"""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SLOW_SECONDS = 2.0


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/slow":
            time.sleep(SLOW_SECONDS)
        body = json.dumps({"supplier": self.path.strip("/"), "items": 12}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


def start():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"
