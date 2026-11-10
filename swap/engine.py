"""Swap cash-flow engine (spec §3). Owner: M1.

PLACEHOLDER from the kickoff skeleton — M1 replaces the bodies below.
"""
from swap.models import PeriodCashFlow, SwapInputs, SwapSummary


def simulate_swap(inputs: SwapInputs, floating_rates: list[float]) -> list[PeriodCashFlow]:
    """Return one cash flow per period using the spec §3 formulas.

    Raises ValueError if len(floating_rates) != inputs.num_periods. No rounding.
    """
    # TODO(M1): real formulas. Placeholder returns zero money per period.
    alpha = inputs.accrual_fraction
    return [
        PeriodCashFlow(
            period=i,
            time_years=i * alpha,
            floating_rate=rate,
            fixed_payment=0.0,
            floating_payment=0.0,
            net_settlement=0.0,
            cumulative_net=0.0,
        )
        for i, rate in enumerate(floating_rates, start=1)
    ]


def summarize(cash_flows: list[PeriodCashFlow]) -> SwapSummary:
    """Aggregate cash flows into totals. An empty list gives all zeros."""
    # TODO(M1): real totals. Placeholder returns zeros.
    return SwapSummary(
        total_fixed=0.0,
        total_floating=0.0,
        total_net=0.0,
        average_floating_rate=0.0,
        periods_receiving=0,
        periods_paying=0,
    )
