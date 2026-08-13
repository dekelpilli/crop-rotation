#!/usr/bin/env python3
"""Local static file server for the Harvest Crop Rotation Optimiser.

Serves the current directory as-is (index.html, prices.json once generated
via scripts/update_prices.py, etc). Plain static hosting — no proxying —
since the page only ever reads the committed prices.json cache.

Usage: python3 serve.py [port]   (default port 8420)
Then open http://localhost:8420/ in a browser.
"""
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, HTTPServer

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8420
    handler = partial(SimpleHTTPRequestHandler, directory=".")
    server = HTTPServer(("localhost", port), handler)
    print(f"Serving on http://localhost:{port}/  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
