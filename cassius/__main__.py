"""CLI-Einstieg: `python -m cassius run [--mock] [--limit N] [--config PATH]`."""

from __future__ import annotations

import argparse
import sys

from .config import Config
from .pipeline import run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cassius",
        description="Cassius — KI-gestützte Analyse von Nachrichtentexten auf Framing und Fehlschlüsse.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Pipeline ausführen und Website bauen")
    p_run.add_argument("--mock", action="store_true", help="Offline-Demo mit Fixture-Daten (kein API-Schlüssel nötig)")
    p_run.add_argument("--limit", type=int, default=None, help="Nur die ersten N Artikel analysieren (Echtbetrieb)")
    p_run.add_argument("--config", default=None, help="Pfad zu sources.yaml")
    p_run.add_argument("--out", default="site", help="Ausgabeverzeichnis der Website")

    args = parser.parse_args(argv)

    if args.command == "run":
        cfg = Config.load(args.config)
        try:
            run(cfg, mock=args.mock, limit=args.limit, out_dir=args.out)
        except Exception as exc:
            print(f"Fehler: {exc}", file=sys.stderr)
            if not args.mock:
                print(
                    "Tipp: Für den Echtbetrieb ANTHROPIC_API_KEY setzen oder `ant auth login` ausführen.\n"
                    "Zum Ausprobieren ohne Schlüssel: `python -m cassius run --mock`.",
                    file=sys.stderr,
                )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
