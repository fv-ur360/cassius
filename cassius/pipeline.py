"""Orchestrierung: einlesen → analysieren → Website bauen.

Zwei Modi:
- Echtbetrieb: Feeds abfragen und via Claude analysieren.
- Mock-Modus: Fixture-Daten laden (offline, ohne API-Schlüssel) — für Demo und Layout.
"""

from __future__ import annotations

import json
from pathlib import Path

from .analyze import Analyzer
from .config import Config
from .build_site import build_site
from .ingest import fetch_articles
from .models import AnalyzedArticle

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "data" / "fixtures" / "sample_articles.json"


def load_fixtures() -> list[AnalyzedArticle]:
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    return [AnalyzedArticle.model_validate(item).clamp() for item in data]


def run(cfg: Config, mock: bool = False, limit: int | None = None, out_dir: str = "site") -> Path:
    if mock:
        print("· Mock-Modus: lade Fixture-Daten (keine echte KI, kein Netz)")
        analyzed = load_fixtures()
    else:
        print(f"· Lese Feeds ({len(cfg.feeds)} Quellen) …")
        articles = fetch_articles(cfg)
        if limit is not None:
            articles = articles[:limit]
        print(f"· {len(articles)} Artikel eingelesen. Analysiere mit {cfg.model_id} …")
        analyzer = Analyzer(cfg)
        analyzed = []
        for i, article in enumerate(articles, 1):
            print(f"  [{i}/{len(articles)}] {article.title[:70]}")
            try:
                analyzed.append(analyzer.analyze(article))
            except Exception as exc:  # ein einzelner Ausfall stoppt den Lauf nicht
                print(f"    ! übersprungen: {exc}")

    print(f"· Baue Website ({len(analyzed)} Analysen) → {out_dir}/ …")
    out = build_site(cfg, analyzed, out_dir=out_dir)
    print(f"· Fertig. Öffne {out}/index.html")
    return out
