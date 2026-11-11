"""Input validation (spec §8). Owner: M3. Rates are decimals."""
from swap.models import Position, SwapInputs


def validate_inputs(inputs: SwapInputs) -> list[str]:
    """Return human-readable error messages. An empty list means valid."""
    errors = []
    if not 1_000 <= inputs.notional <= 1_000_000_000_000:
        errors.append("Notional must be between 1,000 and 1,000,000,000,000.")
    if not 0 <= inputs.fixed_rate <= 0.30:
        errors.append("Fixed rate must be between 0% and 30%.")
    if type(inputs.tenor_years) is not int or not 1 <= inputs.tenor_years <= 30:
        errors.append("Tenor must be a whole number of years between 1 and 30.")
    if type(inputs.payments_per_year) is not int or inputs.payments_per_year not in (1, 2, 4):
        errors.append("Frequency must be annual, semi-annual or quarterly (1, 2 or 4 payments per year).")
    if not isinstance(inputs.position, Position):
        errors.append("Position must be Pay fixed or Receive fixed.")
    return errors


def validate_rates(rates: list[float], expected_len: int) -> list[str]:
    """Check length and per-period range (-5% to 30%). Messages name the period."""
    errors = []
    if len(rates) != expected_len:
        errors.append(f"Expected {expected_len} floating rates, but received {len(rates)}.")
    for period, rate in enumerate(rates, start=1):
        if not -0.05 <= rate <= 0.30:
            errors.append(f"Period {period} rate must be between −5% and 30%.")
    return errors
