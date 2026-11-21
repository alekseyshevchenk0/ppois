"""Money helpers shared by pricing, payroll and loyalty."""
from __future__ import annotations

from decimal import Decimal

PERCENT_BASE = Decimal(100)
CENT = Decimal("0.01")


def apply_percent(amount: Decimal, percent: Decimal) -> Decimal:
    """Raise (positive percent) or lower (negative percent) an amount, rounded to cents."""
    return (amount * (PERCENT_BASE + percent) / PERCENT_BASE).quantize(CENT)


def percent_of(amount: Decimal, percent: Decimal) -> Decimal:
    return (amount * percent / PERCENT_BASE).quantize(CENT)
