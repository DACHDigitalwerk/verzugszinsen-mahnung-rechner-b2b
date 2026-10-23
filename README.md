# Verzugszinsen & Mahnung Rechner B2B (DACH-Raum) ⚖️💶

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests Passing](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![DACH Digitalwerk](https://img.shields.io/badge/Engine-DACH%20Digitalwerk-orange.svg)](https://dach-digitalwerk.netlify.app/)

> **Das professionelle Open-Source-Toolkit und CLI-Utility für taggenaue kaufmännische Verzugszinsberechnung, gesetzliche Schadenspauschalen und 3-stufiges Mahnwesen in Deutschland (§ 288 BGB), Österreich (§ 456 UGB) und der Schweiz (Art. 104 OR / Art. 67 SchKG).**

---

### 🌐 Interaktive Live-Tools & Leitfäden

* 🚀 **Online-Rechner direkt im Browser nutzen:**  
  👉 **[Mahnung & Verzugszinsen Rechner B2B (Live-Web-App)](https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/)**
* 📖 **Ausführlicher Praxis-Ratgeber & Gesetzesleitfaden:**  
  👉 **[Verzugszinsen berechnen: B2B-Praxisratgeber & Muster](https://dach-digitalwerk.netlify.app/verzugszinsen-berechnen-rechner-b2b.html)**

---

## Inhaltsverzeichnis

1. [Rechtliche Grundlagen im DACH-Raum](#rechtliche-grundlagen-im-dach-raum)
   - [Deutschland (§ 288, § 289, § 247 BGB)](#1-deutschland)
   - [Österreich (§ 456, § 458 UGB, § 1000 ABGB)](#2-österreich)
   - [Schweiz (Art. 104 OR, Art. 67 SchKG)](#3-schweiz)
2. [Gesetzliche 40-€-Schadenspauschale](#die-gesetzliche-40--schadenspauschale-b2b)
3. [Zinseszins-Verbot (§ 289 BGB)](#zinseszins-verbot--289-bgb)
4. [Installation & Schnellstart](#installation--schnellstart)
5. [Python-API Referenz & Beispiele](#python-api-referenz--beispiele)
6. [CLI-Utility `b2b-zinsen`](#cli-utility-b2b-zinsen)
7. [Das 3-stufige Mahnwesen-Muster](#das-3-stufige-mahnwesen-muster)
8. [Rechtlicher Hinweis (RDG / Compliance)](#rechtlicher-hinweis--haftungsausschluss-rdg-compliance)

---

## Rechtliche Grundlagen im DACH-Raum

Der Zahlungsverzug von Geschäftspartnern bindet Liquidität und erfordert ein präzises, rechtssicheres Mahnwesen. Das vorliegende Repository setzt die länderspezifischen Vorschriften der DACH-Region mathematisch und formulierungstechnisch exakt um:

```
                            ┌──────────────────────────────────────────────┐
                            │      Gesetzliche Verzugszinsen im DACH-Raum  │
                            └──────────────────────┬───────────────────────┘
                                                   │
            ┌──────────────────────────────────────┼──────────────────────────────────────┐
            ▼                                      ▼                                      ▼
     DEUTSCHLAND (BGB)                      ÖSTERREICH (UGB)                       SCHWEIZ (OR)
 ─────────────────────────              ─────────────────────────              ─────────────────────────
 • B2B: Basiszinssatz + 9 %             • B2B: Basiszinssatz + 9,2 %           • B2B & B2C: 5,00 % fix
   (z.B. 0,27% + 9% = 9,27 %)             (§ 456 UGB)                            (Art. 104 Abs. 1 OR)
 • B2C: Basiszinssatz + 5 %             • B2B: 40 € Pauschale                  • Keine 40-€-EU-Pauschale
 • 40 € Pauschale (§ 288 Abs. 5)          (§ 458 UGB)                          • Betreibung gem. SchKG
 • Zinseszins-Verbot (§ 289)            • B2C: 4,00 % (§ 1000 ABGB)              (Art. 67 Betreibungsbegehren)
```

### 1. Deutschland

* **B2B-Geschäfte (§ 288 Abs. 2 BGB):**  
  Bei Rechtsgeschäften, an denen ein Verbraucher nicht beteiligt ist (B2B / Unternehmergeschäfte), beträgt der Verzugszinssatz **9 Prozentpunkte über dem Basiszinssatz**.  
  *Beispiel:* Liegt der Basiszinssatz der Deutschen Bundesbank bei `0,27 %`, beläuft sich der gesetzliche B2B-Verzugszinssatz auf exakt **`9,27 % p.a.`**.
* **Verbrauchergeschäfte (§ 288 Abs. 1 BGB):**  
  Ist mindestens eine Vertragspartei ein Verbraucher (B2C), beträgt der Zinssatz **5 Prozentpunkte über dem Basiszinssatz** (z.B. `0,27 % + 5,00 % = 5,27 % p.a.`).
* **Basiszinssatz der Bundesbank (§ 247 BGB):**  
  Wird halbjährlich jeweils zum 1. Januar und 1. Juli von der Deutschen Bundesbank im Bundesanzeiger publiziert.
* **Verzugsbeginn (§ 187 Abs. 1 BGB):**  
  Der Verzug beginnt am Tag *nach* Eintritt der Fälligkeit. Bei kalendermäßig bestimmter Fälligkeit tritt der Verzug ohne gesonderte Mahnung ein (§ 286 Abs. 2 Nr. 1 BGB).

### 2. Österreich

* **Unternehmergeschäfte (§ 456 UGB):**  
  Für Geldforderungen zwischen Unternehmern aus unternehmerischen Geschäften beträgt der gesetzliche Zinssatz **9,2 Prozentpunkte über dem Basiszinssatz** der OeNB.
* **Betreibungskostenpauschale (§ 458 UGB):**  
  Gläubiger haben bei Zahlungsverzug Anspruch auf eine gesetzliche Pauschale von **40,00 Euro** für etwaige Betreibungskosten.
* **Verbraucher (§ 1000 Abs. 1 ABGB):**  
  Der gesetzliche Verzugszins für Verbrauchergeschäfte beträgt fix **4,00 % p.a.**

### 3. Schweiz

* **Gesetzlicher Verzugszins (Art. 104 Abs. 1 OR):**  
  Ist der Schuldner mit einer Geldschuld im Verzug, hat er Verzugszinse von **5,00 % für das Jahr** zu entrichten.
* **Keine EU-Schadenspauschale:**  
  Das Schweizer Obligationenrecht sieht keine gesetzliche 40-€-Pauschale nach EU-Recht vor. Betreibungskosten werden direkt vom zuständigen Betreibungsamt festgesetzt und dem Schuldner auferlegt (Art. 68 SchKG).
* **Betreibungsverfahren (Art. 67 ff. SchKG):**  
  Bleibt die Mahnung fruchtlos, wird das offizielle Betreibungsbegehren beim Betreibungsamt am Wohnsitz bzw. Sitz der Schuldnerin eingereicht.

---

## Die gesetzliche 40-€-Schadenspauschale (B2B)

Gemäß **§ 288 Abs. 5 BGB** (Deutschland) und **§ 458 UGB** (Österreich):

1. **Automatischer Entstehungsanspruch:**  
   Die Pauschale in Höhe von 40 Euro entsteht mit Eintritt des Verzugs unmittelbar kraft Gesetzes. Sie muss weder vorab vereinbart noch nachgewiesen werden.
2. **Reiner B2B-Anspruch:**  
   Sie gilt ausschließlich gegenüber Schuldnern, die keine Verbraucher sind (Unternehmen, Freiberufler, juristische Personen des öffentlichen Rechts).
3. **Anrechnungsvorschrift:**  
   Die Pauschale ist auf einen geschuldeten Schadensersatz anzurechnen, soweit der Schaden in Kosten der Rechtsverfolgung (z.B. Rechtsanwaltsgebühren nach RVG) begründet ist.

---

## Zinseszins-Verbot (§ 289 BGB)

> *„Von Zinsen dürfen Verzugszinsen nicht entrichtet werden.“* (§ 289 Satz 1 BGB)

In der Praxis führt dies bei Raten- und Teilzahlungen häufig zu unzulässigen Berechnungen:
* Zinsen werden taggenau ausschließlich auf den **offenen Nettobetrag der Hauptforderung** berechnet.
* Gemäß **§ 367 Abs. 1 BGB** werden Teilzahlungen in folgender Reihenfolge verrechnet:
  1. Zuerst auf die Kosten (z.B. 40-€-Schadenspauschale)
  2. Danach auf die bereits aufgelaufenen Verzugszinsen
  3. Zuletzt auf die Hauptforderung
* Verbleibende Restzinsen dürfen **zu keinem Zeitpunkt** in die neue Zinsberechnungsgrundlage einbezogen werden. Diese Engine garantiert strikte Konformität mit § 289 BGB.

---

## Installation & Schnellstart

### Installation via pip

```bash
git clone https://github.com/DACHDigitalwerk/verzugszinsen-mahnung-rechner-b2b.git
cd verzugszinsen-mahnung-rechner-b2b
pip install -e .
```

*Keine externen Abhängigkeiten erforderlich (100% Python Standardbibliothek).*

---

## Python-API Referenz & Beispiele

### 1. Taggenaue Zinsberechnung (Deutschland B2B)

```python
from b2b_verzugszinsen import calculate_interest, Jurisdiction, DebtorType

# Beispiel: 10.000 € Hauptforderung, fällig seit 01.01.2024, berechnet zum 31.01.2024 (30 Verzugstage)
# Mit Basiszinssatz 0,27 % -> Zinssatz 9,27 % p.a. (§ 288 Abs. 2 BGB)
result = calculate_interest(
    principal=10000.00,
    due_date="2024-01-01",
    calculation_date="2024-01-31",
    jurisdiction=Jurisdiction.DE,
    debtor_type=DebtorType.B2B,
    custom_base_rate=0.27
)

print(f"Zinssatz:          {result.effective_rate_percent:.2f} % p.a.")
print(f"Verzugszinsen:     {result.accrued_interest:.2f} EUR")
print(f"Schadenspauschale: {result.flat_fee:.2f} EUR")
print(f"Gesamtforderung:   {result.total_due:.2f} EUR")
# Ausgabe:
# Zinssatz:          9.27 % p.a.
# Verzugszinsen:     76.19 EUR
# Schadenspauschale: 40.00 EUR
# Gesamtforderung:   10116.19 EUR
```

### 2. Mahnschreiben generieren (3-stufig)

```python
from b2b_verzugszinsen import create_dunning_letter, DunningLevel, Jurisdiction

letter = create_dunning_letter(
    level=DunningLevel.FIRST_DUNNING,  # 1 = Erinnerung, 2 = 1. Mahnung, 3 = Letzte Mahnung
    creditor_name="Hanseatic Cloud Solutions GmbH",
    debtor_name="Logistik Partner Nord AG",
    invoice_number="RE-2024-8841",
    principal=4500.00,
    due_date="2024-02-15",
    jurisdiction=Jurisdiction.DE,
    creditor_iban="DE89370400440532013000",
    deadline_days=7
)

# Textausgabe für Post / E-Mail
print(letter.to_text())
```

### 3. Berücksichtigung von Teilzahlungen (§ 367 BGB & Zinseszins-Verbot)

```python
from b2b_verzugszinsen import calculate_with_partial_payments

res = calculate_with_partial_payments(
    principal=10000.0,
    due_date="2024-01-01",
    payments=[("2024-02-01", 2000.0)],
    calculation_date="2024-03-01",
    jurisdiction="DE",
    debtor_type="B2B",
    custom_base_rate=0.27
)

print("Rest-Hauptforderung:", res["remaining_principal"], "EUR")
print("Gesamtforderung:    ", res["total_due"], "EUR")
print("Zinseszins vermieden:", res["compound_interest_prevented"])
```

---

## CLI-Utility `b2b-zinsen`

Das Paket enthält eine intuitive Befehlszeilenschnittstelle:

### Verzugszinsen berechnen
```bash
# B2B-Berechnung in Deutschland
b2b-zinsen calc --amount 5000 --due 2024-01-15 --jurisdiction DE --b2b

# Berechnung als JSON für Skripte & APIs
b2b-zinsen calc --amount 12000 --due 2024-03-01 --json
```

### Mahnschreiben erstellen
```bash
b2b-zinsen dunning \
  --level 2 \
  --amount 3200 \
  --due 2024-02-01 \
  --creditor "Muster GmbH" \
  --debtor "Schuldner AG" \
  --invoice-nr "INV-2024-099" \
  --iban "DE02100500001098765432"
```

### Gesetzliche Zinstabelle anzeigen
```bash
b2b-zinsen rates
```

---

## Das 3-stufige Mahnwesen-Muster

Das integrierte Mahnwesen-Modul bildet die gängige kaufmännische Praxis im DACH-Raum ab:

1. **Stufe 1 – Zahlungserinnerung:**
   Freundlicher Hinweis auf das offene Fälligkeitsdatum. Keine Mahngebühren, Verzugszinsen werden rein informativ aufgeführt, um Geschäftsbeziehungen zu schonen.
2. **Stufe 2 – 1. Mahnung:**
   Formelle Mahnung mit Verzugsfeststellung. Taggenaue Berechnung der gesetzlichen Verzugszinsen sowie automatische Ansetzung der **40-€-Schadenspauschale** (§ 288 Abs. 5 BGB / § 458 UGB). Zahlungsfrist 7–10 Tage.
3. **Stufe 3 – 2. Mahnung / Letzte Mahnung:**
   - **Deutschland / Österreich:** Letzte außergerichtliche Frist (3–5 Tage) mit unmissverständlicher Ankündigung des gerichtlichen Mahnverfahrens (Beantragung eines Mahnbescheids) und Abgabe an die Rechtsabteilung bzw. ein Inkassounternehmen.
   - **Schweiz:** Formelle Betreibungsankündigung gem. **Art. 67 SchKG** mit Hinweis auf Einreichung des Betreibungsbegehrens beim Betreibungsamt am Sitz des Schuldners.

---

## Tests ausführen

Die Test-Suite deckt alle rechtlichen Fallkonstellationen lückenlos ab:

```bash
python -m unittest discover -s tests -v
```

Enthaltene Tests:
* `test_bundesbank_basiszinssatz`: Prüfung der Stichtage zum 01.01. und 01.07.
* `test_b2b_9_percent_rule`: Deutschland § 288 Abs. 2 BGB (0,27 % + 9 % = 9,27 %)
* `test_b2c_5_percent_rule`: Deutschland § 288 Abs. 1 BGB (0,27 % + 5 % = 5,27 %)
* `test_40_euro_pauschale`: § 288 Abs. 5 BGB und § 458 UGB
* `test_zinseszins_ausschluss`: Verbot des Zinseszinses gem. § 289 BGB bei unterjährigen Teilzahlungen (§ 367 BGB)
* `test_schkg_betreibungsmuster`: Schweiz Art. 104 OR (5,00 %) & Art. 67 SchKG Betreibungsankündigung
* `test_austria_ugb`: Österreich § 456 UGB (9,2 %-Punkte) & § 1000 ABGB
* `test_cli_execution`: Prüfung aller CLI-Befehle (`calc`, `dunning`, `rates`)

---

## Rechtlicher Hinweis / Haftungsausschluss (RDG-Compliance)

> [!IMPORTANT]
> **Reine Zinsmathematik & kaufmännische Berechnungshilfe:**  
> Dieses Softwarepaket sowie die Dokumentation stellen **keine Rechtsberatung** im Sinne des deutschen Rechtsdienstleistungsgesetzes (§ 2 RDG), des österreichischen Rechtsanwaltsrechts oder des schweizerischen Rechts (Art. 404 OR) dar.  
> Sämtliche Vorlagen und Berechnungen sind unverbindliche Hilfsmittel für das kaufmännische Mahnwesen. Für Rechtsfragen im Einzelfall und gerichtliche Durchsetzungen konsultieren Sie bitte eine Rechtsanwältin oder einen Rechtsanwalt.

---

## Weiterführende Ressourcen

* 🌐 **Interaktiver Web-Rechner:** [https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/](https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/)
* 📚 **Ratgeber & Muster-Vorlagen:** [https://dach-digitalwerk.netlify.app/verzugszinsen-berechnen-rechner-b2b.html](https://dach-digitalwerk.netlify.app/verzugszinsen-berechnen-rechner-b2b.html)
* 🏢 **Herausgeber:** DACH Digitalwerk – Open Source Financial Tooling

---

## Lizenz

Dieses Projekt ist lizenziert unter der **MIT-Lizenz** – siehe die [LICENSE](LICENSE) Datei für Details.
