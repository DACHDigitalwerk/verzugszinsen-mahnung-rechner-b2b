"""
b2b_verzugszinsen.cli
====================
CLI-Tool `b2b-zinsen`: Taggenaue kaufmännische Verzugszinsberechnung
und 3-stufige Mahnschreiben für den DACH-Raum.
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys

from .interest_calculator import (
    Jurisdiction,
    DebtorType,
    BaseRates,
    calculate_interest,
)
from .dunning_generator import (
    DunningLevel,
    create_dunning_letter,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="b2b-zinsen",
        description=(
            "Kaufmännische Verzugszinsberechnung & Mahnwesen im DACH-Raum (DE, AT, CH).\n"
            "Rechtlicher Hinweis: Reine Zinsmathematik gemäß § 2 RDG / Art. 404 OR."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", help="Verfügbare Befehle")

    # Command: calc
    calc_p = subparsers.add_parser("calc", help="Taggenaue Verzugszinsen berechnen")
    calc_p.add_argument("--amount", "-a", type=float, required=True, help="Hauptforderung in EUR / CHF")
    calc_p.add_argument("--due", "-d", type=str, required=True, help="Fälligkeitsdatum (YYYY-MM-DD)")
    calc_p.add_argument("--date", "-c", type=str, default=None, help="Berechnungsstichtag (Standard: heute)")
    calc_p.add_argument("--jurisdiction", "-j", choices=["DE", "AT", "CH"], default="DE", help="Land (Standard: DE)")
    group = calc_p.add_mutually_exclusive_group()
    group.add_argument("--b2b", action="store_true", default=True, help="B2B Geschäft (Standard)")
    group.add_argument("--b2c", action="store_true", help="Verbrauchergeschäft (B2C)")
    calc_p.add_argument("--base-rate", type=float, default=None, help="Manueller Basiszinssatz in %")
    calc_p.add_argument("--no-fee", action="store_true", help="40-Euro-Pauschale nicht anrechnen")
    calc_p.add_argument("--json", action="store_true", help="Ausgabe als JSON")

    # Command: dunning
    dunn_p = subparsers.add_parser("dunning", help="3-stufiges Mahnschreiben generieren")
    dunn_p.add_argument("--level", "-l", type=int, choices=[1, 2, 3], default=2, help="Mahnstufe: 1=Erinnerung, 2=1. Mahnung, 3=Letzte Mahnung / SchKG")
    dunn_p.add_argument("--amount", "-a", type=float, required=True, help="Hauptforderung")
    dunn_p.add_argument("--due", "-d", type=str, required=True, help="Fälligkeitsdatum (YYYY-MM-DD)")
    dunn_p.add_argument("--creditor", required=True, help="Name des Gläubigers")
    dunn_p.add_argument("--debtor", required=True, help="Name des Schuldners")
    dunn_p.add_argument("--invoice-nr", required=True, help="Rechnungsnummer")
    dunn_p.add_argument("--iban", default=None, help="IBAN des Gläubigers")
    dunn_p.add_argument("--jurisdiction", "-j", choices=["DE", "AT", "CH"], default="DE", help="Land (Standard: DE)")
    dunn_p.add_argument("--deadline-days", type=int, default=7, help="Zahlungsfrist in Tagen (Standard: 7)")
    dunn_p.add_argument("--base-rate", type=float, default=None, help="Manueller Basiszinssatz in %")

    # Command: rates
    rates_p = subparsers.add_parser("rates", help="Gesetzliche Verzugszinssätze & Bundesbank-Basiszinssätze anzeigen")

    return parser


def handle_calc(args: argparse.Namespace) -> int:
    debtor_type = DebtorType.B2C if args.b2c else DebtorType.B2B
    jurisdiction = Jurisdiction(args.jurisdiction)
    calc_date = args.date if args.date else datetime.date.today().isoformat()

    res = calculate_interest(
        principal=args.amount,
        due_date=args.due,
        calculation_date=calc_date,
        jurisdiction=jurisdiction,
        debtor_type=debtor_type,
        custom_base_rate=args.base_rate,
        include_flat_fee=(not args.no_fee),
    )

    if args.json:
        data = {
            "principal": res.principal,
            "due_date": res.due_date.isoformat(),
            "calculation_date": res.calculation_date.isoformat(),
            "days_overdue": res.days_overdue,
            "jurisdiction": res.jurisdiction.value,
            "debtor_type": res.debtor_type.value,
            "base_rate_percent": res.base_rate_percent,
            "surcharge_percent": res.surcharge_percent,
            "effective_rate_percent": res.effective_rate_percent,
            "accrued_interest": res.accrued_interest,
            "flat_fee": res.flat_fee,
            "total_due": res.total_due,
            "compound_interest_prevented": res.compound_interest_prevented,
            "statutory_basis": res.statutory_basis,
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(res.summary_text())
        print()
        print("Live-Rechner: https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/")
        print("Ratgeber: https://dach-digitalwerk.netlify.app/verzugszinsen-berechnen-rechner-b2b.html")
    return 0


def handle_dunning(args: argparse.Namespace) -> int:
    jurisdiction = Jurisdiction(args.jurisdiction)
    letter = create_dunning_letter(
        level=args.level,
        creditor_name=args.creditor,
        debtor_name=args.debtor,
        invoice_number=args.invoice_nr,
        principal=args.amount,
        due_date=args.due,
        jurisdiction=jurisdiction,
        creditor_iban=args.iban,
        deadline_days=args.deadline_days,
        custom_base_rate=args.base_rate,
    )
    print(letter.to_text())
    return 0


def handle_rates() -> int:
    print("=" * 75)
    print("GESETZLICHE VERZUGSZINSSÄTZE IM DACH-RAUM (DE, AT, CH)")
    print("=" * 75)
    print()
    print("1. DEUTSCHLAND (§ 288 BGB & § 247 BGB)")
    print("   - B2B (ohne Verbraucher): Basiszinssatz + 9,00 Prozentpunkte (§ 288 Abs. 2 BGB)")
    print("   - B2C (mit Verbraucher):  Basiszinssatz + 5,00 Prozentpunkte (§ 288 Abs. 1 BGB)")
    print("   - Schadenspauschale B2B:  40,00 Euro (§ 288 Abs. 5 BGB)")
    print("   - Zinseszins-Verbot:      Keine Zinsen auf Zinsen (§ 289 Satz 1 BGB)")
    print()
    print("   Historische & aktuelle Basiszinssätze der Deutschen Bundesbank:")
    for entry in BaseRates.HISTORIC_BUNDESBANK_RATES:
        b2b_rate = entry.rate_percent + 9.0
        b2c_rate = entry.rate_percent + 5.0
        print(f"     * {entry.valid_from.strftime('%d.%m.%Y')} - {entry.valid_to.strftime('%d.%m.%Y')}: "
              f"Basis: {entry.rate_percent:5.2f} %  |  B2B: {b2b_rate:5.2f} %  |  B2C: {b2c_rate:5.2f} %")
    print(f"     * Referenzbasis: {BaseRates.DEFAULT_REFERENCE_BASE_RATE:5.2f} %  |  B2B: {BaseRates.DEFAULT_REFERENCE_BASE_RATE + 9.0:5.2f} % (aktuell gem. Vorgabe)")
    print()
    print("2. ÖSTERREICH (§ 456, 458 UGB & § 1000 ABGB)")
    print("   - B2B (Unternehmer):      Basiszinssatz + 9,20 Prozentpunkte (§ 456 UGB)")
    print("   - B2B Pauschale:          40,00 Euro Betreibungskostenpauschale (§ 458 UGB)")
    print("   - B2C (Verbraucher):      4,00 % fix p.a. (§ 1000 Abs. 1 ABGB)")
    print()
    print("3. SCHWEIZ (Art. 104 OR & Art. 67 SchKG)")
    print("   - Gesetzlicher Zins:      5,00 % fix p.a. (Art. 104 Abs. 1 OR)")
    print("   - Betreibungsverfahren:   SchKG Betreibungsbegehren (Art. 67 SchKG)")
    print()
    print("Interaktiver Live-Rechner:")
    print("  -> https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/")
    print("Ratgeber & B2B-Leitfaden:")
    print("  -> https://dach-digitalwerk.netlify.app/verzugszinsen-berechnen-rechner-b2b.html")
    print("=" * 75)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "calc":
        return handle_calc(args)
    elif args.command == "dunning":
        return handle_dunning(args)
    elif args.command == "rates":
        return handle_rates()
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
