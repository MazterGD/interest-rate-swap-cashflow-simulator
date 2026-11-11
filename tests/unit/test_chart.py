"""Unit tests for ui/chart.py. Owner: M5."""
import pytest
import altair as alt

from swap.models import PeriodCashFlow
from ui.chart import build_settlement_chart


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_cashflows(nets: list[float]) -> list[PeriodCashFlow]:
    """Build a minimal list of PeriodCashFlow objects for testing."""
    return [
        PeriodCashFlow(
            period=i + 1,
            time_years=(i + 1) * 0.5,
            floating_rate=0.035 + i * 0.005,
            fixed_payment=20_000.0,
            floating_payment=20_000.0 + net,
            net_settlement=net,
            cumulative_net=sum(nets[: i + 1]),
        )
        for i, net in enumerate(nets)
    ]


# Canonical §3 worked example: N=1,000,000, K=4%, 2yr, semi-annual, pay fixed
WORKED_EXAMPLE_NETS = [-2500.0, 0.0, 2500.0, 5000.0]
FIXED_RATE = 0.04


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_chart_has_two_subcharts():
    """build_settlement_chart returns a vconcat with exactly 2 sub-charts."""
    cash_flows = make_cashflows(WORKED_EXAMPLE_NETS)
    chart = build_settlement_chart(cash_flows, FIXED_RATE)
    d = chart.to_dict()
    assert "vconcat" in d, "Top-level chart must be a vconcat"
    assert len(d["vconcat"]) == 2, "Must have exactly 2 sub-charts (rate lines + net bars)"


def test_chart_has_colour_condition_on_net():
    """The bottom chart encodes a conditional colour based on net sign."""
    cash_flows = make_cashflows(WORKED_EXAMPLE_NETS)
    chart = build_settlement_chart(cash_flows, FIXED_RATE)
    chart_str = str(chart.to_dict())
    assert "condition" in chart_str, "Chart must use a conditional colour encoding for net sign"


def test_empty_input_does_not_crash():
    """build_settlement_chart([]) must return a valid Altair chart without raising."""
    chart = build_settlement_chart([], FIXED_RATE)
    # Should be some kind of Altair chart object — just must not raise
    assert hasattr(chart, "to_dict"), "Result must be a valid Altair chart"
    chart.to_dict()  # must not raise


def test_120_periods_does_not_crash():
    """30-year quarterly = 120 periods must build without error."""
    nets = [100.0 * (i - 60) for i in range(120)]  # mix of positive and negative
    cash_flows = make_cashflows(nets)
    chart = build_settlement_chart(cash_flows, FIXED_RATE)
    d = chart.to_dict()
    assert "vconcat" in d, "120-period chart must still be a vconcat"


def test_top_panel_height():
    """Top panel (rate lines) should be ~140 px as per spec §9.4."""
    cash_flows = make_cashflows(WORKED_EXAMPLE_NETS)
    d = build_settlement_chart(cash_flows, FIXED_RATE).to_dict()
    top_height = d["vconcat"][0].get("height", None)
    assert top_height == 140, f"Top panel height should be 140, got {top_height}"


def test_bottom_panel_height():
    """Bottom panel (net bars) should be ~220 px as per spec §9.4."""
    cash_flows = make_cashflows(WORKED_EXAMPLE_NETS)
    d = build_settlement_chart(cash_flows, FIXED_RATE).to_dict()
    bottom_height = d["vconcat"][1].get("height", None)
    assert bottom_height == 220, f"Bottom panel height should be 220, got {bottom_height}"


def test_positive_and_negative_nets_in_data():
    """Chart data must include both positive and negative net values from the worked example."""
    cash_flows = make_cashflows(WORKED_EXAMPLE_NETS)
    d = build_settlement_chart(cash_flows, FIXED_RATE).to_dict()
    # Extract data values from the chart spec
    chart_str = str(d)
    assert "-2500" in chart_str or "-2500.0" in chart_str, "Negative net must appear in chart data"
    assert "5000" in chart_str or "5000.0" in chart_str, "Positive net must appear in chart data"

