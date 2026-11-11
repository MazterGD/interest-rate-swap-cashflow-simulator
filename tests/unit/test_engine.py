import pytest

from swap.engine import simulate_swap, summarize
from swap.models import Position, SwapInputs


def worked_example_inputs(position: Position) -> SwapInputs:
    return SwapInputs(1_000_000, 0.04, 2, 2, position)


@pytest.mark.parametrize(
    ("position", "expected_net", "expected_cumulative", "expected_total"),
    [
        (
            Position.PAY_FIXED,
            [-2_500, 0, 2_500, 5_000],
            [-2_500, -2_500, 0, 5_000],
            5_000,
        ),
        (
            Position.RECEIVE_FIXED,
            [2_500, 0, -2_500, -5_000],
            [2_500, 2_500, 0, -5_000],
            -5_000,
        ),
    ],
)
def test_simulate_swap_worked_example(
    position: Position,
    expected_net: list[float],
    expected_cumulative: list[float],
    expected_total: float,
) -> None:
    cash_flows = simulate_swap(
        worked_example_inputs(position), [0.035, 0.04, 0.045, 0.05]
    )

    assert [flow.period for flow in cash_flows] == [1, 2, 3, 4]
    assert [flow.time_years for flow in cash_flows] == pytest.approx(
        [0.5, 1.0, 1.5, 2.0]
    )
    assert [flow.fixed_payment for flow in cash_flows] == pytest.approx(
        [20_000] * 4
    )
    assert [flow.floating_payment for flow in cash_flows] == pytest.approx(
        [17_500, 20_000, 22_500, 25_000]
    )
    assert [flow.net_settlement for flow in cash_flows] == pytest.approx(expected_net)
    assert [flow.cumulative_net for flow in cash_flows] == pytest.approx(
        expected_cumulative
    )
    assert summarize(cash_flows).total_net == pytest.approx(expected_total)


def test_simulate_swap_rejects_rate_length_mismatch() -> None:
    with pytest.raises(ValueError, match="Expected 4 floating rates, got 3"):
        simulate_swap(worked_example_inputs(Position.PAY_FIXED), [0.04, 0.04, 0.04])


def test_simulate_swap_supports_zero_and_negative_rates() -> None:
    inputs = SwapInputs(1_000, 0.01, 1, 4, Position.PAY_FIXED)

    cash_flows = simulate_swap(inputs, [0.0, -0.02, 0.01, 0.03])

    assert [flow.floating_payment for flow in cash_flows] == pytest.approx(
        [0, -5, 2.5, 7.5]
    )
    assert [flow.net_settlement for flow in cash_flows] == pytest.approx(
        [-2.5, -7.5, 0, 5]
    )


def test_simulate_swap_supports_30_year_quarterly_path() -> None:
    inputs = SwapInputs(1_000_000, 0.04, 30, 4, Position.PAY_FIXED)

    cash_flows = simulate_swap(inputs, [0.04] * 120)

    assert len(cash_flows) == 120
    assert cash_flows[-1].period == 120
    assert cash_flows[-1].time_years == pytest.approx(30.0)
    assert cash_flows[-1].cumulative_net == pytest.approx(0.0)


def test_summarize_empty_list_returns_zeros() -> None:
    summary = summarize([])

    assert summary.total_fixed == 0.0
    assert summary.total_floating == 0.0
    assert summary.total_net == 0.0
    assert summary.average_floating_rate == 0.0
    assert summary.periods_receiving == 0
    assert summary.periods_paying == 0


def test_summarize_counts_zero_as_neither() -> None:
    cash_flows = simulate_swap(
        worked_example_inputs(Position.PAY_FIXED), [0.035, 0.04, 0.045, 0.05]
    )

    summary = summarize(cash_flows)

    assert summary.total_fixed == pytest.approx(80_000)
    assert summary.total_floating == pytest.approx(85_000)
    assert summary.average_floating_rate == pytest.approx(0.0425)
    assert summary.periods_receiving == 2
    assert summary.periods_paying == 1