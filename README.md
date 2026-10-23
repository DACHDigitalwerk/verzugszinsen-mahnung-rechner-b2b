# ⚖️ DACH B2B & B2C Verzugszinsen-, Mahnspesen- & Forderungsrechner (2026)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Tests: 12 Passing](https://img.shields.io/badge/Tests-12%20Passed-brightgreen.svg)](tests/)
[![Deutschland: § 288 BGB](https://img.shields.io/badge/Deutschland-%C2%A7_288_BGB_(Basis_+_9_%25)-indigo.svg)](https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/)
[![Schweiz: Art. 104 OR](https://img.shields.io/badge/Schweiz-Art._104_OR_(5_%25_p.a.)-red.svg)](https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/)
[![Österreich: § 456 UGB](https://img.shields.io/badge/%C3%96sterreich-%C2%A7_456_UGB_(Basis_+_9.2_%25)-emerald.svg)](https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/)

> 💸 **Open-Source Berechnungs-Engine, CLI-Utility & kaufmännische Referenz für gesetzliche Verzugszinsen und Mahnspesen in Deutschland, der Schweiz und Österreich.**  
> Unterstützt taggenaue Zinsberechnung über historische Basiszinssatz-Stichtage der Deutschen Bundesbank und der Oesterreichischen Nationalbank, die 40-€-B2B-Verzugspauschale (§ 288 Abs. 5 BGB / § 458 UGB) und den Schweizer Verzugszins nach Art. 104 OR.

---

### 🌐 Interaktive Live-Tools & Ratgeber im Web

* 🧮 **Web-Rechner & Mahnschreiben-Generator:**  
  👉 **[https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/](https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/)**  
  *Berechnen Sie Verzugszinsen und Pauschalen direkt online im Browser, schalten Sie zwischen 3 Mahnstufen um und erzeugen Sie druckfertige DIN-A4 Mahnschreiben als PDF ohne Abo.*

* 📚 **Ratgeber: B2B Verzugszinsen richtig berechnen:**  
  👉 **[https://dach-digitalwerk.netlify.app/verzugszinsen-berechnen-rechner-b2b.html](https://dach-digitalwerk.netlify.app/verzugszinsen-berechnen-rechner-b2b.html)**

* 📝 **Muster & Vorlage: 3-stufiges Mahnverfahren rechtssicher aufbauen:**  
  👉 **[https://dach-digitalwerk.netlify.app/mahnung-schreiben-vorlage-3-stufen.html](https://dach-digitalwerk.netlify.app/mahnung-schreiben-vorlage-3-stufen.html)**

* 🇨🇭 **Leitfaden: Schweizer Zahlungsbefehl & Betreibungsverfahren (SchKG):**  
  👉 **[https://dach-digitalwerk.netlify.app/zahlungsbefehl-betreibung-schweiz-ablauf.html](https://dach-digitalwerk.netlify.app/zahlungsbefehl-betreibung-schweiz-ablauf.html)**

---

## 🏛️ Gesetzliche Zinsmodelle im Überblick

| Land | Geschäftsart | Gesetzliche Grundlage | Zinssatz (Stand 2026) | Gesetzliche Pauschale |
|---|---|---|---|---|
| **Deutschland (DE)** | **B2B** (Handelsgeschäft) | § 288 Abs. 2 BGB | Basiszinssatz + **9,00 Prozentpunkte** | **40,00 EUR** (§ 288 Abs. 5 BGB) |
| **Deutschland (DE)** | **B2C** (Verbraucher) | § 288 Abs. 1 BGB | Basiszinssatz + **5,00 Prozentpunkte** | *Keine gesetzliche Pauschale* |
| **Schweiz (CH)** | **B2B & B2C** | Art. 104 Abs. 1 OR | **5,00 % p.a. fix** (sofern vertraglich nicht höher) | *Verzugsschaden Art. 106 OR* |
| **Österreich (AT)** | **B2B** (Unternehmer) | § 456 UGB | Basiszinssatz + **9,20 Prozentpunkte** | **40,00 EUR** (§ 458 UGB) |
| **Österreich (AT)** | **B2C** (Verbraucher) | § 1000 Abs. 1 ABGB | **4,00 % p.a. fix** | *Keine gesetzliche Pauschale* |

---

## 🚀 Installation & Schnellstart

### 1. Installation

```bash
git clone https://github.com/DACHDigitalwerk/verzugszinsen-mahnung-rechner-b2b.git
cd verzugszinsen-mahnung-rechner-b2b
pip install -e .
```

### 2. CLI-Nutzung (`dach-verzugszinsen`)

#### Beispiel A: Deutsches B2B-Handelsgeschäft (15.000 € Forderung)
```bash
dach-verzugszinsen 15000 2024-01-15 --country DE --type B2B
```

**Ausgabe:**
```text
=================================================================
⚖️  DACH VERZUGSZINSEN- & MAHNSPESEN-BERECHNUNG (DE - B2B)
=================================================================
Hauptforderung        :   15000.00 EUR
Faelligkeitsdatum     : 15.01.2024
Berechnungsstichtag   : 23.10.2026 (1012 Verzugstage)
Rechtsgrundlage       : § 288 Abs. 2 BGB (Basis + 9 %) + § 288 Abs. 5 BGB (40 € Verzugspauschale)
-----------------------------------------------------------------
ZEITRAUM-AUFSCHLUESSELUNG:
  • 16.01.2024 bis 30.06.2024 (167 Tage) @ 12.62% =  865.51 EUR
  • 01.07.2024 bis 31.12.2024 (184 Tage) @ 12.37% =  936.53 EUR
  • 01.01.2025 bis 30.06.2025 (181 Tage) @ 12.12% =  901.87 EUR
  ...
-----------------------------------------------------------------
Gesetzliche Verzugszinsen:    5054.12 EUR
Gesetzliche B2B-Pauschale:      40.00 EUR
=================================================================
GESAMTFORDERUNG          :   20094.12 EUR
=================================================================
```

#### Beispiel B: Schweizer Handwerkerforderung (8.500 CHF nach Art. 104 OR)
```bash
dach-verzugszinsen 8500 2025-06-01 --country CH --calc-date 2026-06-01
```

#### Beispiel C: JSON-Export für ERP- & Faktura-Integration
```bash
dach-verzugszinsen 4200 2025-01-01 --json
```

---

## 🐍 Python-API Verwendung

```python
from verzugszinsen_b2b import calculate_interest, Jurisdiction, TransactionType

# Taggenaue Berechnung
result = calculate_interest(
    principal=12500.00,
    due_date="2025-03-01",
    calculation_date="2026-03-01",
    jurisdiction=Jurisdiction.DE,
    transaction_type=TransactionType.B2B,
    custom_reminder_fees=10.00 # eigene Mahnspesen
)

print(f"Zinsen: {result.total_interest} {result.currency}")
print(f"40-Euro-Pauschale: {result.statutory_fee} {result.currency}")
print(f"Gesamtforderung: {result.total_claim} {result.currency}")

# Aufschlüsselung der Halbjahresperioden
for p in result.periods:
    print(f"{p.start_date} - {p.end_date}: {p.days} Tage @ {p.total_rate}% = {p.interest_amount} EUR")
```

---

## 🧪 Unit-Tests ausführen

```bash
python -m unittest discover -s tests
```
Alle 12 Testfälle (inkl. Schaltjahre, Zinsgrenzen und B2B-Pauschalen) laufen standardmäßig ohne externe Abhängigkeiten durch.

---

## 📄 Lizenz

Dieses Repository steht unter der [MIT License](LICENSE).  
Entwickelt von **DACH Digitalwerk** für transparente und faire Forderungsabwicklung im DACH-Raum.
