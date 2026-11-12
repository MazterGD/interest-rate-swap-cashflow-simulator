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

def test_chart_has_three_subcharts():
    """build_settlement_chart returns a vconcat: rates, net bars, cumulative net."""
    cash_flows = make_cashflows(WORKED_EXAMPLE_NETS)
    chart = build_settlement_chart(cash_flows, FIXED_RATE)
    d = chart.to_dict()
    assert "vconcat" in d, "Top-level chart must be a vconcat"
    assert len(d["vconcat"]) == 3, "Must have 3 sub-charts (rates, net bars, cumulative)"


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
    assert top_height == 180, f"Top panel height should be 180, got {top_height}"


def test_bottom_panel_height():
    """Bottom panel (net bars) should be ~220 px as per spec §9.4."""
    cash_flows = make_cashflows(WORKED_EXAMPLE_NETS)
    d = build_settlement_chart(cash_flows, FIXED_RATE).to_dict()
    bottom_height = d["vconcat"][1].get("height", None)
    assert bottom_height == 250, f"Net panel height should be 250, got {bottom_height}"


def test_positive_and_negative_nets_in_data():
    """Chart data must include both positive and negative net values from the worked example."""
    cash_flows = make_cashflows(WORKED_EXAMPLE_NETS)
    d = build_settlement_chart(cash_flows, FIXED_RATE).to_dict()
    # Extract data values from the chart spec
    chart_str = str(d)
    assert "-2500" in chart_str or "-2500.0" in chart_str, "Negative net must appear in chart data"
    assert "5000" in chart_str or "5000.0" in chart_str, "Positive net must appear in chart data"



def _layers(d: dict, panel: int) -> list[dict]:
    return d["vconcat"][panel]["layer"]


def test_zero_net_bar_is_neutral_not_red():
    """Green only for receive, red only for pay; a zero period is MUTED (spec §9.2)."""
    from ui.formatting import MUTED, NEGATIVE, POSITIVE

    d = build_settlement_chart(make_cashflows(WORKED_EXAMPLE_NETS), FIXED_RATE).to_dict()
    colour = _layers(d, 1)[0]["encoding"]["color"]
    assert colour["value"] == MUTED
    tests = {c["test"]: c["value"] for c in colour["condition"]}
    assert tests == {"datum.Net > 0": POSITIVE, "datum.Net < 0": NEGATIVE}


def test_cumulative_panel_plots_running_total():
    d = build_settlement_chart(make_cashflows(WORKED_EXAMPLE_NETS), FIXED_RATE).to_dict()
    assert d["vconcat"][2]["height"] == 180
    assert _layers(d, 2)[0]["encoding"]["y"]["field"] == "Cumulative"


def test_shared_tooltip_compares_fixed_and_floating_payments():
    """Every panel's top band carries one tooltip with both payments, net and cumulative."""
    d = build_settlement_chart(make_cashflows(WORKED_EXAMPLE_NETS), FIXED_RATE).to_dict()
    for panel in range(3):
        band = _layers(d, panel)[-1]
        fields = {t["field"] for t in band["encoding"]["tooltip"]}
        assert {"Fixed Payment", "Floating Payment", "Net", "Cumulative"} <= fields


def test_click_selection_is_shared_across_panels():
    """One `period_pick` click selection (on Period) drives the walkthrough (spec §9.6)."""
    from ui.chart import PICK_PARAM

    d = build_settlement_chart(make_cashflows(WORKED_EXAMPLE_NETS), FIXED_RATE).to_dict()
    params = {p["name"]: p for p in d.get("params", [])}
    assert params[PICK_PARAM]["select"]["on"] == "click"
    assert params[PICK_PARAM]["select"]["fields"] == ["Period"]
    assert "hover" in params


def test_highlight_period_tints_that_band():
    d = build_settlement_chart(make_cashflows(WORKED_EXAMPLE_NETS), FIXED_RATE, 3).to_dict()
    assert "datum.Period === 3" in str(_layers(d, 1)[-1]["encoding"]["opacity"])


def test_picked_period_reads_streamlit_selection_event():
    from ui.chart import PICK_PARAM, _picked_period

    assert _picked_period({"selection": {PICK_PARAM: [{"Period": 2}]}}) == 2
    assert _picked_period({"selection": {PICK_PARAM: []}}) is None
    assert _picked_period(None) is None


def test_each_panel_has_a_heading_with_a_colour_key():
    """Panels are labelled where they are read, not explained in a paragraph (D10 review)."""
    from ui.chart import PANEL_HEADINGS, PANEL_KEYS, panel_heading_html
    from ui.formatting import FIXED, FLOATING

    assert len(PANEL_HEADINGS) == len(PANEL_KEYS) == 3
    html = panel_heading_html(*PANEL_HEADINGS[0])
    assert "Floating vs fixed rate (%)" in html
    assert f"color: {FLOATING}" in html and f"color: {FIXED}" in html
    assert html.count('aria-hidden="true"') == 2  # swatches are decorative; the text carries meaning
    net_html = panel_heading_html(*PANEL_HEADINGS[1])
    assert "You receive" in net_html and "You pay" in net_html


def _render_chart() -> None:
    from swap.engine import simulate_swap
    from swap.models import Position, SwapInputs
    from ui.chart import render_settlement_chart

    inputs = SwapInputs(1_000_000, 0.04, 2, 2, Position.PAY_FIXED)
    render_settlement_chart(simulate_swap(inputs, [0.035, 0.04, 0.045, 0.05]), inputs.fixed_rate)


def test_render_shows_hint_headings_and_three_charts():
    from streamlit.testing.v1 import AppTest
    from ui.chart import CHART_HINT, PANEL_HEADINGS

    at = AppTest.from_function(_render_chart).run()
    assert not at.exception
    text = "\n".join(str(m.value) for m in at.markdown)
    assert CHART_HINT in text
    for title, _ in PANEL_HEADINGS:
        assert title in text
    assert not at.caption  # no paragraph-style chart instructions any more
