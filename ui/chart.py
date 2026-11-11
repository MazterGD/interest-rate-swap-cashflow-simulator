"""Rate-path and net-settlement charts (spec §9.4). Owner: M5."""
import altair as alt
import pandas as pd
import streamlit as st

from swap.models import PeriodCashFlow
from ui.formatting import ACCENT, FIXED_LINE, MUTED, NEGATIVE, POSITIVE


def build_settlement_chart(
    cash_flows: list[PeriodCashFlow], fixed_rate: float
) -> alt.Chart:
    """Pure builder: rate lines (top) + net settlement bars (bottom), shared x = Period.

    Top panel (~140 px): floating-rate solid line (ACCENT) + fixed-rate dashed
    horizontal rule (FIXED_LINE).  Y axis in %.

    Bottom panel (~220 px): net settlement bars coloured POSITIVE (green) when
    net > 0, NEGATIVE (red) otherwise.  Zero baseline rule.  Tooltip shows
    Period, Floating rate, Net settlement.

    No chart title or legend (spec §9.4).  Shared x = Period (ordinal).
    """
    # Graceful empty-input fallback — must not raise (spec §10.1).
    if not cash_flows:
        return alt.Chart(pd.DataFrame()).mark_bar()

    # ── Build a single DataFrame for both panels ──────────────────────────────
    df = pd.DataFrame({
        "Period":        [cf.period for cf in cash_flows],
        "Floating Rate": [round(cf.floating_rate * 100, 6) for cf in cash_flows],  # → %
        "Fixed Rate":    [round(fixed_rate * 100, 6)] * len(cash_flows),            # → %
        "Net":           [cf.net_settlement for cf in cash_flows],
    })

    # Shared x encoding (ordinal so spacing is even regardless of period count).
    x_enc = alt.X(
        "Period:O",
        axis=alt.Axis(labelColor=MUTED, tickColor=MUTED, domainColor=MUTED),
    )

    # ── TOP PANEL — rate lines ────────────────────────────────────────────────
    base_top = alt.Chart(df).encode(x=x_enc)

    y_rate = alt.Y(
        "Floating Rate:Q",
        title="Rate (%)",
        axis=alt.Axis(
            labelColor=MUTED,
            titleColor=MUTED,
            grid=True,
            gridColor="#EEEEEE",
            domainColor=MUTED,
        ),
    )

    floating_line = base_top.mark_line(color=ACCENT, point=True).encode(y=y_rate)

    # Horizontal dashed rule at the fixed rate level (same y-scale).
    fixed_rule = base_top.mark_rule(
        color=FIXED_LINE, strokeDash=[4, 4], strokeWidth=1.5
    ).encode(y="Fixed Rate:Q")

    top = (floating_line + fixed_rule).properties(height=140)

    # ── BOTTOM PANEL — net settlement bars ───────────────────────────────────
    base_bottom = alt.Chart(df).encode(x=x_enc)

    color_condition = alt.condition(
        alt.datum["Net"] > 0,
        alt.value(POSITIVE),
        alt.value(NEGATIVE),
    )

    bars = base_bottom.mark_bar().encode(
        y=alt.Y(
            "Net:Q",
            title="Net settlement ($)",
            axis=alt.Axis(
                labelColor=MUTED,
                titleColor=MUTED,
                domainColor=MUTED,
                format=",.0f",
            ),
        ),
        color=color_condition,
        tooltip=[
            alt.Tooltip("Period:O", title="Period"),
            alt.Tooltip("Floating Rate:Q", title="Floating rate (%)", format=".2f"),
            alt.Tooltip("Net:Q", title="Net settlement ($)", format=",.0f"),
        ],
    )

    # Zero baseline rule so negative bars read clearly.
    zero_rule = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(
        color=MUTED, strokeWidth=1
    ).encode(y="y:Q")

    bottom = (bars + zero_rule).properties(height=220)

    # ── Combine ───────────────────────────────────────────────────────────────
    return (
        alt.vconcat(top, bottom)
        .configure_legend(disable=True)
        .configure_view(stroke=None)
        .configure_axis(labelFont="sans-serif", titleFont="sans-serif")
    )


def render_settlement_chart(
    cash_flows: list[PeriodCashFlow], fixed_rate: float
) -> None:
    """Render the chart at full container width (spec §6.2)."""
    st.altair_chart(
        build_settlement_chart(cash_flows, fixed_rate),
        width='stretch',
    )
