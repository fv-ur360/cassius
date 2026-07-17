"""Datenmodelle für Cassius.

Die Modelle sind bewusst so gebaut, dass die Leitplanken *strukturell* erzwungen
werden: jeder Befund trägt einen Beleg und eine Konfidenz, jede Analyse trägt
ausgewiesene blinde Flecken. Fehlbarkeit ist kein Nachgedanke, sondern Teil des Schemas.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

# Kategorien von Befunden. Als Literal → sauberes Enum im JSON-Schema für Structured Outputs.
Kategorie = Literal[
    "fehlschluss",          # logischer Fehlschluss
    "framing",              # Rahmung durch Auswahl/Reihenfolge/Setzung
    "suggestivsprache",     # wertende statt beschreibende Wortwahl
    "fehlender_kontext",    # was fehlt, um fair urteilen zu können
    "unbelegte_behauptung", # behauptet, aber nicht gezeigt
    "false_balance",        # inszenierte Ausgewogenheit gegen die Belege
]

Schwere = Literal["niedrig", "mittel", "hoch"]


class Finding(BaseModel):
    """Ein einzelner Befund im Text. Ohne Beleg kein Befund."""

    art: Kategorie
    beschreibung: str            # was am Text auffällt — über die Struktur, nie über Absichten
    beleg: str                   # kurzes wörtliches Zitat / konkrete Stelle aus dem Text
    konfidenz: float             # 0.0–1.0; niedrig, wo es subjektiv ist
    schwere: Schwere


class ArticleAnalysis(BaseModel):
    """Das strukturierte Analyse-Ergebnis, das die KI liefert."""

    einordnung: str              # Gesamteinordnung (Schwäche vs. systematische Perfidie)
    befunde: list[Finding]       # kann leer sein — ein sauberer Text ist ein gutes Ergebnis
    blinde_flecken: list[str]    # was Cassius NICHT beurteilen kann
    cassius_kommentar: str       # die Stimme: zynisch, präzise, ohne Häme gegen Schwache
    gesamt_konfidenz: float      # 0.0–1.0 über die gesamte Analyse


class Article(BaseModel):
    """Ein eingelesener Nachrichtenartikel (nur öffentliche Feed-Metadaten)."""

    id: str
    title: str
    source: str
    url: str
    published: str
    region: str
    lang: str
    snippet: str                 # kurzer Auszug aus der Feed-Zusammenfassung (Zitatrecht)


class AnalyzedArticle(BaseModel):
    """Artikel + Analyse + Provenienz. Die Provenienz ist Teil der Kennzeichnung."""

    article: Article
    analysis: ArticleAnalysis
    model: str                   # welches KI-Modell die Analyse erzeugt hat
    generated_at: str            # ISO-Zeitstempel der Erzeugung
    mock: bool = False           # True = Demo-/Fixture-Daten, keine echte KI-Ausgabe

    def clamp(self) -> "AnalyzedArticle":
        """Konfidenzwerte defensiv in [0,1] halten (das Modell hält sich meist daran)."""
        self.analysis.gesamt_konfidenz = _clamp01(self.analysis.gesamt_konfidenz)
        for f in self.analysis.befunde:
            f.konfidenz = _clamp01(f.konfidenz)
        return self


def _clamp01(x: float) -> float:
    try:
        return max(0.0, min(1.0, float(x)))
    except (TypeError, ValueError):
        return 0.0
