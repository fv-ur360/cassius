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

## Betriebsmodus: privates Solo-Werkzeug (Standard)

Cassius läuft standardmäßig als **privates Werkzeug** (`access.mode: private` in
`config/sources.yaml`): nur mit Passwort erreichbar, nur an `127.0.0.1` gebunden,
**kein Publikum, kein Dritter**. In diesem Modus analysiert er für *dich* — ohne die
Pflichten (Impressum, V.i.S.d.P.), die erst greifen, sobald etwas öffentlich an Dritte
geht. Das Compliance-Gate ist hier durchlässig; der öffentliche Modus ist später ein
einziger Schalter (`access.mode: public`).

## Schnellstart

```bash
# 1. Abhängigkeiten
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Demo ohne API-Schlüssel (nutzt Fixture-Daten)
python -m cassius run --mock

# 3. Echter Lauf (braucht ANTHROPIC_API_KEY oder `ant auth login`)
export ANTHROPIC_API_KEY="sk-ant-..."
python -m cassius run                 # einmalig, nur neue Artikel (Dedup)

# 4. Vollautomatik (läuft in Schleife)
python -m cassius auto --interval 3600

# 5. Privat ansehen (passwortgeschützt, nur lokal)
export CASSIUS_PASSWORD="dein-passwort"
python -m cassius serve --port 8000   # → http://localhost:8000 (Nutzer „cassius")
```

- **Gedächtnis**: Cassius überspringt bereits analysierte Artikel und sammelt Muster,
  die als *Kontext* (nie als Regel) in neue Analysen zurückfließen — siehe Seite „Gelernt".
- **Konfiguration**: `config/sources.yaml` (Feeds, Sprache, Modell, Zugang, Automatik,
  Gate). Standard-Modell: `claude-opus-4-8`.
- **Privatsphäre**: Das Gedächtnis (`data/state/`) ist aus dem Repo ausgeschlossen —
  reale Analysen landen nie im öffentlichen Repository.

## ⚠️ Öffentliches Repo — Nutzung auf eigene Gefahr

Dieses Repository ist öffentlich und der Code steht unter MIT (ohne Gewähr, ohne
Haftung — siehe `LICENSE`). **Wer eine eigene Instanz betreibt, tut das auf eigene
Verantwortung.** Sobald du Analysen *veröffentlichst* (Modus `public`, für Dritte
erreichbar), bist du der **Betreiber** im Sinne von EU AI Act und DSGVO und trägst die
Verantwortung für Kennzeichnung, Impressum/V.i.S.d.P. und die getätigten Aussagen. Lies
vorher `docs/COMPLIANCE.md` und `docs/ETHICS.md`. Für den öffentlichen Betrieb mit
Bezug auf benannte Personen ist ein einmaliger Blick eines Fachanwalts für Medienrecht
dringend zu empfehlen.

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
├── cassius/                  · die Pipeline
│   ├── ingest.py             · Feeds einlesen (RSS)
│   ├── analyze.py            · Claude + Persona (Structured Outputs)
│   ├── store.py              · Gedächtnis: Archiv, Dedup, Muster-Lernen
│   ├── gate.py               · Compliance-Gate (privat durchlässig / public scharf)
│   ├── build_site.py         · statische Website (Jinja2)
│   ├── serve.py              · passwortgeschütztes privates Ausliefern
│   └── pipeline.py           · Orchestrierung + Vollautomatik
├── templates/                · Jinja2-HTML (mit Compliance-Kennzeichnung)
├── static/                   · CSS
├── data/fixtures/            · Beispieldaten für den Mock-Modus
└── data/state/               · Gedächtnis zur Laufzeit (NICHT im Repo)
```

## Lizenz & Verantwortung

MIT (siehe `LICENSE`). Wer das Repo betreibt, ist der **Betreiber** im Sinne des
EU AI Act und trägt die Verantwortung dafür, dass die Kennzeichnungspflichten
eingehalten und keine benannten Personen diffamiert werden. Lies vor dem Betrieb
`docs/COMPLIANCE.md` und `docs/ETHICS.md`.
