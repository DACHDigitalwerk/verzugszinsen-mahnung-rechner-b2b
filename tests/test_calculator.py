# -*- coding: utf-8 -*-
"""
Unit tests for DACH Verzugszinsen & Mahnspesen Calculation Engine.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from verzugszinsen_b2b.calculator import (
    calculate_interest,
    Jurisdiction,
    TransactionType,
    PeriodCalculation
)

class TestVerzugszinsenDE(unittest.TestCase):
    def test_de_b2b_standard(self):
        # 10.000 € Forderung, fällig am 01.01.2024, berechnet bis 30.06.2024
        # Verzugstage: 02.01.2024 bis 30.06.2024 = 181 Tage
        # Basiszinssatz H1 2024: 3.62 % -> B2B Zinssatz = 3.62 + 9 = 12.62 %
        res = calculate_interest(
            principal=10000.0,
            due_date="2024-01-01",
            calculation_date="2024-06-30",
            jurisdiction=Jurisdiction.DE,
            transaction_type=TransactionType.B2B
        )
        self.assertEqual(res.jurisdiction, Jurisdiction.DE)
        self.assertEqual(res.total_days, 181)
        self.assertEqual(res.statutory_fee, 40.0)
        self.assertGreater(res.total_interest, 600.0)
        self.assertEqual(res.total_claim, round(10000.0 + res.total_interest + 40.0, 2))

    def test_de_b2c_no_statutory_fee(self):
        # Verbrauchergeschäft: kein Anspruch auf 40 € Pauschale
        res = calculate_interest(
            principal=2000.0,
            due_date="2024-01-01",
            calculation_date="2024-06-30",
            jurisdiction=Jurisdiction.DE,
            transaction_type=TransactionType.B2C
        )
        self.assertEqual(res.statutory_fee, 0.0)
        self.assertEqual(res.periods[0].margin, 5.0)

    def test_de_rate_boundary_split(self):
        # Über Stichtag 01.07.2024 hinweg (Änderung Basiszinssatz von 3.62 % auf 3.37 %)
        res = calculate_interest(
            principal=5000.0,
            due_date="2024-06-15",
            calculation_date="2024-07-15",
            jurisdiction=Jurisdiction.DE,
            transaction_type=TransactionType.B2B
        )
        self.assertEqual(len(res.periods), 2)
        self.assertAlmostEqual(res.periods[0].total_rate, 12.62, places=2)
        self.assertAlmostEqual(res.periods[1].total_rate, 12.37, places=2)

class TestVerzugszinsenCH(unittest.TestCase):
    def test_ch_standard_5_percent(self):
        # 10.000 CHF Forderung für 365 Tage @ 5% p.a.
        res = calculate_interest(
            principal=10000.0,
            due_date="2024-12-31",
            calculation_date="2025-12-31",
            jurisdiction=Jurisdiction.CH,
            transaction_type=TransactionType.B2B
        )
        self.assertEqual(res.currency, "CHF")
        self.assertEqual(res.total_days, 365)
        self.assertEqual(res.total_interest, 500.0)
        self.assertEqual(res.statutory_fee, 0.0)

    def test_ch_custom_contract_rate(self):
        # Vertraglicher Zins 8% p.a.
        res = calculate_interest(
            principal=10000.0,
            due_date="2025-01-01",
            calculation_date="2025-07-02",
            jurisdiction=Jurisdiction.CH,
            contract_swiss_rate=8.0
        )
        self.assertEqual(res.periods[0].total_rate, 8.0)

class TestVerzugszinsenAT(unittest.TestCase):
    def test_at_b2b_surcharge_and_fee(self):
        # Österreich B2B: Basiszinssatz + 9.2 % + 40 € Pauschale (§ 458 UGB)
        res = calculate_interest(
            principal=4000.0,
            due_date="2024-01-01",
            calculation_date="2024-06-30",
            jurisdiction=Jurisdiction.AT,
            transaction_type=TransactionType.B2B
        )
        self.assertEqual(res.currency, "EUR")
        self.assertEqual(res.statutory_fee, 40.0)
        self.assertEqual(res.periods[0].margin, 9.2)

    def test_at_b2c_fixed_4_percent(self):
        # Österreich B2C (§ 1000 ABGB fix 4%)
        res = calculate_interest(
            principal=1000.0,
            due_date="2024-12-31",
            calculation_date="2025-12-31",
            jurisdiction=Jurisdiction.AT,
            transaction_type=TransactionType.B2C
        )
        self.assertEqual(res.total_interest, 40.0)
        self.assertEqual(res.statutory_fee, 0.0)

class TestEdgeCases(unittest.TestCase):
    def test_not_yet_due(self):
        # Rechnung erst morgen fällig
        res = calculate_interest(
            principal=1000.0,
            due_date="2026-12-31",
            calculation_date="2026-10-01",
            jurisdiction=Jurisdiction.DE
        )
        self.assertEqual(res.total_days, 0)
        self.assertEqual(res.total_interest, 0.0)
        self.assertEqual(res.total_claim, 1000.0)

    def test_custom_reminder_fees(self):
        res = calculate_interest(
            principal=500.0,
            due_date="2025-01-01",
            calculation_date="2025-02-01",
            jurisdiction=Jurisdiction.DE,
            custom_reminder_fees=12.50
        )
        self.assertEqual(res.custom_reminder_fees, 12.50)
        self.assertIn(12.50, [res.custom_reminder_fees])

    def test_leap_year_day_count(self):
        # Schaltjahr 2024: 29. Februar
        res = calculate_interest(
            principal=10000.0,
            due_date="2024-02-01",
            calculation_date="2024-03-01",
            jurisdiction=Jurisdiction.DE,
            day_count_convention="act/act"
        )
        self.assertEqual(res.total_days, 29) # 2. Feb bis 1. März = 29 Tage
        self.assertEqual(res.periods[0].year_days, 366)

    def test_negative_principal_raises(self):
        with self.assertRaises(ValueError):
            calculate_interest(principal=-100.0, due_date="2025-01-01")

    def test_invalid_date_raises(self):
        with self.assertRaises(ValueError):
            calculate_interest(principal=100.0, due_date="ungueltig")

if __name__ == "__main__":
    unittest.main()
