"""Compliance-Gate — der spätere Schalter von privat zu öffentlich.

Im Privatmodus (Solo-Werkzeug) ist das Gate durchlässig: alles wird behalten, denn
es gibt kein Publikum und keinen Dritten. Im Public-Modus wird es scharf: es lässt
nur die risikoarme Klasse durch (Werturteil über Textstruktur, Konfidenz über
Schwelle, kein Denylist-Treffer) und hält alles andere zurück.
"""

from __future__ import annotations

from .config import Config
from .models import AnalyzedArticle


def _haystack(a: AnalyzedArticle) -> str:
    parts = [a.article.title, a.analysis.einordnung, a.analysis.cassius_kommentar]
    for f in a.analysis.befunde:
        parts.append(f.beschreibung)
        parts.append(f.beleg)
    return " ".join(parts).lower()


def classify(cfg: Config, a: AnalyzedArticle) -> tuple[str, list[str]]:
    """Gibt (Entscheidung, Gründe) zurück. Entscheidung: 'publish' oder 'hold'."""
    # Privatmodus: Solo-Werkzeug, kein Dritter → alles wird behalten.
    if cfg.access == "private":
        return ("publish", [])

    reasons: list[str] = []
    hay = _haystack(a)

    for term in cfg.denylist:
        t = term.strip().lower()
        if t and t in hay:
            reasons.append(f"Denylist-Treffer: „{term}“")

    if a.analysis.gesamt_konfidenz < cfg.gate_min_confidence:
        reasons.append(
            f"Konfidenz unter Schwelle ({a.analysis.gesamt_konfidenz:.2f} < {cfg.gate_min_confidence:.2f})"
        )

    return ("hold", reasons) if reasons else ("publish", [])
