"""Floating-rate path generator (spec §7). Owner: M2.

PLACEHOLDER from the kickoff skeleton — M2 replaces the body below.
"""
from swap.models import RatePreset


def generate_rates(
    preset: RatePreset,
    num_periods: int,
    start_rate: float,
    step: float = 0.0025,
    seed: int = 42,
) -> list[float]:
    """Return num_periods decimal rates for the preset. Deterministic for the same arguments."""
    # TODO(M2): Flat / Rising / Falling / Volatile per spec §7. Placeholder is always flat.
    return [start_rate] * num_periods
