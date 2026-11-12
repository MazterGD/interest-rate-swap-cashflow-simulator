import io

import pandas as pd
import pytest

from swap.engine import simulate_swap, summarize
from swap.export import cash_flows_to_dataframe, to_csv_bytes
from swap.models import Position, RatePreset, SwapInputs
from swap.scenarios import generate_rates
from swap.validation import validate_inputs, validate_rates

pytestmark = pytest.mark.integration


def test_pipeline_worked_example() -> None:
    inputs = SwapInputs(1_000_000, 0.04, 2, 2, Position.PAY_FIXED)
    rates = [0.035, 0.04, 0.045, 0.05]

    assert validate_inputs(inputs) == []
    assert validate_rates(rates, inputs.num_periods) == []
    cash_flows = simulate_swap(inputs, rates)
    summary = summarize(cash_flows)
    csv = to_csv_bytes(cash_flows_to_dataframe(cash_flows))
    exported = pd.read_csv(io.BytesIO(csv))

    assert summary.total_net == pytest.approx(5_000)
    assert exported["Cumulative net"].iloc[-1] == pytest.approx(5_000)


def test_pipeline_position_flip_negates_total() -> None:
    rates = [0.035, 0.04, 0.045, 0.05]
    pay_inputs = SwapInputs(1_000_000, 0.04, 2, 2, Position.PAY_FIXED)
    receive_inputs = SwapInputs(1_000_000, 0.04, 2, 2, Position.RECEIVE_FIXED)

    pay_summary = summarize(simulate_swap(pay_inputs, rates))
    receive_summary = summarize(simulate_swap(receive_inputs, rates))

    assert receive_summary.total_net == pytest.approx(-pay_summary.total_net)


@pytest.mark.parametrize("preset", list(RatePreset))
@pytest.mark.parametrize("payments_per_year", [1, 2, 4])
def test_pipeline_totals_are_consistent(
    preset: RatePreset, payments_per_year: int
) -> None:
    inputs = SwapInputs(1_000_000, 0.04, 2, payments_per_year, Position.PAY_FIXED)
    rates = generate_rates(preset, inputs.num_periods, 0.035)
    cash_flows = simulate_swap(inputs, rates)
    summary = summarize(cash_flows)

    assert sum(flow.net_settlement for flow in cash_flows) == pytest.approx(
        summary.total_net
    )
    assert cash_flows[-1].cumulative_net == pytest.approx(summary.total_net)


def test_pipeline_rejects_invalid_rates_before_engine() -> None:
    inputs = SwapInputs(1_000_000, 0.04, 1, 2, Position.PAY_FIXED)
    rates = [0.04, 0.40]

    errors = validate_rates(rates, inputs.num_periods)

    assert errors
    assert "Period 2" in errors[0]

def test_pipeline_assignment_brief_sample() -> None:
    """Brief table: Q1..Q4 nets +37,500 / +25,000 / -25,000 / -12,500 for the fixed receiver."""
    inputs = SwapInputs(10_000_000, 0.08, 1, 4, Position.RECEIVE_FIXED)
    rates = [0.065, 0.07, 0.09, 0.085]

    assert validate_inputs(inputs) == [] and validate_rates(rates, 4) == []
    cash_flows = simulate_swap(inputs, rates)
    exported = pd.read_csv(io.BytesIO(to_csv_bytes(cash_flows_to_dataframe(cash_flows))))

    assert [f.fixed_payment for f in cash_flows] == pytest.approx([200_000] * 4)
    assert [f.floating_payment for f in cash_flows] == pytest.approx(
        [162_500, 175_000, 225_000, 212_500]
    )
    assert list(exported["Net settlement"]) == pytest.approx([37_500, 25_000, -25_000, -12_500])
    assert summarize(cash_flows).total_net == pytest.approx(25_000)
