"""Unit tests for swap/scenarios.py. Owner: M2."""

import pytest

from swap.models import RatePreset
from swap.scenarios import generate_rates


@pytest.mark.parametrize(
    ("preset", "expected"),
    [
        (RatePreset.FLAT, [0.04, 0.04, 0.04, 0.04]),
        (RatePreset.RISING, [0.04, 0.0425, 0.045, 0.0475]),
        (RatePreset.FALLING, [0.04, 0.0375, 0.035, 0.0325]),
    ],
)
def test_generate_rates_matches_preset_shape_and_values(preset: RatePreset, expected: list[float]) -> None:
    assert generate_rates(preset, 4, 0.04, step=0.0025, seed=42) == pytest.approx(expected)


def test_generate_rates_is_deterministic_for_volatile_preset() -> None:
    first = generate_rates(RatePreset.VOLATILE, 8, 0.03, step=0.0025, seed=42)
    second = generate_rates(RatePreset.VOLATILE, 8, 0.03, step=0.0025, seed=42)

    assert first == pytest.approx(second)
    assert len(first) == 8
    assert first[0] == pytest.approx(0.03)
    assert all(rate >= 0.0 for rate in first)


def test_generate_rates_never_goes_below_zero_for_falling_preset() -> None:
    rates = generate_rates(RatePreset.FALLING, 6, 0.005, step=0.01)

    assert len(rates) == 6
    assert all(rate >= 0.0 for rate in rates)
    assert rates == pytest.approx([0.005, 0.0, 0.0, 0.0, 0.0, 0.0])


def test_generate_rates_handles_single_period() -> None:
    for preset in RatePreset:
        result = generate_rates(preset, 1, 0.03)
        assert result == pytest.approx([0.03])
