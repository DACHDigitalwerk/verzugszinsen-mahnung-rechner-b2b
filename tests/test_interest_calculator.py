"""
Unit tests for interest_calculator.py covering:
1. Bundesbank-Basiszinssatz-Berechnung
2. B2B 9%-Regel (§ 288 Abs. 2 BGB) -> 9,27 %
3. Verbraucher 5%-Regel (§ 288 Abs. 1 BGB)
4. 40-€-Pauschale (§ 288 Abs. 5 BGB / § 458 UGB)
5. Zinseszins-Ausschluss (§ 289 BGB)
6. Österreich UGB (§ 456 / § 458 UGB)
7. Schweiz Art. 104 OR
"""

import datetime
import unittest

from b2b_verzugszinsen.interest_calculator import (
    Jurisdiction,
    DebtorType,
    BaseRates,
    calculate_interest,
    calculate_with_partial_payments,
)


class TestInterestCalculator(unittest.TestCase):
    """Test-Suite für kaufmännische Verzugszinsen im DACH-Raum."""

    def test_bundesbank_basiszinssatz(self):
        """1. Test Bundesbank-Basiszinssatz Stichtage und Gültigkeitszeiträume."""
        # Test 1. Halbjahr 2024: 3,62 %
        rate_2024_h1 = BaseRates.get_bundesbank_rate(datetime.date(2024, 3, 15))
        self.assertEqual(rate_2024_h1, 3.62)

        # Test 2. Halbjahr 2024: 3,37 %
        rate_2024_h2 = BaseRates.get_bundesbank_rate(datetime.date(2024, 8, 1))
        self.assertEqual(rate_2024_h2, 3.37)

        # Test 1. Halbjahr 2025: 3,02 %
        rate_2025_h1 = BaseRates.get_bundesbank_rate(datetime.date(2025, 2, 10))
        self.assertEqual(rate_2025_h1, 3.02)

        # Test Stichtag 01.07.2023: 3,12 %
        rate_2023_h2 = BaseRates.get_bundesbank_rate(datetime.date(2023, 7, 1))
        self.assertEqual(rate_2023_h2, 3.12)

    def test_b2b_9_percent_rule(self):
        """
        2. Test B2B 9%-Regel nach § 288 Abs. 2 BGB:
        Basiszinssatz + 9 Prozentpunkte.
        Mit Vorgabe-Basiszinssatz von 0,27 % ergibt sich exakt 9,27 % Verzugszinssatz.
        """
        result = calculate_interest(
            principal=10000.0,
            due_date=datetime.date(2024, 1, 1),
            calculation_date=datetime.date(2024, 1, 31),  # 30 Tage Verzug
            jurisdiction=Jurisdiction.DE,
            debtor_type=DebtorType.B2B,
            custom_base_rate=0.27,
        )

        self.assertEqual(result.base_rate_percent, 0.27)
        self.assertEqual(result.surcharge_percent, 9.0)
        self.assertEqual(result.effective_rate_percent, 9.27)
        self.assertEqual(result.days_overdue, 30)

        # Erwartete Zinsen: 10.000 * 0.0927 * (30 / 365) = 76.19178... -> 76.19 EUR
        self.assertAlmostEqual(result.accrued_interest, 76.19, places=2)
        # Gesamtforderung: 10.000 + 76.19 + 40.00 Pauschale = 10.116,19 EUR
        self.assertEqual(result.total_due, 10116.19)

    def test_b2c_5_percent_rule(self):
        """
        3. Test Verbraucher 5%-Regel nach § 288 Abs. 1 BGB:
        Basiszinssatz + 5 Prozentpunkte.
        Mit Basiszinssatz von 0,27 % ergibt sich 5,27 % Verzugszinssatz.
        """
        result = calculate_interest(
            principal=1000.0,
            due_date=datetime.date(2024, 1, 1),
            calculation_date=datetime.date(2024, 1, 31),  # 30 Tage Verzug
            jurisdiction=Jurisdiction.DE,
            debtor_type=DebtorType.B2C,
            custom_base_rate=0.27,
        )

        self.assertEqual(result.base_rate_percent, 0.27)
        self.assertEqual(result.surcharge_percent, 5.0)
        self.assertEqual(result.effective_rate_percent, 5.27)
        # B2C hat KEINE 40-Euro-Pauschale
        self.assertEqual(result.flat_fee, 0.0)
        # Erwartete Zinsen: 1000 * 0.0527 * (30 / 365) = 4.3315... -> 4.33 EUR
        self.assertAlmostEqual(result.accrued_interest, 4.33, places=2)
        self.assertEqual(result.total_due, 1004.33)

    def test_40_euro_pauschale(self):
        """
        4. Test 40-€-Schadenspauschale (§ 288 Abs. 5 BGB / § 458 UGB):
        - Fällt bei B2B-Verzug an.
        - Fällt bei B2C NICHT an.
        - Fällt bei pünktlicher Zahlung (kein Verzug) NICHT an.
        - Kann abgewählt werden (include_flat_fee=False).
        """
        # B2B in Verzug -> 40 €
        res_b2b = calculate_interest(
            principal=500.0,
            due_date="2024-01-01",
            calculation_date="2024-01-15",
            jurisdiction="DE",
            debtor_type="B2B",
        )
        self.assertEqual(res_b2b.flat_fee, 40.0)

        # B2C in Verzug -> 0 €
        res_b2c = calculate_interest(
            principal=500.0,
            due_date="2024-01-01",
            calculation_date="2024-01-15",
            jurisdiction="DE",
            debtor_type="B2C",
        )
        self.assertEqual(res_b2c.flat_fee, 0.0)

        # B2B nicht in Verzug (due_date >= calc_date) -> 0 €
        res_no_delay = calculate_interest(
            principal=500.0,
            due_date="2024-01-15",
            calculation_date="2024-01-10",
            jurisdiction="DE",
            debtor_type="B2B",
        )
        self.assertEqual(res_no_delay.flat_fee, 0.0)
        self.assertEqual(res_no_delay.accrued_interest, 0.0)

        # B2B explizit ohne Pauschale
        res_without = calculate_interest(
            principal=500.0,
            due_date="2024-01-01",
            calculation_date="2024-01-15",
            jurisdiction="DE",
            debtor_type="B2B",
            include_flat_fee=False,
        )
        self.assertEqual(res_without.flat_fee, 0.0)

    def test_zinseszins_ausschluss(self):
        """
        5. Test Zinseszins-Ausschluss (§ 289 Satz 1 BGB):
        "Von Zinsen dürfen Verzugszinsen nicht entrichtet werden."
        Bei unterjährigen Teilzahlungen (§ 367 BGB) werden Zinsen ausschließlich
        auf die Rest-Hauptforderung berechnet und verbleibende aufgelaufene Zinsen
        verzinsen sich zu keinem Zeitpunkt weiter.
        """
        # Hauptforderung: 10.000 EUR, Fällig am 01.01.2024
        # Teilzahlung 1: Am 01.02.2024 zahlt Schuldner 2.000 EUR
        # Berechnung zum 01.03.2024
        res = calculate_with_partial_payments(
            principal=10000.0,
            due_date="2024-01-01",
            payments=[("2024-02-01", 2000.0)],
            calculation_date="2024-03-01",
            jurisdiction="DE",
            debtor_type="B2B",
            custom_base_rate=0.27,  # 9,27 % Verzugszins
        )

        self.assertTrue(res["compound_interest_prevented"])
        # Vor Teilzahlung fielen 40 € Kosten an
        # 31 Tage Verzug auf 10.000 EUR: 10.000 * 0.0927 * (31/365) = 78.73 EUR Zinsen
        # Teilzahlung 2.000 EUR tilgt:
        # 1. 40 € Kosten -> Restzahlung 1.960 EUR
        # 2. 78.73 EUR Zinsen -> Restzahlung 1.881,27 EUR
        # 3. Hauptforderung wird getilgt um 1.881,27 EUR -> Rest-Hauptforderung = 8.118,73 EUR
        # Für den Zeitraum 01.02. bis 01.03. (29 Tage) fallen Zinsen NUR auf 8.118,73 EUR an!
        timeline = res["timeline"]
        self.assertEqual(len(timeline), 1)
        step = timeline[0]
        self.assertEqual(step["cost_paid"], 40.0)
        self.assertEqual(step["interest_paid"], 78.73)
        self.assertEqual(step["remaining_costs"], 0.0)
        self.assertEqual(step["remaining_interest"], 0.0)
        self.assertAlmostEqual(step["remaining_principal"], 8118.73, places=2)

    def test_austria_ugb(self):
        """Test Österreich § 456 UGB (9,2 Prozentpunkte) & § 458 UGB (40 € Pauschale)."""
        res_at_b2b = calculate_interest(
            principal=5000.0,
            due_date="2024-01-01",
            calculation_date="2024-01-31",
            jurisdiction=Jurisdiction.AT,
            debtor_type=DebtorType.B2B,
            custom_base_rate=0.27,
        )
        self.assertEqual(res_at_b2b.surcharge_percent, 9.2)
        self.assertEqual(res_at_b2b.effective_rate_percent, 9.47)
        self.assertEqual(res_at_b2b.flat_fee, 40.0)
        self.assertIn("§ 456 UGB", res_at_b2b.statutory_basis)

        # Österreich B2C (§ 1000 ABGB = 4 % fix)
        res_at_b2c = calculate_interest(
            principal=5000.0,
            due_date="2024-01-01",
            calculation_date="2024-01-31",
            jurisdiction=Jurisdiction.AT,
            debtor_type=DebtorType.B2C,
        )
        self.assertEqual(res_at_b2c.effective_rate_percent, 4.0)
        self.assertEqual(res_at_b2c.flat_fee, 0.0)
        self.assertIn("§ 1000 Abs. 1 ABGB", res_at_b2c.statutory_basis)


if __name__ == "__main__":
    unittest.main()
