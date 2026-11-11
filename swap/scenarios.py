"""Floating-rate path generator (spec §7). Owner: M2."""
import random

from swap.models import RatePreset


def generate_rates(
    preset: RatePreset,
    num_periods: int,
    start_rate: float,
    step: float = 0.0025,
    seed: int = 42,
) -> list[float]:
    """Return num_periods decimal rates for the preset. Deterministic for the same arguments."""
    if num_periods <= 0:
        return []

    def clamp(value: float) -> float:
        return round(max(0.0, value), 6)

    if preset == RatePreset.FLAT:
        return [clamp(start_rate) for _ in range(num_periods)]
    if preset == RatePreset.RISING:
        return [clamp(start_rate + step * period_index) for period_index in range(num_periods)]
    if preset == RatePreset.FALLING:
        return [clamp(start_rate - step * period_index) for period_index in range(num_periods)]

    rng = random.Random(seed)
    values: list[float] = [clamp(start_rate)]
    current_rate = values[0]
    for _ in range(1, num_periods):
        current_rate = clamp(current_rate + rng.gauss(0.0, step))
        values.append(current_rate)
    return values
