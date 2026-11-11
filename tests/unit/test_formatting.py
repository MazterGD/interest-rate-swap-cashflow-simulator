"""M4 display contracts, including signs, zero and rounding."""
import pytest

from ui.formatting import fmt_money, fmt_rate, fmt_signed_money


@pytest.mark.parametrize("value, expected", [
    (1234567.8, "$1,234,568"), (2500.2, "$2,500"),
    (-2500, "−$2,500"), (0, "$0"), (-0.0, "$0"),
])
def test_money(value, expected):
    assert fmt_money(value) == expected


@pytest.mark.parametrize("value, expected", [
    (5000, "+$5,000"), (-2500, "−$2,500"),
    (0, "$0"), (-0.0, "$0"), (1234.8, "+$1,235"),
    (-1234.8, "−$1,235"),
])
def test_signed_money(value, expected):
    assert fmt_signed_money(value) == expected


@pytest.mark.parametrize("value, expected", [
    (0.0425, "4.25%"), (0, "0.00%"), (-0.015, "-1.50%"),
    (0.034567, "3.46%"),
])
def test_rate(value, expected):
    assert fmt_rate(value) == expected
