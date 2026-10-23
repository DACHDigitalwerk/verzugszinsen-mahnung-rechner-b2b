# -*- coding: utf-8 -*-
"""
Command-line interface (CLI) for DACH Verzugszinsen- & Mahnspesen-Berechnung.
"""

import argparse
import json
import sys
from datetime import date
from .calculator import (
    calculate_interest,
    Jurisdiction,
    TransactionType
)

def main():
    parser = argparse.ArgumentParser(
        prog="dach-verzugszinsen",
        description="DACH B2B/B2C Gesetzlicher Verzugszinsen- & Mahnspesen-Rechner (§ 288 BGB, Art. 104 OR, § 456 UGB)"
    )

    parser.add_argument("principal", type=float, help="Hauptforderung / Rechnungsbetrag (z.B. 2500.00)")
    parser.add_argument("due_date", type=str, help="Faelligkeitsdatum der Rechnung (Format: YYYY-MM-DD oder DD.MM.YYYY)")
    parser.add_argument("--calc-date", "-c", type=str, default=None, help="Berechnungsstichtag (Standard: heute)")
    parser.add_argument("--country", "-j", choices=["DE", "CH", "AT"], default="DE", help="Rechtsordnung: DE, CH oder AT (Standard: DE)")
    parser.add_argument("--type", "-t", choices=["B2B", "B2C"], default="B2B", help="Geschaeftsart: B2B oder B2C (Standard: B2B)")
    parser.add_argument("--fees", "-f", type=float, default=0.0, help="Eigene Mahngebuehren / Mahnspesen (z.B. 5.00)")
    parser.add_argument("--no-statutory-fee", action="store_true", help="40 € B2B-Verzugspauschale ausschliessen")
    parser.add_argument("--json", action="store_true", help="Ausgabe als maschinenlesbares JSON")

    args = parser.parse_args()

    try:
        res = calculate_interest(
            principal=args.principal,
            due_date=args.due_date,
            calculation_date=args.calc_date,
            jurisdiction=Jurisdiction(args.country),
            transaction_type=TransactionType(args.type),
            custom_reminder_fees=args.fees,
            include_statutory_b2b_fee=not args.no_statutory_fee
        )
    except Exception as e:
        print(f"Fehler bei der Berechnung: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        out = {
            "principal": res.principal,
            "currency": res.currency,
            "jurisdiction": res.jurisdiction.value,
            "transaction_type": res.transaction_type.value,
            "due_date": res.due_date.isoformat(),
            "calculation_date": res.calculation_date.isoformat(),
            "total_days": res.total_days,
            "total_interest": res.total_interest,
            "statutory_fee": res.statutory_fee,
            "custom_reminder_fees": res.custom_reminder_fees,
            "total_claim": res.total_claim,
            "legal_basis": res.legal_basis,
            "periods": [
                {
                    "start": p.start_date.isoformat(),
                    "end": p.end_date.isoformat(),
                    "days": p.days,
                    "base_rate": p.base_rate,
                    "margin": p.margin,
                    "total_rate": p.total_rate,
                    "interest": round(p.interest_amount, 2)
                } for p in res.periods
            ]
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    print("=" * 65)
    print(f"⚖️  DACH VERZUGSZINSEN- & MAHNSPESEN-BERECHNUNG ({res.jurisdiction.value} - {res.transaction_type.value})")
    print("=" * 65)
    print(f"Hauptforderung        : {res.principal:10.2f} {res.currency}")
    print(f"Faelligkeitsdatum     : {res.due_date.strftime('%d.%m.%Y')}")
    print(f"Berechnungsstichtag   : {res.calculation_date.strftime('%d.%m.%Y')} ({res.total_days} Verzugstage)")
    print(f"Rechtsgrundlage       : {res.legal_basis}")
    print("-" * 65)
    print("ZEITRAUM-AUFSCHLUESSELUNG:")
    for p in res.periods:
        print(f"  • {p.start_date.strftime('%d.%m.%Y')} bis {p.end_date.strftime('%d.%m.%Y')} ({p.days:3d} Tage) @ {p.total_rate:5.2f}% = {p.interest_amount:7.2f} {res.currency}")
    print("-" * 65)
    print(f"Gesetzliche Verzugszinsen: {res.total_interest:10.2f} {res.currency}")
    if res.statutory_fee > 0:
        print(f"Gesetzliche B2B-Pauschale: {res.statutory_fee:10.2f} {res.currency}")
    if res.custom_reminder_fees > 0:
        print(f"Mahngebuehren / Spesen   : {res.custom_reminder_fees:10.2f} {res.currency}")
    print("=" * 65)
    print(f"GESAMTFORDERUNG          : {res.total_claim:10.2f} {res.currency}")
    print("=" * 65)

if __name__ == "__main__":
    main()
