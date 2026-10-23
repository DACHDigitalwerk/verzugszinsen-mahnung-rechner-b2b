"""
Unit tests for dunning_generator.py covering:
6. SchKG Betreibungsmuster & Schweiz (Art. 104 OR / Art. 67 SchKG)
7. Mahnstufen 1 (Erinnerung), 2 (1. Mahnung), 3 (Letzte Mahnung)
8. CLI Tool Integration
"""

import datetime
import io
import unittest
from contextlib import redirect_stdout

from b2b_verzugszinsen.interest_calculator import (
    Jurisdiction,
    DebtorType,
    calculate_interest,
)
from b2b_verzugszinsen.dunning_generator import (
    DunningLevel,
    DunningParty,
    DunningLetter,
    create_dunning_letter,
)
from b2b_verzugszinsen.cli import main


class TestDunningGenerator(unittest.TestCase):
    """Test-Suite für Mahnschreiben-Generierung und SchKG Betreibungsmuster."""

    def test_schkg_betreibungsmuster(self):
        """
        6. Test SchKG Betreibungsmuster (Schweiz Art. 104 OR & Art. 67 SchKG):
        - Gesetzlicher Verzugszins von 5,00 % p.a.
        - Währung CHF
        - Keine 40-Euro-EU-Pauschale
        - Mahnstufe 3 erzeugt ausdrückliche Betreibungsankündigung gem. Art. 67 SchKG
        """
        calc_ch = calculate_interest(
            principal=12500.0,
            due_date=datetime.date(2024, 1, 1),
            calculation_date=datetime.date(2024, 3, 1),  # 60 Tage
            jurisdiction=Jurisdiction.CH,
            debtor_type=DebtorType.B2B,
        )

        self.assertEqual(calc_ch.effective_rate_percent, 5.0)
        self.assertEqual(calc_ch.flat_fee, 0.0)
        self.assertIn("Art. 104 Abs. 1 OR", calc_ch.statutory_basis)

        letter = create_dunning_letter(
            level=DunningLevel.FINAL_DUNNING,
            creditor_name="Alpen Tech AG",
            debtor_name="Zürich Handel GmbH",
            invoice_number="CH-2024-998",
            principal=12500.0,
            due_date=datetime.date(2024, 1, 1),
            letter_date=datetime.date(2024, 3, 1),
            jurisdiction=Jurisdiction.CH,
            deadline_days=5,
        )

        self.assertEqual(letter.currency, "CHF")
        text = letter.to_text()

        # Überprüfung SchKG-Rechtstexte
        self.assertIn("BETREIBUNGSANKÜNDIGUNG GEMÄSS ART. 67 SchKG", text)
        self.assertIn("Betreibungsbegehren beim zuständigen Betreibungsamt", text)
        self.assertIn("12,500.00 CHF", text)
        self.assertIn("Verzugszinsen (5.00 % p.a. taggenau)", text)
        self.assertIn("Hinweis gemäß § 2 RDG / Art. 404 OR", text)
        self.assertIn("https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/", text)

    def test_dunning_level_1_reminder(self):
        """Test Mahnstufe 1: Zahlungserinnerung ohne Verzugszinsdruck."""
        letter = create_dunning_letter(
            level=DunningLevel.PAYMENT_REMINDER,
            creditor_name="Digitalwerk GmbH",
            debtor_name="Kunde AG",
            invoice_number="RE-1001",
            principal=2000.0,
            due_date=datetime.date(2024, 2, 1),
            letter_date=datetime.date(2024, 2, 10),
            jurisdiction=Jurisdiction.DE,
        )
        text = letter.to_text()
        self.assertIn("Zahlungserinnerung zu Rechnung Nr. RE-1001", text)
        self.assertIn("vorübergehendes Versehen", text)
        # In Stufe 1 keine Schadenspauschale gefordert
        self.assertEqual(letter.calculation.flat_fee, 0.0)

    def test_dunning_level_2_first_dunning(self):
        """Test Mahnstufe 2: 1. Mahnung mit Zinsen und 40-€-Pauschale."""
        letter = create_dunning_letter(
            level=DunningLevel.FIRST_DUNNING,
            creditor_name="Digitalwerk GmbH",
            debtor_name="Kunde AG",
            invoice_number="RE-1002",
            principal=3500.0,
            due_date=datetime.date(2024, 1, 1),
            letter_date=datetime.date(2024, 2, 1),
            jurisdiction=Jurisdiction.DE,
            custom_base_rate=0.27,
        )
        text = letter.to_text()
        self.assertIn("1. Mahnung", text)
        self.assertIn("Gesetzliche Schadenspauschale (§ 288 Abs. 5 BGB): 40.00 EUR", text)
        self.assertIn("Verzugszinsen (9.27 % p.a. taggenau)", text)

    def test_cli_execution(self):
        """Test CLI Befehle (calc, rates, dunning)."""
        # Test rates
        out = io.StringIO()
        with redirect_stdout(out):
            ret = main(["rates"])
        self.assertEqual(ret, 0)
        output = out.getvalue()
        self.assertIn("§ 288 BGB", output)
        self.assertIn("§ 456, 458 UGB", output)
        self.assertIn("Art. 104 OR", output)

        # Test calc json
        out_calc = io.StringIO()
        with redirect_stdout(out_calc):
            ret_calc = main(["calc", "--amount", "1000", "--due", "2024-01-01", "--date", "2024-02-01", "--base-rate", "0.27", "--json"])
        self.assertEqual(ret_calc, 0)
        self.assertIn('"effective_rate_percent": 9.27', out_calc.getvalue())
        self.assertIn('"flat_fee": 40.0', out_calc.getvalue())


if __name__ == "__main__":
    unittest.main()
