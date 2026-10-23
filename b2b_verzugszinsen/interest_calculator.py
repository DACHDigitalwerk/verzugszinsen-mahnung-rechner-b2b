"""
b2b_verzugszinsen.interest_calculator
====================================
Taggenaue kaufmännische Verzugszinsberechnung für den DACH-Raum (Deutschland, Österreich, Schweiz).

Rechtlicher Hintergrund:
- Deutschland:
  * § 288 Abs. 2 BGB: Verzugszinssatz für Rechtsgeschäfte ohne Verbraucherbeteiligung (B2B)
    beträgt 9 Prozentpunkte über dem Basiszinssatz.
  * § 288 Abs. 1 BGB: Verzugszinssatz für Rechtsgeschäfte mit Verbraucherbeteiligung (B2C)
    beträgt 5 Prozentpunkte über dem Basiszinssatz.
  * § 288 Abs. 5 BGB: Gesetzliche 40-Euro-Schadenspauschale für B2B-Entgeltforderungen.
  * § 289 Satz 1 BGB: Zinseszins-Verbot ("Von Zinsen dürfen Verzugszinsen nicht entrichtet werden").
  * § 247 BGB: Basiszinssatz der Deutschen Bundesbank (Halbjährliche Anpassung zum 01.01. und 01.07.).
- Österreich:
  * § 456 UGB: 9,2 Prozentpunkte über dem Basiszinssatz für unternehmerische Geschäfte (B2B).
  * § 458 UGB: 40-Euro-Betreibungskostenpauschale für unternehmerische Geschäfte.
  * § 1000 Abs. 1 ABGB: Gesetzlicher Verzugszins für Verbraucher (B2C) beträgt 4,00 % p.a.
- Schweiz:
  * Art. 104 Abs. 1 OR: Gesetzlicher Verzugszins von 5,00 % p.a.
  * Art. 67 ff. SchKG: Betreibungsverfahren beim zuständigen Betreibungsamt.

HINWEIS GEMÄSS § 2 RDG / ART. 404 OR:
Reine mathematische und kaufmännische Berechnungshilfe. Keine Rechtsberatung!
Online-Live-Rechner: https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/
Ratgeber: https://dach-digitalwerk.netlify.app/verzugszinsen-berechnen-rechner-b2b.html
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import List, Optional, Tuple, Union


class Jurisdiction(str, Enum):
    """Länderkennung für DACH-Verzugszinsen."""
    DE = "DE"  # Deutschland (§ 288 BGB)
    AT = "AT"  # Österreich (§ 456 UGB / § 1000 ABGB)
    CH = "CH"  # Schweiz (Art. 104 OR)


class DebtorType(str, Enum):
    """Schuldnertyp."""
    B2B = "B2B"  # Unternehmer / Gewerblich / Juristische Person
    B2C = "B2C"  # Verbraucher / Privatperson


@dataclass(frozen=True)
class BaseRateEntry:
    """Repräsentiert einen Basiszinssatz für einen Gültigkeitszeitraum."""
    valid_from: datetime.date
    valid_to: datetime.date
    rate_percent: float  # z.B. 0.27, 3.37, 3.62

    def contains(self, check_date: datetime.date) -> bool:
        return self.valid_from <= check_date <= self.valid_to


class BaseRates:
    """
    Verwaltung historischer und aktueller Basiszinssätze der Deutschen Bundesbank
    und der Oesterreichischen Nationalbank (OeNB).
    """

    # Referenztabelle der Deutschen Bundesbank (§ 247 BGB)
    # Stichtage jeweils 1. Januar und 1. Juli
    HISTORIC_BUNDESBANK_RATES: List[BaseRateEntry] = [
        BaseRateEntry(datetime.date(2025, 1, 1), datetime.date(2025, 6, 30), 3.02),
        BaseRateEntry(datetime.date(2024, 7, 1), datetime.date(2024, 12, 31), 3.37),
        BaseRateEntry(datetime.date(2024, 1, 1), datetime.date(2024, 6, 30), 3.62),
        BaseRateEntry(datetime.date(2023, 7, 1), datetime.date(2023, 12, 31), 3.12),
        BaseRateEntry(datetime.date(2023, 1, 1), datetime.date(2023, 6, 30), 1.62),
        BaseRateEntry(datetime.date(2022, 7, 1), datetime.date(2022, 12, 31), -0.88),
        BaseRateEntry(datetime.date(2022, 1, 1), datetime.date(2022, 6, 30), -0.88),
        BaseRateEntry(datetime.date(2021, 1, 1), datetime.date(2021, 12, 31), -0.88),
        # Spezieller Referenz-Basiszinssatz 0.27% (ergibt 9.27% B2B Verzugszins gem. BGB § 288 Abs. 2)
        BaseRateEntry(datetime.date(2013, 7, 1), datetime.date(2013, 12, 31), 0.38),
        BaseRateEntry(datetime.date(2013, 1, 1), datetime.date(2013, 6, 30), -0.13),
    ]

    # Aktueller kaufmännischer Standard-Referenzzinssatz für Demonstrations- & Berechnungszwecke
    # Bei 0,27 % Basiszinssatz -> B2B = 9,27 % (§ 288 Abs. 2 BGB)
    DEFAULT_REFERENCE_BASE_RATE: float = 0.27

    @classmethod
    def get_bundesbank_rate(cls, target_date: datetime.date) -> float:
        """
        Ermittelt den Basiszinssatz der Deutschen Bundesbank für ein gegebenes Datum.
        Falls Datum außerhalb der hinterlegten Tabelle liegt, wird der jüngste bzw.
        Standard-Referenzzinssatz herangezogen.
        """
        for entry in cls.HISTORIC_BUNDESBANK_RATES:
            if entry.contains(target_date):
                return entry.rate_percent

        # Falls vor ältester Tabelle: 0.27 % Referenz
        # Falls in der Zukunft oder nicht explizit tabelliert: neuester hinterlegter Eintrag
        if target_date > cls.HISTORIC_BUNDESBANK_RATES[0].valid_to:
            return cls.HISTORIC_BUNDESBANK_RATES[0].rate_percent
        return cls.DEFAULT_REFERENCE_BASE_RATE


@dataclass
class InterestPeriodResult:
    """Zinsberechnung für ein Teil-Intervall."""
    start_date: datetime.date
    end_date: datetime.date
    days: int
    base_rate_percent: float
    surcharge_percent: float
    effective_rate_percent: float
    interest_amount: float


@dataclass
class InterestCalculationResult:
    """Vollständiges Ergebnis einer Verzugszinsberechnung."""
    principal: float  # Hauptforderung
    due_date: datetime.date  # Fälligkeitsdatum
    calculation_date: datetime.date  # Zinsberechnungsstichtag
    days_overdue: int  # Verzugstage (Verzug beginnt gem. § 187 Abs. 1 BGB am Folgetag)
    jurisdiction: Jurisdiction
    debtor_type: DebtorType
    base_rate_percent: float  # Basiszinssatz in %
    surcharge_percent: float  # Gesetzlicher Aufschlag in Prozentpunkten
    effective_rate_percent: float  # Gesamtzinssatz p.a. in %
    accrued_interest: float  # Aufgelaufene Verzugszinsen (EUR / CHF)
    flat_fee: float  # Gesetzliche Schadenspauschale (40 € B2B in DE/AT, 0 in CH)
    total_due: float  # Gesamtforderung = Hauptforderung + Zinsen + Pauschale
    periods: List[InterestPeriodResult] = field(default_factory=list)
    compound_interest_prevented: bool = True  # § 289 BGB Zinseszins-Ausschluss gewahrt
    statutory_basis: str = ""

    def summary_text(self) -> str:
        """Kompakter deutscher Zusammenfassungstext."""
        curr = "CHF" if self.jurisdiction == Jurisdiction.CH else "EUR"
        lines = [
            f"--- Verzugszinsberechnung ({self.jurisdiction.value} | {self.debtor_type.value}) ---",
            f"Hauptforderung:         {self.principal:,.2f} {curr}",
            f"Fälligkeitsdatum:       {self.due_date.strftime('%d.%m.%Y')}",
            f"Berechnungsstichtag:    {self.calculation_date.strftime('%d.%m.%Y')}",
            f"Verzugstage:            {self.days_overdue} Tage",
            f"Basiszinssatz:          {self.base_rate_percent:.2f} % p.a.",
            f"Gesetzlicher Aufschlag: {self.surcharge_percent:.2f} %-Punkte",
            f"Verzugszinssatz gesamt: {self.effective_rate_percent:.2f} % p.a.",
            f"Verzugszinsen:          {self.accrued_interest:,.2f} {curr}",
            f"Schadenspauschale:      {self.flat_fee:,.2f} {curr}",
            f"----------------------------------------",
            f"GESAMTFORDRUNG:         {self.total_due:,.2f} {curr}",
            f"Rechtsgrundlage:        {self.statutory_basis}",
            f"Zinseszins-Ausschluss:  Eingehalten (§ 289 BGB / Art. 104 OR)",
        ]
        return "\n".join(lines)


def _round_currency(value: Union[float, Decimal]) -> float:
    """Kaufmännische Rundung auf 2 Nachkommastellen (ROUND_HALF_UP)."""
    d = Decimal(str(value)) if isinstance(value, float) else value
    return float(d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def calculate_interest(
    principal: float,
    due_date: Union[datetime.date, str],
    calculation_date: Optional[Union[datetime.date, str]] = None,
    jurisdiction: Union[Jurisdiction, str] = Jurisdiction.DE,
    debtor_type: Union[DebtorType, str] = DebtorType.B2B,
    custom_base_rate: Optional[float] = None,
    custom_surcharge: Optional[float] = None,
    include_flat_fee: bool = True,
    day_count_convention: str = "act/365",
) -> InterestCalculationResult:
    """
    Berechnet taggenaue Verzugszinsen und Pauschalen nach dem jeweiligen Landesrecht (DE, AT, CH).

    :param principal: Hauptforderungsbetrag in EUR (bzw. CHF für CH)
    :param due_date: Fälligkeitsdatum der Rechnung (Date oder 'YYYY-MM-DD')
    :param calculation_date: Berechnungsstichtag (Standard: heute)
    :param jurisdiction: DE, AT oder CH
    :param debtor_type: B2B (Unternehmer) oder B2C (Verbraucher)
    :param custom_base_rate: Manuell vorgegebener Basiszinssatz in % (optional)
    :param custom_surcharge: Manuell vorgegebener Zinsaufschlag in %-Punkten (optional)
    :param include_flat_fee: Ob die 40-€-Pauschale (§ 288 Abs. 5 BGB / § 458 UGB) anfällt
    :param day_count_convention: 'act/365' (Standard B2B), 'act/360' oder 'act/act'
    :return: InterestCalculationResult
    """
    # Parse dates
    if isinstance(due_date, str):
        due_date = datetime.date.fromisoformat(due_date)

    if calculation_date is None:
        calculation_date = datetime.date.today()
    elif isinstance(calculation_date, str):
        calculation_date = datetime.date.fromisoformat(calculation_date)

    # Convert Enums
    if isinstance(jurisdiction, str):
        jurisdiction = Jurisdiction(jurisdiction.upper())
    if isinstance(debtor_type, str):
        debtor_type = DebtorType(debtor_type.upper())

    if calculation_date <= due_date:
        # Kein Verzug eingetreten
        days_overdue = 0
    else:
        # Gemäß § 187 Abs. 1 BGB beginnt der Verzug am Tag nach dem Fälligkeitstag
        # z.B. Fällig am 01.01., Zinsen ab 02.01. bis einschließlich 10.01. = 9 Tage
        days_overdue = (calculation_date - due_date).days

    # Ermittlung des Zinssatzes und der Pauschale nach Jurisdiktion
    flat_fee = 0.0

    if jurisdiction == Jurisdiction.DE:
        # Deutschland
        if debtor_type == DebtorType.B2B:
            # § 288 Abs. 2 BGB: 9 Prozentpunkte über Basiszinssatz
            default_surcharge = 9.0
            statutory_basis = "§ 288 Abs. 2 BGB (B2B: 9 Prozentpunkte über Basiszinssatz) & § 288 Abs. 5 BGB (40 € Pauschale)"
            if include_flat_fee and days_overdue > 0:
                flat_fee = 40.0
        else:
            # § 288 Abs. 1 BGB: 5 Prozentpunkte über Basiszinssatz für Verbraucher
            default_surcharge = 5.0
            statutory_basis = "§ 288 Abs. 1 BGB (B2C: 5 Prozentpunkte über Basiszinssatz)"
            flat_fee = 0.0

        if custom_base_rate is not None:
            base_rate = float(custom_base_rate)
        else:
            base_rate = BaseRates.get_bundesbank_rate(due_date)

        surcharge = custom_surcharge if custom_surcharge is not None else default_surcharge
        effective_rate = base_rate + surcharge

    elif jurisdiction == Jurisdiction.AT:
        # Österreich
        if debtor_type == DebtorType.B2B:
            # § 456 UGB: 9,2 Prozentpunkte über Basiszinssatz
            default_surcharge = 9.2
            statutory_basis = "§ 456 UGB (B2B: 9,2 Prozentpunkte über Basiszinssatz) & § 458 UGB (40 € Pauschale)"
            if include_flat_fee and days_overdue > 0:
                flat_fee = 40.0
            if custom_base_rate is not None:
                base_rate = float(custom_base_rate)
            else:
                base_rate = BaseRates.get_bundesbank_rate(due_date)  # EZB/OeNB Leitzinskorridor
            surcharge = custom_surcharge if custom_surcharge is not None else default_surcharge
            effective_rate = base_rate + surcharge
        else:
            # § 1000 Abs. 1 ABGB: Gesetzlicher Zinssatz 4,00 % fix
            base_rate = 0.0
            surcharge = 4.0 if custom_surcharge is None else custom_surcharge
            effective_rate = surcharge
            statutory_basis = "§ 1000 Abs. 1 ABGB (B2C: 4,00 % p.a. gesetzlicher Verzugszins)"
            flat_fee = 0.0

    elif jurisdiction == Jurisdiction.CH:
        # Schweiz: Art. 104 Abs. 1 OR
        base_rate = 0.0
        surcharge = 5.0 if custom_surcharge is None else custom_surcharge
        effective_rate = surcharge
        statutory_basis = "Art. 104 Abs. 1 OR (5,00 % gesetzlicher Verzugszins) & SchKG"
        flat_fee = 0.0  # Schweiz kennt keine gesetzliche 40-€-Pauschale nach EU-Recht

    else:
        raise ValueError(f"Unbekannte Jurisdiktion: {jurisdiction}")

    # Taggenaue Berechnung
    # divisor: 365 oder 366 bei Schaltjahr (act/act) oder 360
    if days_overdue <= 0:
        accrued_interest = 0.0
        periods = []
    else:
        if day_count_convention == "act/360":
            days_in_year = 360.0
        elif day_count_convention == "act/act":
            # Bestimme, ob Schaltjahr
            days_in_year = 366.0 if (calculation_date.year % 4 == 0 and (calculation_date.year % 100 != 0 or calculation_date.year % 400 == 0)) else 365.0
        else:
            # act/365 Standard in kaufmännischer B2B-Praxis
            days_in_year = 365.0

        raw_interest = principal * (effective_rate / 100.0) * (days_overdue / days_in_year)
        accrued_interest = _round_currency(raw_interest)

        periods = [
            InterestPeriodResult(
                start_date=due_date + datetime.timedelta(days=1),
                end_date=calculation_date,
                days=days_overdue,
                base_rate_percent=base_rate,
                surcharge_percent=surcharge,
                effective_rate_percent=effective_rate,
                interest_amount=accrued_interest,
            )
        ]

    total_due = _round_currency(principal + accrued_interest + flat_fee)

    return InterestCalculationResult(
        principal=_round_currency(principal),
        due_date=due_date,
        calculation_date=calculation_date,
        days_overdue=days_overdue,
        jurisdiction=jurisdiction,
        debtor_type=debtor_type,
        base_rate_percent=round(base_rate, 4),
        surcharge_percent=round(surcharge, 4),
        effective_rate_percent=round(effective_rate, 4),
        accrued_interest=accrued_interest,
        flat_fee=_round_currency(flat_fee),
        total_due=total_due,
        periods=periods,
        compound_interest_prevented=True,  # § 289 BGB gewahrt
        statutory_basis=statutory_basis,
    )


def calculate_with_partial_payments(
    principal: float,
    due_date: Union[datetime.date, str],
    payments: List[Tuple[Union[datetime.date, str], float]],
    calculation_date: Optional[Union[datetime.date, str]] = None,
    jurisdiction: Union[Jurisdiction, str] = Jurisdiction.DE,
    debtor_type: Union[DebtorType, str] = DebtorType.B2B,
    custom_base_rate: Optional[float] = None,
    include_flat_fee: bool = True,
) -> dict:
    """
    Berechnet Verzugszinsen unter Berücksichtigung von Teilzahlungen.
    Verrechnung gemäß § 367 Abs. 1 BGB:
    Zunächst auf Kosten (Pauschale), dann auf Zinsen, zuletzt auf Hauptforderung.
    
    STRENGER ZINSESZINS-AUSSCHLUSS GEMÄSS § 289 BGB:
    Zinsen fallen IMMER NUR auf die verbleibende Hauptforderung an, NIEMALS auf Zinsen!
    """
    if isinstance(due_date, str):
        due_date = datetime.date.fromisoformat(due_date)
    if calculation_date is None:
        calculation_date = datetime.date.today()
    elif isinstance(calculation_date, str):
        calculation_date = datetime.date.fromisoformat(calculation_date)

    # Sort payments by date
    parsed_payments: List[Tuple[datetime.date, float]] = []
    for p_date, p_amount in payments:
        d = datetime.date.fromisoformat(p_date) if isinstance(p_date, str) else p_date
        parsed_payments.append((d, float(p_amount)))
    parsed_payments.sort(key=lambda x: x[0])

    # Initial state
    current_principal = float(principal)
    current_date = due_date
    accumulated_interest = 0.0
    
    # 40 € fee arises once on default for B2B in DE/AT
    is_b2b = (debtor_type == DebtorType.B2B or str(debtor_type).upper() == "B2B")
    current_costs = 40.0 if (is_b2b and include_flat_fee and jurisdiction in (Jurisdiction.DE, "DE", Jurisdiction.AT, "AT")) else 0.0

    timeline = []

    for p_date, p_amount in parsed_payments:
        if p_date <= current_date:
            # Payment received before/on due date directly reduces principal
            current_principal = max(0.0, current_principal - p_amount)
            continue
        if p_date > calculation_date:
            break

        # Calculate interest for interval strictly on principal (NO COMPOUNDING!)
        interval_days = (p_date - current_date).days
        sub_res = calculate_interest(
            principal=current_principal,
            due_date=current_date,
            calculation_date=p_date,
            jurisdiction=jurisdiction,
            debtor_type=debtor_type,
            custom_base_rate=custom_base_rate,
            include_flat_fee=False,
        )
        accumulated_interest += sub_res.accrued_interest

        # Allocate payment per § 367 BGB: 1. Costs -> 2. Interest -> 3. Principal
        rem_payment = p_amount
        cost_paid = min(current_costs, rem_payment)
        current_costs -= cost_paid
        rem_payment -= cost_paid

        interest_paid = min(accumulated_interest, rem_payment)
        accumulated_interest -= interest_paid
        rem_payment -= interest_paid

        principal_paid = min(current_principal, rem_payment)
        current_principal -= principal_paid

        timeline.append({
            "date": p_date.isoformat(),
            "payment": p_amount,
            "cost_paid": _round_currency(cost_paid),
            "interest_paid": _round_currency(interest_paid),
            "principal_paid": _round_currency(principal_paid),
            "remaining_principal": _round_currency(current_principal),
            "remaining_interest": _round_currency(accumulated_interest),
            "remaining_costs": _round_currency(current_costs),
        })
        current_date = p_date

    # Final interval up to calculation_date
    if calculation_date > current_date and current_principal > 0:
        sub_res = calculate_interest(
            principal=current_principal,
            due_date=current_date,
            calculation_date=calculation_date,
            jurisdiction=jurisdiction,
            debtor_type=debtor_type,
            custom_base_rate=custom_base_rate,
            include_flat_fee=False,
        )
        accumulated_interest += sub_res.accrued_interest

    final_total = _round_currency(current_principal + accumulated_interest + current_costs)

    return {
        "initial_principal": _round_currency(principal),
        "remaining_principal": _round_currency(current_principal),
        "accrued_interest": _round_currency(accumulated_interest),
        "remaining_costs": _round_currency(current_costs),
        "total_due": final_total,
        "compound_interest_prevented": True,
        "timeline": timeline,
    }
