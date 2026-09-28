"""Run the local reader: uv run python -m tools.reader_server --open."""
from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from tools.reader_store import ROOT, Conflict, ReaderStore, StoreError


class ReaderHandler(BaseHTTPRequestHandler):
    server_version = "GamebookReader/0.1"

    def log_message(self, format, *args):
        # Keep reader feedback and request bodies out of terminal logs.
        if args and str(args[1] if len(args) > 1 else "").startswith("5"):
            super().log_message(format, *args)

    def reply(self, status, body, content_type="application/json; charset=utf-8", attachment=None):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        if attachment:
            self.send_header("Content-Disposition", f'attachment; filename="{attachment}"')
        self.end_headers()
        self.wfile.write(body)

    def host_allowed(self):
        return self.headers.get("Host") in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}

    def do_GET(self):
        self.dispatch(False)

    def do_POST(self):
        self.dispatch(True)

    def dispatch(self, mutation):
        try:
            if not self.host_allowed():
                return self.reply(403, {"error": "This reader accepts local browser connections only."})
            url = urlsplit(self.path)
            parts = url.path.strip("/").split("/")
            store = self.server.store
            data = {}
            if mutation:
                origin = self.headers.get("Origin")
                if origin and origin != "http://" + self.headers["Host"]:
                    return self.reply(403, {"error": "Cross-site requests are not accepted."})
                if self.headers.get_content_type() != "application/json":
                    return self.reply(415, {"error": "Expected a JSON request."})
                length = int(self.headers.get("Content-Length", "0"))
                if not 0 < length <= 128000:
                    return self.reply(413, {"error": "Request is empty or too large."})
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise StoreError("Expected a JSON object.")
            if not mutation and url.path == "/api/bootstrap":
                return self.reply(200, store.bootstrap())
            if mutation and url.path == "/api/sessions":
                return self.reply(201, store.create(data.get("label", "")))
            if len(parts) >= 3 and parts[:2] == ["api", "sessions"]:
                identifier = parts[2]
                if not mutation and len(parts) == 3:
                    viewing = parse_qs(url.query).get("passage", [None])[0]
                    return self.reply(200, store.read(identifier, viewing))
                if not mutation and parts[3:] == ["report"]:
                    return self.reply(200, store.report(identifier), "text/markdown; charset=utf-8", f"tower-{identifier[:8]}.md")
                if mutation and parts[3:] == ["action"]:
                    return self.reply(200, store.action(identifier, data.get("action"), data.get("payload", {}), data.get("version")))
                if mutation and parts[3:] == ["notes"]:
                    return self.reply(200, store.note(identifier, data.get("text"), data.get("quote", ""), data.get("passage"), data.get("version")))
            static = {"/": "index.html", "/index.html": "index.html", "/app.js": "app.js", "/styles.css": "styles.css"}
            if not mutation and url.path in static:
                path = ROOT / "reader" / static[url.path]
                mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
                return self.reply(200, path.read_bytes(), mime + "; charset=utf-8")
            return self.reply(404, {"error": "Page not found."})
        except Conflict as error:
            self.reply(409, {"error": str(error)})
        except (ValueError, TypeError) as error:
            self.reply(400, {"error": str(error)})
        except Exception:
            import traceback
            traceback.print_exc()
            self.reply(500, {"error": "The reader could not complete this request. Your previous save is intact; check the server terminal."})


def make_server(port=8767, sessions_dir=None):
    server = ThreadingHTTPServer(("127.0.0.1", port), ReaderHandler)
    server.store = ReaderStore(sessions_dir or ROOT / ".playtest/browser-sessions")
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8767)
    parser.add_argument("--sessions-dir", type=Path)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()
    try:
        server = make_server(args.port, args.sessions_dir)
    except OSError as error:
        print(f"Could not start the reader: {error}. If it is already running, open http://127.0.0.1:{args.port}.", file=sys.stderr)
        return 1
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"The Tower of the Elephant — {url}\nProgress and notes: {server.store.directory}\nKeep this terminal open while reading. Press Ctrl-C to stop.", flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
