#!/usr/bin/env python3
"""Optional local server for the Harvest Crop Rotation Optimiser.

Serves index.html and proxies /api/prices?league=<league> to poe.ninja
server-side, avoiding poe.ninja's CORS restriction entirely (no public
third-party proxy involved). Only needed if the page's direct-fetch and
public-proxy fallbacks fail; manual price entry always works regardless.

Usage: python3 serve.py [port]   (default port 8420)
Then open http://localhost:8420/ in a browser.
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

NINJA_URL = "https://poe.ninja/poe1/api/economy/exchange/current/overview"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep stdout quiet

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/prices":
            self.handle_prices(urllib.parse.parse_qs(parsed.query))
        elif parsed.path in ("/", "/index.html"):
            self.serve_file("index.html", "text/html; charset=utf-8")
        else:
            self.send_error(404)

    def handle_prices(self, query):
        league = query.get("league", ["Allflame"])[0]
        target = f"{NINJA_URL}?league={urllib.parse.quote(league)}&type=Currency"
        try:
            req = urllib.request.Request(target, headers={"User-Agent": "crop-rotation-tree-calc/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def serve_file(self, name, content_type):
        try:
            with open(name, "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self.send_error(404)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8420
    server = HTTPServer(("localhost", port), Handler)
    print(f"Serving on http://localhost:{port}/  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
