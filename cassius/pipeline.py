"""Orchestrierung: einlesen → analysieren → Gate → Website aus dem Archiv bauen.

Neu in v0.2 (privates Solo-Werkzeug):
- Inkrementell: bereits analysierte Artikel werden übersprungen (Dedup via Store).
- Gedächtnis: der Store sammelt Muster und gibt sie als Kontext in neue Analysen.
- Gate: im Privatmodus durchlässig, im Public-Modus scharf.
- Die Website wird immer aus dem *gesamten Archiv* gebaut, nicht nur aus dem letzten Lauf.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from .analyze import Analyzer
from .build_site import build_site
from .config import Config
from .gate import classify
from .ingest import fetch_articles
from .models import AnalyzedArticle
from .store import Store

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "data" / "fixtures" / "sample_articles.json"


def load_fixtures() -> list[AnalyzedArticle]:
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    return [AnalyzedArticle.model_validate(item).clamp() for item in data]


def _analyze_new(cfg: Config, store: Store, limit: int | None) -> int:
    seen = store.seen_urls()
    articles = [a for a in fetch_articles(cfg) if a.url not in seen]
    if limit is not None:
        articles = articles[:limit]
    if not articles:
        print("· Keine neuen Artikel.")
        return 0

    print(f"· {len(articles)} neue Artikel. Analysiere mit {cfg.model_id} …")
    analyzer = Analyzer(cfg)
    count = 0
    for i, article in enumerate(articles, 1):
        print(f"  [{i}/{len(articles)}] {article.title[:70]}")
        brief = store.patterns_brief() if cfg.learning_enabled else ""
        try:
            analyzed = analyzer.analyze(article, memory_brief=brief)
            store.add(analyzed)
            count += 1
        except Exception as exc:  # ein Ausfall stoppt den Lauf nicht
            print(f"    ! übersprungen: {exc}")
    return count


def run(cfg: Config, mock: bool = False, limit: int | None = None, out_dir: str = "site") -> Path:
    store = Store()

    if mock:
        if not store.load_archive():
            print("· Mock-Modus: Fixture-Daten ins Archiv laden (keine echte KI, kein Netz)")
            for a in load_fixtures():
                store.add(a)
        else:
            print("· Mock-Modus: Archiv bereits vorhanden, baue daraus")
    else:
        print(f"· Lese Feeds ({len(cfg.feeds)} Quellen) …")
        _analyze_new(cfg, store, limit)

    # Website aus dem gesamten Archiv bauen, Gate anwenden
    archive = store.load_archive()
    published: list[AnalyzedArticle] = []
    held: list[AnalyzedArticle] = []
    for a in archive:
        decision, reasons = classify(cfg, a)
        (published if decision == "publish" else held).append(a)

    mode = "privat (Gate durchlässig)" if cfg.access == "private" else "öffentlich (Gate scharf)"
    print(f"· Modus: {mode} · veröffentlicht: {len(published)} · zurückgehalten: {len(held)}")

    out = build_site(cfg, published, store.stats(), out_dir=out_dir)
    print(f"· Fertig. {out}/index.html")
    return out


def auto(cfg: Config, interval: int | None = None, out_dir: str = "site") -> None:
    """Vollautomatik: läuft in Schleife, analysiert nur Neues, baut neu."""
    interval = interval or cfg.interval_seconds
    print(f"· Vollautomatik gestartet · Intervall {interval}s · Strg-C beendet")
    round_no = 0
    while True:
        round_no += 1
        print(f"\n=== Lauf {round_no} ===")
        try:
            run(cfg, mock=False, out_dir=out_dir)
        except Exception as exc:
            print(f"! Lauf fehlgeschlagen: {exc}")
        print(f"· Warte {interval}s …")
        time.sleep(interval)
