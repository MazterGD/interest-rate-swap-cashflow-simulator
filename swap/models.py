"""Shared data contracts. FROZEN — change only via the WORK_PLAN contract-change process."""
from dataclasses import dataclass
from enum import Enum


class Position(str, Enum):
    PAY_FIXED = "pay_fixed"          # payer swap: pay fixed, receive floating
    RECEIVE_FIXED = "receive_fixed"  # receiver swap: receive fixed, pay floating


class RatePreset(str, Enum):
    FLAT = "flat"
    RISING = "rising"
    FALLING = "falling"
    VOLATILE = "volatile"


@dataclass(frozen=True)
class SwapInputs:
    notional: float           # e.g. 1_000_000
    fixed_rate: float         # decimal, 0.04 == 4%
    tenor_years: int          # 1..30
    payments_per_year: int    # 1, 2 or 4
    position: Position

    @property
    def num_periods(self) -> int:
        return self.tenor_years * self.payments_per_year

    @property
    def accrual_fraction(self) -> float:
        return 1 / self.payments_per_year


@dataclass(frozen=True)
class PeriodCashFlow:
    period: int               # 1-based
    time_years: float         # period * accrual_fraction
    floating_rate: float      # decimal
    fixed_payment: float      # N * K * alpha
    floating_payment: float   # N * L * alpha
    net_settlement: float     # user's view: + receive, - pay
    cumulative_net: float


@dataclass(frozen=True)
class SwapSummary:
    total_fixed: float
    total_floating: float
    total_net: float          # user's view: + receive, - pay
    average_floating_rate: float
    periods_receiving: int    # net > 0
    periods_paying: int       # net < 0
