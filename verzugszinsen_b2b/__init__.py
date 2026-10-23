"""
DACH B2B & B2C Verzugszinsen-, Mahnspesen- & Verzugspauschalen-Engine (2026)
DE (§ 288 BGB), CH (Art. 104 OR) & AT (§ 456 UGB / § 1000 ABGB).
"""

__version__ = "1.0.0"
__author__ = "DACH Digitalwerk"
__license__ = "MIT"

from .calculator import (
    calculate_interest,
    InterestCalculationResult,
    Jurisdiction,
    TransactionType,
    BASE_RATES_DE,
    BASE_RATES_AT,
    SWISS_DEFAULT_RATE
)

__all__ = [
    "calculate_interest",
    "InterestCalculationResult",
    "Jurisdiction",
    "TransactionType",
    "BASE_RATES_DE",
    "BASE_RATES_AT",
    "SWISS_DEFAULT_RATE"
]
