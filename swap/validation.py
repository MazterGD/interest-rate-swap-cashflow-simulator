"""Input validation (spec §8). Owner: M3.

PLACEHOLDER from the kickoff skeleton — M3 replaces the bodies below.
"""
from swap.models import SwapInputs


def validate_inputs(inputs: SwapInputs) -> list[str]:
    """Return human-readable error messages. An empty list means valid."""
    # TODO(M3): check the spec §8 limits. Placeholder accepts everything.
    return []


def validate_rates(rates: list[float], expected_len: int) -> list[str]:
    """Check length and per-period range (-5% to 30%). Messages name the period."""
    # TODO(M3): check length and range. Placeholder accepts everything.
    return []
