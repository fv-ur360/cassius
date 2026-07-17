# EU-AI-Act-Konformität

> Dieses Dokument bildet das Projekt auf die **Transparenzpflichten der Verordnung (EU)
> 2024/1689 (KI-Verordnung / „AI Act")** ab. Es ist keine Rechtsberatung. Wer das Repo
> betreibt, ist im Sinne der Verordnung **Betreiber** (deployer) und trägt die
> Verantwortung. Im Zweifel eine Fachanwältin oder einen Fachanwalt für IT-/Medienrecht
> hinzuziehen.

## Warum dieses Projekt überhaupt betroffen ist

Der Kern des Systems ist: **eine KI erzeugt Text zu Themen von öffentlichem Interesse
(Nachrichten, öffentliche Debatte) und veröffentlicht ihn.** Genau das ist der
Anwendungsfall, den **Artikel 50 der KI-Verordnung** adressiert. Die einschlägigen
Transparenzpflichten gelten ab dem **2. August 2026**. Wir setzen sie ab Tag 1 um.

## Die vier relevanten Pflichten — und wie wir sie erfüllen

### 1. Art. 50 Abs. 4 — Kennzeichnung KI-erzeugter Texte zu Themen öffentlichen Interesses
**Pflicht:** Wer KI-generierten oder -manipulierten Text veröffentlicht, um die
Öffentlichkeit über Angelegenheiten von öffentlichem Interesse zu informieren, muss
offenlegen, dass der Text künstlich erzeugt wurde. (Ausnahme nur bei menschlicher
redaktioneller Kontrolle mit klarer redaktioneller Verantwortung.)

**Umsetzung:**
- Auf **jeder** Analyse-Seite ein sichtbarer, nicht wegklickbarer Hinweis:
  „🤖 Von KI erstellt · fiktive Kunstfigur · kein journalistisches Urteil".
- Der Hinweis steht **über** dem Inhalt, nicht im Kleingedruckten.
- Siehe `templates/base.html` (`ai-disclosure`-Banner) und `templates/article.html`.

### 2. Art. 50 Abs. 2 — Maschinenlesbare Markierung synthetischer Inhalte
**Pflicht:** Anbieter von KI, die synthetische Inhalte erzeugt, müssen die Ausgaben in
einem **maschinenlesbaren Format** als künstlich erzeugt markieren.

**Umsetzung (in jeder generierten HTML-Seite):**
- `<meta name="ai-generated" content="true">`
- `<meta name="generator" content="Cassius AI (claude-opus-4-8)">`
- `JSON-LD`-Block mit `"isAccessibleForFree": true` und einem `disambiguatingDescription`,
  der den KI-Ursprung und den Fiktionscharakter benennt.
- Siehe `cassius/build_site.py` und `templates/base.html`.

> Hinweis: Der AI Act verweist auf sich entwickelnde Standards (z. B. C2PA / Content
> Credentials) für die maschinenlesbare Markierung. Meta-Tags + JSON-LD sind der
> pragmatische Einstieg; ein späterer C2PA-Manifest-Anhang ist in der Roadmap vermerkt.

### 3. Art. 50 Abs. 1 — Offenlegung bei KI-Interaktion
**Pflicht:** Interagiert ein Mensch mit einem KI-System, muss ihm das mitgeteilt werden,
sofern es nicht offensichtlich ist.

**Umsetzung:** Die Website ist rein lesend (kein Chat). Trotzdem ist der KI-Ursprung auf
jeder Seite und im „Über Cassius"-Bereich klar benannt. Falls später ein interaktiver
Chat ergänzt wird, muss dieser beim ersten Kontakt „Du sprichst mit einer KI" ausgeben.

### 4. Kunst- und Fiktions-Ausnahme (Art. 50 Abs. 4 UAbs. 2) — bewusst NICHT als Schlupfloch genutzt
Die Verordnung erlaubt für **offensichtlich künstlerische/fiktionale** Werke eine
reduzierte Kennzeichnung. Cassius **ist** eine Kunstfigur — aber weil die Analysen reale
Nachrichten betreffen, verlassen wir uns **nicht** auf diese Ausnahme. Wir kennzeichnen
voll (Punkte 1–3). Die Fiktion betrifft die **Stimme**, nicht die Analyse; beides wird
getrennt ausgewiesen.

## Zusätzliche Rechtspflichten (nicht AI Act, aber Betrieb betreffend)

| Bereich | Pflicht | Umsetzung im Projekt |
|---|---|---|
| **Urheberrecht** | Keine Volltext-Reproduktion; Zitatrecht (§ 51 UrhG) | Nur kurze Beleg-Zitate; Link auf Original; keine Speicherung ganzer Artikel |
| **Persönlichkeitsrecht / üble Nachrede** | Keine unwahren Tatsachenbehauptungen über benannte Personen | Persona- und Analyse-Prompt verbieten Aussagen über *Absichten* benannter Personen; nur Argumentstruktur |
| **DSGVO** | Keine unnötige Verarbeitung personenbezogener Daten | Nur öffentliche Feed-Metadaten; keine Nutzerprofile; keine Tracker |
| **Quellen-ToS / robots.txt** | Nutzungsbedingungen der Quellen achten | Nur offizielle RSS/News-APIs; Rate-Limits respektieren |
| **Impressum / Anbieterkennzeichnung** | § 5 DDG (ehem. TMG) | `templates/about.html` enthält Platzhalter — vom Betreiber auszufüllen |

## Betreiber-Checkliste vor dem Livegang

- [ ] Impressum in `about.html` mit echten Kontaktdaten ausgefüllt
- [ ] Nur Quellen genutzt, deren ToS API-/RSS-Nutzung erlauben
- [ ] Sichtbarer KI-Hinweis auf jeder Seite geprüft (Banner + Meta + JSON-LD)
- [ ] Stichprobe: kein Befund unterstellt einer benannten Person böse Absicht
- [ ] Datenschutzhinweis ergänzt (auch wenn keine Tracker: DSGVO-Transparenz)
- [ ] Klar dokumentiert, dass **Konfidenzwerte** und **blinde Flecken** angezeigt werden
- [ ] Verantwortliche natürliche/juristische Person als Betreiber benannt

## Roadmap Compliance
- C2PA / Content-Credentials-Manifest an die HTML-Ausgabe anhängen
- Optionaler menschlicher Review-Schritt vor Veröffentlichung (verschiebt die Rolle
  Richtung „redaktionelle Verantwortung" nach Art. 50 Abs. 4)
- Einspruchs-/Korrekturkanal für Betroffene (Notice-and-Action)
