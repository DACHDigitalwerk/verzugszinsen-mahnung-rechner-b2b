# -*- coding: utf-8 -*-
"""
Core calculation engine for DACH statutory default interest and late payment fees.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import List, Optional, Tuple, Dict
import calendar

class Jurisdiction(str, Enum):
    DE = "DE" # Deutschland (§ 288 BGB)
    CH = "CH" # Schweiz (Art. 104 OR)
    AT = "AT" # Österreich (§ 456 UGB / § 1000 ABGB)

class TransactionType(str, Enum):
    B2B = "B2B" # Handelsgeschäfte zwischen Unternehmern
    B2C = "B2C" # Verbraucherbeteiligung

# Deutsche Bundesbank Basiszinssätze (§ 247 BGB)
# Format: (Gültig ab, Basiszinssatz in Prozent)
BASE_RATES_DE: List[Tuple[date, float]] = [
    (date(2022, 1, 1), -0.88),
    (date(2022, 7, 1), -0.88),
    (date(2023, 1, 1), 1.62),
    (date(2023, 7, 1), 3.12),
    (date(2024, 1, 1), 3.62),
    (date(2024, 7, 1), 3.37),
    (date(2025, 1, 1), 3.12),
    (date(2025, 7, 1), 2.87),
    (date(2026, 1, 1), 2.62),
    (date(2026, 7, 1), 2.62),
]

# Oesterreichische Nationalbank Basiszinssätze (OeNB / § 456 UGB)
BASE_RATES_AT: List[Tuple[date, float]] = [
    (date(2022, 1, 1), -0.62),
    (date(2022, 7, 1), -0.62),
    (date(2023, 1, 1), 1.88),
    (date(2023, 7, 1), 3.38),
    (date(2024, 1, 1), 3.88),
    (date(2024, 7, 1), 3.63),
    (date(2025, 1, 1), 3.38),
    (date(2025, 7, 1), 3.13),
    (date(2026, 1, 1), 2.88),
    (date(2026, 7, 1), 2.88),
]

SWISS_DEFAULT_RATE = 5.0 # Art. 104 Abs. 1 OR: 5% p.a.
GERMAN_B2B_SURCHARGE = 9.0 # § 288 Abs. 2 BGB: Basiszinssatz + 9 %-Punkte
GERMAN_B2C_SURCHARGE = 5.0 # § 288 Abs. 1 BGB: Basiszinssatz + 5 %-Punkte
AUSTRIAN_B2B_SURCHARGE = 9.2 # § 456 UGB: Basiszinssatz + 9.2 %-Punkte
AUSTRIAN_B2C_RATE = 4.0 # § 1000 Abs. 1 ABGB: 4 % p.a.

B2B_FEE_DE = 40.0 # § 288 Abs. 5 BGB: 40 € Verzugspauschale
B2B_FEE_AT = 40.0 # § 458 UGB: 40 € Pauschale

@dataclass
class PeriodCalculation:
    start_date: date
    end_date: date
    days: int
    base_rate: float
    margin: float
    total_rate: float
    interest_amount: float
    year_days: int

@dataclass
class InterestCalculationResult:
    principal: float
    currency: str
    jurisdiction: Jurisdiction
    transaction_type: TransactionType
    due_date: date
    calculation_date: date
    total_days: int
    periods: List[PeriodCalculation]
    total_interest: float
    statutory_fee: float
    custom_reminder_fees: float
    total_claim: float
    legal_basis: str

def parse_date(d) -> date:
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    if isinstance(d, str):
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(d, fmt).date()
            except ValueError:
                pass
        raise ValueError(f"Ungueltiges Datumsformat: {d}. Erwartet YYYY-MM-DD oder DD.MM.YYYY")
    raise TypeError(f"Nicht unterstuetzter Datumstyp: {type(d)}")

def get_base_rate(rates_table: List[Tuple[date, float]], target_date: date) -> float:
    applicable_rate = rates_table[0][1]
    for rate_date, rate in rates_table:
        if rate_date <= target_date:
            applicable_rate = rate
        else:
            break
    return applicable_rate

def calculate_interest(
    principal: float,
    due_date,
    calculation_date=None,
    jurisdiction: Jurisdiction = Jurisdiction.DE,
    transaction_type: TransactionType = TransactionType.B2B,
    custom_reminder_fees: float = 0.0,
    include_statutory_b2b_fee: bool = True,
    contract_swiss_rate: Optional[float] = None,
    day_count_convention: str = "act/365" # "act/365", "act/act", "act/360"
) -> InterestCalculationResult:
    """
    Berechnet taggenau die gesetzlichen Verzugszinsen und Mahnspesen nach deutschem,
    schweizerischem oder oesterreichischem Recht.
    """
    if principal <= 0:
        raise ValueError("Hauptforderung (principal) muss groesser als 0 sein.")

    start = parse_date(due_date)
    # Verzugszinsen beginnen gemaess BGB/OR/UGB am Tag NACH Eintritt der Faelligkeit
    interest_start = start + timedelta(days=1)
    
    end = parse_date(calculation_date) if calculation_date else date.today()

    if end < interest_start:
        total_days = 0
        periods = []
        fee = 0.0
        return InterestCalculationResult(
            principal=round(principal, 2),
            currency="CHF" if jurisdiction == Jurisdiction.CH else "EUR",
            jurisdiction=jurisdiction,
            transaction_type=transaction_type,
            due_date=start,
            calculation_date=end,
            total_days=0,
            periods=[],
            total_interest=0.0,
            statutory_fee=0.0,
            custom_reminder_fees=round(custom_reminder_fees, 2),
            total_claim=round(principal + custom_reminder_fees, 2),
            legal_basis="Kein Verzug (Rechnung noch nicht oder erst heute faellig)"
        )

    periods: List[PeriodCalculation] = []
    current_cur = interest_start

    # Schweizer Recht (OR Art. 104)
    if jurisdiction == Jurisdiction.CH:
        rate = contract_swiss_rate if contract_swiss_rate is not None else SWISS_DEFAULT_RATE
        currency = "CHF"
        legal_basis = f"Art. 104 Abs. 1 OR ({rate:.2f} % p.a. gesetzlicher Verzugszins)"
        statutory_fee = 0.0 # CH kennt keine automatische 40-CHF-Pauschale
        
        while current_cur <= end:
            year = current_cur.year
            is_leap = calendar.isleap(year)
            year_days = 366 if (day_count_convention == "act/act" and is_leap) else (360 if day_count_convention == "act/360" else 365)
            
            # Segment bis Jahresende oder Berechnungsende
            period_end = min(date(year, 12, 31), end)
            days = (period_end - current_cur).days + 1
            interest_part = principal * (rate / 100.0) * (days / year_days)
            
            periods.append(PeriodCalculation(
                start_date=current_cur,
                end_date=period_end,
                days=days,
                base_rate=rate,
                margin=0.0,
                total_rate=rate,
                interest_amount=round(interest_part, 4),
                year_days=year_days
            ))
            current_cur = period_end + timedelta(days=1)

    # Deutsches Recht (§ 288 BGB)
    elif jurisdiction == Jurisdiction.DE:
        currency = "EUR"
        margin = GERMAN_B2B_SURCHARGE if transaction_type == TransactionType.B2B else GERMAN_B2C_SURCHARGE
        statutory_fee = (B2B_FEE_DE if (transaction_type == TransactionType.B2B and include_statutory_b2b_fee) else 0.0)
        legal_ref = "§ 288 Abs. 2 BGB (Basis + 9 %)" if transaction_type == TransactionType.B2B else "§ 288 Abs. 1 BGB (Basis + 5 %)"
        if statutory_fee > 0:
            legal_ref += " + § 288 Abs. 5 BGB (40 € Verzugspauschale)"
        legal_basis = legal_ref

        # Wir teilen die Periode nach Zinsaenderungsstichtagen (1.1. und 1.7.)
        while current_cur <= end:
            base_r = get_base_rate(BASE_RATES_DE, current_cur)
            tot_r = base_r + margin
            
            # Naechster Stichtag
            if current_cur.month <= 6:
                next_boundary = date(current_cur.year, 6, 30)
            else:
                next_boundary = date(current_cur.year, 12, 31)
            
            period_end = min(next_boundary, end)
            days = (period_end - current_cur).days + 1
            
            year_days = 366 if (day_count_convention == "act/act" and calendar.isleap(current_cur.year)) else (360 if day_count_convention == "act/360" else 365)
            interest_part = principal * (tot_r / 100.0) * (days / year_days)

            periods.append(PeriodCalculation(
                start_date=current_cur,
                end_date=period_end,
                days=days,
                base_rate=base_r,
                margin=margin,
                total_rate=round(tot_r, 4),
                interest_amount=round(interest_part, 4),
                year_days=year_days
            ))
            current_cur = period_end + timedelta(days=1)

    # Oesterreichisches Recht (§ 456 UGB / § 1000 ABGB)
    elif jurisdiction == Jurisdiction.AT:
        currency = "EUR"
        if transaction_type == TransactionType.B2B:
            margin = AUSTRIAN_B2B_SURCHARGE
            statutory_fee = (B2B_FEE_AT if include_statutory_b2b_fee else 0.0)
            legal_basis = f"§ 456 UGB (Basis + 9.2 %) + § 458 UGB ({statutory_fee:.0f} € Pauschale)"
            
            while current_cur <= end:
                base_r = get_base_rate(BASE_RATES_AT, current_cur)
                tot_r = base_r + margin
                if current_cur.month <= 6:
                    next_boundary = date(current_cur.year, 6, 30)
                else:
                    next_boundary = date(current_cur.year, 12, 31)
                
                period_end = min(next_boundary, end)
                days = (period_end - current_cur).days + 1
                year_days = 366 if (day_count_convention == "act/act" and calendar.isleap(current_cur.year)) else (360 if day_count_convention == "act/360" else 365)
                interest_part = principal * (tot_r / 100.0) * (days / year_days)

                periods.append(PeriodCalculation(
                    start_date=current_cur,
                    end_date=period_end,
                    days=days,
                    base_rate=base_r,
                    margin=margin,
                    total_rate=round(tot_r, 4),
                    interest_amount=round(interest_part, 4),
                    year_days=year_days
                ))
                current_cur = period_end + timedelta(days=1)
        else:
            # B2C Oesterreich fix 4 % (§ 1000 Abs. 1 ABGB)
            margin = 0.0
            statutory_fee = 0.0
            legal_basis = "§ 1000 Abs. 1 ABGB (4.00 % p.a. fixer gesetzlicher Verzugszins)"
            days = (end - current_cur).days + 1
            year_days = 365
            tot_r = AUSTRIAN_B2C_RATE
            interest_part = principal * (tot_r / 100.0) * (days / year_days)
            periods.append(PeriodCalculation(
                start_date=current_cur,
                end_date=end,
                days=days,
                base_rate=tot_r,
                margin=0.0,
                total_rate=tot_r,
                interest_amount=round(interest_part, 4),
                year_days=year_days
            ))

    total_interest = sum(p.interest_amount for p in periods)
    total_days = sum(p.days for p in periods)
    total_claim = principal + total_interest + statutory_fee + custom_reminder_fees

    return InterestCalculationResult(
        principal=round(principal, 2),
        currency=currency,
        jurisdiction=jurisdiction,
        transaction_type=transaction_type,
        due_date=start,
        calculation_date=end,
        total_days=total_days,
        periods=periods,
        total_interest=round(total_interest, 2),
        statutory_fee=round(statutory_fee, 2),
        custom_reminder_fees=round(custom_reminder_fees, 2),
        total_claim=round(total_claim, 2),
        legal_basis=legal_basis
    )
