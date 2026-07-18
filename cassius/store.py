"""Persistentes Gedächtnis: Archiv, Dedup und begrenztes Lernen.

Das ist der „autodidaktische" Teil — aber bewusst begrenzt: Cassius merkt sich,
was er gesehen hat (Dedup), sammelt Muster (welche Quelle neigt wozu) und kann
dieses Wissen als *Kontext* in künftige Analysen zurückgeben. Er verändert damit
niemals seine eigenen Regeln — er lernt Beobachtungen, nicht Gebote.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from .models import AnalyzedArticle

REPO_ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = REPO_ROOT / "data" / "state"


class Store:
    def __init__(self, state_dir: Path | None = None):
        self.dir = Path(state_dir) if state_dir else STATE_DIR
        self.dir.mkdir(parents=True, exist_ok=True)
        self.archive_path = self.dir / "archive.jsonl"
        self.seen_path = self.dir / "seen.json"
        self.patterns_path = self.dir / "patterns.json"
        self.feedback_path = self.dir / "feedback.jsonl"

    # --- Dedup ---------------------------------------------------------------
    def seen_urls(self) -> set[str]:
        if not self.seen_path.exists():
            return set()
        return set(json.loads(self.seen_path.read_text(encoding="utf-8")))

    def _mark_seen(self, url: str) -> None:
        seen = self.seen_urls()
        seen.add(url)
        self.seen_path.write_text(json.dumps(sorted(seen)), encoding="utf-8")

    # --- Archiv (die Grundlage der Website) ----------------------------------
    def load_archive(self) -> list[AnalyzedArticle]:
        if not self.archive_path.exists():
            return []
        items: dict[str, AnalyzedArticle] = {}
        for line in self.archive_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            a = AnalyzedArticle.model_validate_json(line).clamp()
            items[a.article.url] = a  # spätere Fassung gewinnt
        return list(items.values())

    def add(self, analyzed: AnalyzedArticle) -> None:
        with self.archive_path.open("a", encoding="utf-8") as fh:
            fh.write(analyzed.model_dump_json() + "\n")
        self._mark_seen(analyzed.article.url)
        self._update_patterns(analyzed)

    # --- Lernen (Muster-Bibliothek) ------------------------------------------
    def patterns(self) -> dict:
        if not self.patterns_path.exists():
            return {"total": 0, "clean": 0, "by_source": {}, "categories": {}}
        return json.loads(self.patterns_path.read_text(encoding="utf-8"))

    def _update_patterns(self, analyzed: AnalyzedArticle) -> None:
        p = self.patterns()
        p["total"] = p.get("total", 0) + 1
        if not analyzed.analysis.befunde:
            p["clean"] = p.get("clean", 0) + 1

        src = analyzed.article.source
        by_source = p.setdefault("by_source", {})
        entry = by_source.setdefault(src, {"count": 0, "categories": {}, "conf_sum": 0.0})
        entry["count"] += 1
        entry["conf_sum"] = round(entry.get("conf_sum", 0.0) + analyzed.analysis.gesamt_konfidenz, 3)

        cats = p.setdefault("categories", {})
        for f in analyzed.analysis.befunde:
            cats[f.art] = cats.get(f.art, 0) + 1
            entry["categories"][f.art] = entry["categories"].get(f.art, 0) + 1

        self.patterns_path.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")

    def patterns_brief(self, max_sources: int = 6) -> str:
        """Kompakter Gedächtnis-Auszug, der als Kontext in die Analyse zurückfließt.

        Reine Beobachtung — keine neuen Regeln. Leer, solange nichts gelernt wurde.
        """
        p = self.patterns()
        if p.get("total", 0) == 0:
            return ""
        lines = [f"Bisher {p['total']} Analysen, davon {p.get('clean', 0)} ohne Befund."]
        top_sources = sorted(
            p.get("by_source", {}).items(), key=lambda kv: kv[1]["count"], reverse=True
        )[:max_sources]
        for src, entry in top_sources:
            if not entry.get("categories"):
                lines.append(f"- {src}: {entry['count']} Analysen, bisher unauffällig.")
                continue
            dom = Counter(entry["categories"]).most_common(2)
            doms = ", ".join(f"{c} ({n})" for c, n in dom)
            lines.append(f"- {src}: {entry['count']} Analysen, häufigste Befunde {doms}.")
        return "\n".join(lines)

    # --- Feedback (optional, für spätere Verfeinerung) -----------------------
    def record_feedback(self, article_id: str, verdict: str, note: str = "") -> None:
        rec = {"id": article_id, "verdict": verdict, "note": note}
        with self.feedback_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # --- Kennzahlen für die „Gelernt"-Seite ----------------------------------
    def stats(self) -> dict:
        p = self.patterns()
        total = p.get("total", 0)
        clean = p.get("clean", 0)
        return {
            "total": total,
            "clean": clean,
            "clean_rate": round(100 * clean / total) if total else 0,
            "categories": dict(sorted(p.get("categories", {}).items(), key=lambda kv: kv[1], reverse=True)),
            "by_source": p.get("by_source", {}),
        }
