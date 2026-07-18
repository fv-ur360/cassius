"""CLI-Einstieg für Cassius.

  python -m cassius run   [--mock] [--limit N] [--config PATH] [--out DIR]
  python -m cassius auto  [--interval SEK] [--config PATH] [--out DIR]
  python -m cassius serve [--port N] [--host H] [--out DIR] [--password PW]
"""

from __future__ import annotations

import argparse
import sys

from .config import Config
from .pipeline import auto, run
from .serve import serve


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cassius",
        description="Cassius — privates KI-Werkzeug zur Analyse von Nachrichten auf Framing und Fehlschlüsse.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Einmal ausführen und Website bauen")
    p_run.add_argument("--mock", action="store_true", help="Offline-Demo mit Fixture-Daten (kein API-Schlüssel nötig)")
    p_run.add_argument("--limit", type=int, default=None, help="Nur die ersten N neuen Artikel analysieren")
    p_run.add_argument("--config", default=None, help="Pfad zu sources.yaml")
    p_run.add_argument("--out", default="site", help="Ausgabeverzeichnis der Website")

    p_auto = sub.add_parser("auto", help="Vollautomatik: in Schleife laufen lassen")
    p_auto.add_argument("--interval", type=int, default=None, help="Sekunden zwischen den Läufen")
    p_auto.add_argument("--config", default=None, help="Pfad zu sources.yaml")
    p_auto.add_argument("--out", default="site", help="Ausgabeverzeichnis der Website")

    p_serve = sub.add_parser("serve", help="Website privat (passwortgeschützt) ausliefern")
    p_serve.add_argument("--host", default="127.0.0.1", help="Bind-Adresse (Standard: nur lokal)")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.add_argument("--out", default="site", help="Verzeichnis der gebauten Website")
    p_serve.add_argument("--password", default=None, help="Passwort (sonst aus Umgebungsvariable)")
    p_serve.add_argument("--config", default=None, help="Pfad zu sources.yaml")

    args = parser.parse_args(argv)
    cfg = Config.load(getattr(args, "config", None))

    try:
        if args.command == "run":
            run(cfg, mock=args.mock, limit=args.limit, out_dir=args.out)
        elif args.command == "auto":
            auto(cfg, interval=args.interval, out_dir=args.out)
        elif args.command == "serve":
            serve(
                directory=args.out,
                host=args.host,
                port=args.port,
                user=cfg.auth_user,
                password=args.password,
                password_env=cfg.password_env,
            )
    except KeyboardInterrupt:
        print("\n· Abgebrochen.")
        return 130
    except Exception as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        if getattr(args, "command", None) != "run" or not getattr(args, "mock", False):
            print(
                "Tipp: Für echte Läufe ANTHROPIC_API_KEY setzen (oder `ant auth login`).\n"
                "Ausprobieren ohne Schlüssel: `python -m cassius run --mock`.",
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
