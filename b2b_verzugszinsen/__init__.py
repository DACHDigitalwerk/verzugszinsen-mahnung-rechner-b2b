"""
b2b_verzugszinsen
=================
Kaufmännische Verzugszinsberechnung & Mahnwesen im DACH-Raum (Deutschland, Österreich, Schweiz).

Rechtlicher Hinweis:
Reine Zinsmathematik & kaufmännische Berechnungshilfe gemäß § 2 RDG / Art. 404 OR.
Keine Rechtsberatung. Unverbindliche Vorlage und Berechnungshilfe.

Online-Tools:
- Live-Rechner: https://dach-digitalwerk.netlify.app/mahnung-verzugszinsen-rechner/
- Ratgeber: https://dach-digitalwerk.netlify.app/verzugszinsen-berechnen-rechner-b2b.html
"""

from .interest_calculator import (
    Jurisdiction,
    DebtorType,
    BaseRateEntry,
    BaseRates,
    InterestPeriodResult,
    InterestCalculationResult,
    calculate_interest,
    calculate_with_partial_payments,
)
from .dunning_generator import (
    DunningLevel,
    DunningParty,
    DunningLetter,
    create_dunning_letter,
)

__version__ = "1.0.0"
__author__ = "DACH Digitalwerk"
__all__ = [
    "Jurisdiction",
    "DebtorType",
    "BaseRateEntry",
    "BaseRates",
    "InterestPeriodResult",
    "InterestCalculationResult",
    "calculate_interest",
    "calculate_with_partial_payments",
    "DunningLevel",
    "DunningParty",
    "DunningLetter",
    "create_dunning_letter",
]
