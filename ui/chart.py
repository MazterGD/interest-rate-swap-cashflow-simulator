"""Rate-path, net-settlement and cumulative-net charts (spec §9.4). Owner: M5."""
import altair as alt
import pandas as pd
import streamlit as st

from swap.models import PeriodCashFlow
from ui.formatting import ACCENT, FIXED_LINE, MUTED, NEGATIVE, POSITIVE, TEXT


CHART_GUIDE = (
    "Top: floating vs fixed rate. Each payment is N × rate × α, so the gap between the "
    "lines is what gets settled. Middle: net settlement each period (green = you receive, "
    "red = you pay). Bottom: the running total."
)

AXIS = dict(labelColor=MUTED, titleColor=MUTED, domainColor=MUTED, tickColor=MUTED)


def build_settlement_chart(
    cash_flows: list[PeriodCashFlow], fixed_rate: float
) -> alt.Chart:
    """Pure builder: three panels sharing x = Period (spec §9.4).

    1. Rates (~140 px): floating-rate line (ACCENT) + dashed fixed-rate rule (FIXED_LINE).
       Tooltip shows both rates and both payments, so it doubles as the payment comparison.
    2. Net settlement (~220 px): bars, POSITIVE if > 0, NEGATIVE if < 0, MUTED if 0.
    3. Cumulative net (~140 px): greyscale line of the running total.

    No chart title or legend.
    """
    # Graceful empty-input fallback — must not raise (spec §10.1).
    if not cash_flows:
        return alt.Chart(pd.DataFrame()).mark_bar()

    df = pd.DataFrame({
        "Period":           [cf.period for cf in cash_flows],
        "Floating Rate":    [round(cf.floating_rate * 100, 6) for cf in cash_flows],
        "Fixed Rate":       [round(fixed_rate * 100, 6)] * len(cash_flows),
        "Floating Payment": [cf.floating_payment for cf in cash_flows],
        "Fixed Payment":    [cf.fixed_payment for cf in cash_flows],
        "Net":              [cf.net_settlement for cf in cash_flows],
        "Cumulative":       [cf.cumulative_net for cf in cash_flows],
    })

    # Ordinal x so spacing is even regardless of period count.
    x_enc = alt.X("Period:O", axis=alt.Axis(**AXIS))
    period_tip = alt.Tooltip("Period:O", title="Period")
    zero_rule = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(
        color=MUTED, strokeWidth=1
    ).encode(y="y:Q")

    # ── 1. Rates ──────────────────────────────────────────────────────────────
    base_top = alt.Chart(df).encode(x=x_enc)
    floating_line = base_top.mark_line(color=ACCENT, point=True).encode(
        y=alt.Y(
            "Floating Rate:Q",
            title="Rate (%)",
            axis=alt.Axis(grid=True, gridColor="#EEEEEE", **AXIS),
        ),
        tooltip=[
            period_tip,
            alt.Tooltip("Floating Rate:Q", title="Floating rate (%)", format=".2f"),
            alt.Tooltip("Fixed Rate:Q", title="Fixed rate (%)", format=".2f"),
            alt.Tooltip("Floating Payment:Q", title="Floating payment ($)", format=",.2f"),
            alt.Tooltip("Fixed Payment:Q", title="Fixed payment ($)", format=",.2f"),
        ],
    )
    fixed_rule = base_top.mark_rule(
        color=FIXED_LINE, strokeDash=[4, 4], strokeWidth=1.5
    ).encode(y="Fixed Rate:Q")
    rates = (floating_line + fixed_rule).properties(height=140)

    # ── 2. Net settlement bars ────────────────────────────────────────────────
    # Green only for receive, red only for pay; a zero period stays neutral (spec §9.2).
    bar_colour = alt.value(
        MUTED,
        condition=[
            {"test": "datum.Net > 0", "value": POSITIVE},
            {"test": "datum.Net < 0", "value": NEGATIVE},
        ],
    )
    bars = alt.Chart(df).mark_bar().encode(
        x=x_enc,
        y=alt.Y("Net:Q", title="Net settlement ($)", axis=alt.Axis(format=",.0f", **AXIS)),
        color=bar_colour,
        tooltip=[
            period_tip,
            alt.Tooltip("Floating Rate:Q", title="Floating rate (%)", format=".2f"),
            alt.Tooltip("Net:Q", title="Net settlement ($)", format=",.0f"),
        ],
    )
    net = (bars + zero_rule).properties(height=220)

    # ── 3. Cumulative net line ────────────────────────────────────────────────
    cumulative_line = alt.Chart(df).mark_line(color=TEXT, point=True).encode(
        x=x_enc,
        y=alt.Y("Cumulative:Q", title="Cumulative net ($)", axis=alt.Axis(format=",.0f", **AXIS)),
        tooltip=[
            period_tip,
            alt.Tooltip("Cumulative:Q", title="Cumulative net ($)", format=",.0f"),
        ],
    )
    cumulative = (cumulative_line + zero_rule).properties(height=140)

    return (
        alt.vconcat(rates, net, cumulative)
        .configure_legend(disable=True)
        .configure_view(stroke=None)
        .configure_axis(labelFont="sans-serif", titleFont="sans-serif")
    )


def render_settlement_chart(
    cash_flows: list[PeriodCashFlow], fixed_rate: float
) -> None:
    """Render the chart at full container width with a one-line reading guide (spec §6.2)."""
    st.caption(CHART_GUIDE)
    st.altair_chart(
        build_settlement_chart(cash_flows, fixed_rate),
        width="stretch",
    )
