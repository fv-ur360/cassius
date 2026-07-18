"""Passwortgeschütztes privates Ausliefern der Website (Basic Auth).

Bindet standardmäßig nur an 127.0.0.1 — die Seite ist damit privat und nur mit
Passwort erreichbar. Das Passwort kommt aus einer Umgebungsvariablen (nie aus dem
Repo). So bleibt das Solo-Werkzeug ein Solo-Werkzeug.
"""

from __future__ import annotations

import base64
import functools
import hmac
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


def serve(
    directory: str = "site",
    host: str = "127.0.0.1",
    port: int = 8000,
    user: str = "cassius",
    password: str | None = None,
    password_env: str = "CASSIUS_PASSWORD",
) -> None:
    password = password or os.environ.get(password_env)
    if not password:
        raise RuntimeError(
            f"Kein Passwort gesetzt. Setze die Umgebungsvariable {password_env} "
            f"(z. B. `export {password_env}=…`) oder gib --password."
        )

    expected = "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()

    class Handler(SimpleHTTPRequestHandler):
        def _authorized(self) -> bool:
            got = self.headers.get("Authorization", "")
            # konstante-Zeit-Vergleich gegen Timing-Seitenkanäle
            return hmac.compare_digest(got, expected)

        def do_GET(self):  # noqa: N802 (Signatur von SimpleHTTPRequestHandler)
            if not self._authorized():
                self.send_response(401)
                self.send_header("WWW-Authenticate", 'Basic realm="Cassius (privat)"')
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write("🔒 Privater Testbetrieb. Zugang nur mit Passwort.".encode())
                return
            super().do_GET()

        def log_message(self, *args):  # ruhiger Betrieb
            pass

    handler = functools.partial(Handler, directory=directory)
    httpd = ThreadingHTTPServer((host, port), handler)
    print(f"· Privat-Server: http://{host}:{port}  (Basic Auth · Nutzer „{user}“)")
    print("· Nur lokal erreichbar. Beenden mit Strg-C.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n· Server beendet.")
