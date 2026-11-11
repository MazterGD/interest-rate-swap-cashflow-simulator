"""Swap cash-flow engine (spec §3). Owner: M1."""
from swap.models import PeriodCashFlow, SwapInputs, SwapSummary


def simulate_swap(inputs: SwapInputs, floating_rates: list[float]) -> list[PeriodCashFlow]:
    """Return one cash flow per period using the spec §3 formulas.

    Raises ValueError if len(floating_rates) != inputs.num_periods. No rounding.
    """
    if len(floating_rates) != inputs.num_periods:
        raise ValueError(
            f"Expected {inputs.num_periods} floating rates, got {len(floating_rates)}"
        )

    alpha = inputs.accrual_fraction
    fixed_payment = inputs.notional * inputs.fixed_rate * alpha
    cumulative_net = 0.0
    cash_flows = []

    for period, floating_rate in enumerate(floating_rates, start=1):
        floating_payment = inputs.notional * floating_rate * alpha
        net_settlement = floating_payment - fixed_payment
        if inputs.position.value == "receive_fixed":
            net_settlement = -net_settlement
        cumulative_net += net_settlement
        cash_flows.append(
            PeriodCashFlow(
                period=period,
                time_years=period * alpha,
                floating_rate=floating_rate,
                fixed_payment=fixed_payment,
                floating_payment=floating_payment,
                net_settlement=net_settlement,
                cumulative_net=cumulative_net,
            )
        )

    return cash_flows


def summarize(cash_flows: list[PeriodCashFlow]) -> SwapSummary:
    """Aggregate cash flows into totals. An empty list gives all zeros."""
    if not cash_flows:
        return SwapSummary(0.0, 0.0, 0.0, 0.0, 0, 0)

    return SwapSummary(
        total_fixed=sum(flow.fixed_payment for flow in cash_flows),
        total_floating=sum(flow.floating_payment for flow in cash_flows),
        total_net=sum(flow.net_settlement for flow in cash_flows),
        average_floating_rate=sum(flow.floating_rate for flow in cash_flows)
        / len(cash_flows),
        periods_receiving=sum(flow.net_settlement > 0 for flow in cash_flows),
        periods_paying=sum(flow.net_settlement < 0 for flow in cash_flows),
    )
