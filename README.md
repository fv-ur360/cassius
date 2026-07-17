# Cassius — Die Spinne im Netz der Nachrichten

> Eine fiktive Kunstfigur, die weltweite Nachrichten auf **logische Fehlschlüsse,
> Framing und rhetorische Manipulation** untersucht — und ihre eigene Fehlbarkeit
> offen ausweist. Legal, quellenbasiert, EU-AI-Act-konform.

**Cassius ist keine reale Person und keine reale Redaktion.** Er ist eine
literarische Persona — die „Spinnensünde der Perfidie" — die Heuchelei entlarvt,
menschliche Schwäche aber verschont. Was hier veröffentlicht wird, sind
**KI-generierte Analysen von Argumentstrukturen**, keine journalistischen
Tatsachenbehauptungen und kein Urteil über die Absichten benannter Menschen.

---

## Was das Projekt ist — und was nicht

**Ist:**
- Ein Werkzeug, das öffentliche Nachrichten über offizielle Kanäle (RSS, News-APIs)
  einliest und jeden Text durch eine KI-gestützte Analyse schickt.
- Die Analyse markiert **Fehlschlüsse, Framing, Suggestivsprache, fehlenden Kontext
  und unbelegte Behauptungen** — jeweils mit **Konfidenzwert** und **Beleg-Zitat**.
- Ein „Beweise, dass wir falsch liegen"-Durchlauf (Red-Teaming) filtert
  überschießende Befunde heraus, bevor etwas veröffentlicht wird.
- Jede Ausgabe endet mit **blinden Flecken** — Dingen, die Cassius *nicht* beurteilen
  kann, weil die Datenlage dünn oder mehrdeutig ist.

**Ist nicht:**
- Kein autonomer, sich selbst verbreitender Agent. Kein Hacking, keine Überwachung,
  kein Krypto-Selbsterhalt. Diese Ideen bleiben **Lore** (siehe `docs/PHILOSOPHY.md`),
  nicht Code.
- Kein Zensur-Werkzeug. Cassius löscht nichts. Er beleuchtet — und lässt den Leser
  urteilen.
- Kein Diffamierungs-Werkzeug. Analysiert werden **Texte und Argumente**, nicht
  Personen.

---

## Wie es funktioniert (Pipeline)

```
  RSS / News-APIs        LLM-Analyse            Red-Team-Pass          Statische Website
 ┌──────────────┐      ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
 │  ingest.py   │ ───▶ │  analyze.py  │ ────▶ │  (in-prompt  │ ────▶ │ build_site.py│
 │  feedparser  │      │  Claude +    │       │  Selbst-     │       │  Jinja2 →    │
 │  Dedup       │      │  Persona     │       │  widerlegung)│       │  HTML        │
 └──────────────┘      └──────────────┘       └──────────────┘       └──────────────┘
```

1. **Einlesen** — Nur öffentliche Quellen über offizielle Feeds. Zitiert wird kurz,
   verlinkt wird immer auf das Original. Keine Volltext-Reproduktion (Zitatrecht).
2. **Analysieren** — `claude-opus-4-8` mit der Cassius-Persona als System-Prompt und
   einem strengen Analyse-Auftrag. Ausgabe ist **strukturiert** (Pydantic-Schema).
3. **Prüfen** — Der Prompt zwingt das Modell, jeden Befund gegen sich selbst zu
   verteidigen und Konfidenz + blinde Flecken auszuweisen.
4. **Veröffentlichen** — Eine statische Website mit **EU-AI-Act-konformer
   Kennzeichnung** (sichtbar + maschinenlesbar) auf jeder Seite.

---

## Schnellstart

```bash
# 1. Abhängigkeiten
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Demo ohne API-Schlüssel (nutzt Fixture-Daten)
python -m cassius run --mock

# 3. Echter Lauf (braucht ANTHROPIC_API_KEY oder `ant auth login`)
export ANTHROPIC_API_KEY="sk-ant-..."
python -m cassius run

# 4. Ergebnis ansehen
python -m http.server -d site 8000   # → http://localhost:8000
```

Die Quellen konfigurierst du in `config/sources.yaml` (Sprache, Region, Feeds,
Modell). Standard: gemischt DE/EN-international, `claude-opus-4-8`.

---

## Projektstruktur

```
cassius/
├── README.md                 · dieses Dokument
├── requirements.txt
├── config/sources.yaml       · Feeds, Region, Sprache, Modell
├── persona/
│   ├── system_prompt.md      · Cassius' Seele (Persona + Leitplanken)
│   └── analysis_prompt.md    · der strukturierte Analyse-Auftrag
├── docs/
│   ├── COMPLIANCE.md         · EU-AI-Act-Abbildung (der wichtige Teil)
│   ├── ETHICS.md             · Leitplanken, Fehlbarkeit, rechtliche Linie
│   └── PHILOSOPHY.md         · die Lore von Cassius (Fiktion)
├── cassius/                  · die Pipeline (ingest · analyze · build)
├── templates/                · Jinja2-HTML (mit Compliance-Kennzeichnung)
├── static/                   · CSS
└── data/fixtures/            · Beispieldaten für den Mock-Modus
```

## Lizenz & Verantwortung

MIT (siehe `LICENSE`). Wer das Repo betreibt, ist der **Betreiber** im Sinne des
EU AI Act und trägt die Verantwortung dafür, dass die Kennzeichnungspflichten
eingehalten und keine benannten Personen diffamiert werden. Lies vor dem Betrieb
`docs/COMPLIANCE.md` und `docs/ETHICS.md`.
