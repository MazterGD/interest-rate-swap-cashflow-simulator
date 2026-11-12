"""Rate-path, net-settlement and cumulative-net charts (spec §9.4). Owner: M5."""
import warnings

import altair as alt
import pandas as pd
import streamlit as st

from swap.models import PeriodCashFlow
from ui.formatting import ACCENT, FIXED, FIXED_LINE, FLOATING, MUTED, NEGATIVE, POSITIVE, TEXT
from ui.walkthrough import PERIOD_KEY

CHART_HINT = (
    "Hover a period to see its numbers. Click one to explain it in "
    "“Show the maths” below; the shaded column marks that period."
)

# Each panel is labelled where it is read: a title with its unit, plus an inline colour key.
# Keys: (swatch kind, colour, label); swatch kinds are styled in ui/theme.py.
PANEL_HEADINGS = (
    ("Floating vs fixed rate (%)", (("line", FLOATING, "Floating"), ("dash", FIXED, "Fixed"))),
    ("Net settlement each period ($)", (("box", POSITIVE, "You receive"), ("box", NEGATIVE, "You pay"))),
    ("Running total ($)", (("line", TEXT, "Above 0 means you are ahead overall"),)),
)

PICK_PARAM = "period_pick"
# Panel heights in px (spec §9.4). Rendered fitted to the column, they include the x axis.
RATES_HEIGHT, NET_HEIGHT, CUMULATIVE_HEIGHT = 180, 250, 180
PANEL_KEYS = ("chart_rates", "chart_net", "chart_cumulative")
_LAST_PICK_KEY = "_settlement_chart_last_pick"

# A fixed y-axis width keeps the three plot areas aligned when they render as separate charts.
AXIS = dict(labelColor=MUTED, titleColor=MUTED, domainColor=MUTED, tickColor=MUTED, labelFontSize=11)
Y_AXIS = dict(minExtent=44, maxExtent=44, **AXIS)
GRID = dict(grid=True, gridColor="#E9ECF3")
# Compact money ticks (20k, −40k) that still print a plain 0 at the baseline.
MONEY_LABELS = "datum.value === 0 ? '0' : format(datum.value, '~s')"


def _frame(cash_flows: list[PeriodCashFlow], fixed_rate: float) -> pd.DataFrame:
    return pd.DataFrame({
        "Period":           [cf.period for cf in cash_flows],
        "Floating Rate":    [round(cf.floating_rate * 100, 6) for cf in cash_flows],
        "Fixed Rate":       [round(fixed_rate * 100, 6)] * len(cash_flows),
        "Floating Payment": [cf.floating_payment for cf in cash_flows],
        "Fixed Payment":    [cf.fixed_payment for cf in cash_flows],
        "Net":              [cf.net_settlement for cf in cash_flows],
        "Cumulative":       [cf.cumulative_net for cf in cash_flows],
    })


def build_panels(
    cash_flows: list[PeriodCashFlow], fixed_rate: float, highlight_period: int | None = None
) -> tuple[alt.LayerChart, alt.LayerChart, alt.LayerChart]:
    """The three panels (rates, net, cumulative), each a layer chart sharing x = Period.

    Every panel has a near-transparent full-height band on top that carries the shared
    tooltip (rates, both payments, net, cumulative), a hover tint, the click selection
    `period_pick`, and a tint on `highlight_period`.
    """
    df = _frame(cash_flows, fixed_rate)
    # Ordinal x so spacing is even regardless of period count; only the bottom panel is titled.
    x_plain = alt.X("Period:O", axis=alt.Axis(labelAngle=0, title=None, **AXIS))
    x_titled = alt.X("Period:O", axis=alt.Axis(labelAngle=0, title="Period", **AXIS))
    hover = alt.selection_point(
        name="hover", fields=["Period"], on="pointerover", clear="pointerout", empty=False
    )
    pick = alt.selection_point(name=PICK_PARAM, fields=["Period"], on="click", empty=False)
    band_opacity = (
        alt.when(alt.datum.Period == (highlight_period or -1)).then(alt.value(0.13))
        .when(hover).then(alt.value(0.07))
        .otherwise(alt.value(0.001))
    )
    tooltip = [
        alt.Tooltip("Period:O", title="Period"),
        alt.Tooltip("Floating Rate:Q", title="Floating rate (%)", format=".2f"),
        alt.Tooltip("Fixed Rate:Q", title="Fixed rate (%)", format=".2f"),
        alt.Tooltip("Floating Payment:Q", title="Floating payment ($)", format=",.2f"),
        alt.Tooltip("Fixed Payment:Q", title="Fixed payment ($)", format=",.2f"),
        alt.Tooltip("Net:Q", title="Net settlement ($)", format=",.0f"),
        alt.Tooltip("Cumulative:Q", title="Cumulative net ($)", format=",.0f"),
    ]

    def band(x: alt.X = x_plain) -> alt.Chart:
        return (
            alt.Chart(df)
            .mark_bar(color=ACCENT, cursor="pointer")
            .encode(x=x, opacity=band_opacity, tooltip=tooltip)
            .add_params(hover, pick)
        )

    zero_rule = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(
        color=MUTED, strokeWidth=1
    ).encode(y="y:Q")

    # ── 1. Rates ──────────────────────────────────────────────────────────────
    floating_line = alt.Chart(df).mark_line(
        color=FLOATING, strokeWidth=2.5, point=alt.OverlayMarkDef(color=FLOATING, size=40)
    ).encode(
        x=x_plain,
        y=alt.Y(
            "Floating Rate:Q", title=None,
            scale=alt.Scale(zero=False, padding=8),  # show the movement, not the distance to 0
            axis=alt.Axis(**GRID, **Y_AXIS),
        ),
    )
    # One horizontal rule across the panel (no x encoding, or it becomes per-period ticks).
    fixed_rule = alt.Chart(pd.DataFrame({"Fixed Rate": [round(fixed_rate * 100, 6)]})).mark_rule(
        color=FIXED_LINE, strokeDash=[5, 4], strokeWidth=2
    ).encode(y="Fixed Rate:Q")
    rates = (floating_line + fixed_rule + band()).properties(height=RATES_HEIGHT)

    # ── 2. Net settlement bars ────────────────────────────────────────────────
    # Green only for receive, red only for pay; a zero period stays neutral (spec §9.2).
    bar_colour = alt.value(
        MUTED,
        condition=[
            {"test": "datum.Net > 0", "value": POSITIVE},
            {"test": "datum.Net < 0", "value": NEGATIVE},
        ],
    )
    bars = alt.Chart(df).mark_bar(cornerRadius=3).encode(
        x=x_plain,
        y=alt.Y("Net:Q", title=None, axis=alt.Axis(labelExpr=MONEY_LABELS, **GRID, **Y_AXIS)),
        color=bar_colour,
    )
    net = (bars + zero_rule + band()).properties(height=NET_HEIGHT)

    # ── 3. Cumulative net line ────────────────────────────────────────────────
    cumulative_line = alt.Chart(df).mark_line(
        color=TEXT, strokeWidth=2, point=alt.OverlayMarkDef(color=TEXT, size=30)
    ).encode(
        x=x_titled,
        y=alt.Y("Cumulative:Q", title=None, axis=alt.Axis(labelExpr=MONEY_LABELS, **GRID, **Y_AXIS)),
    )
    cumulative = (cumulative_line + zero_rule + band(x_titled)).properties(height=CUMULATIVE_HEIGHT)
    return rates, net, cumulative


def _configure(chart):
    return (
        chart.configure_legend(disable=True)
        .configure_view(stroke=None)
        .configure_axis(labelFont="sans-serif", titleFont="sans-serif", titleFontWeight=500)
    )


def build_settlement_chart(
    cash_flows: list[PeriodCashFlow], fixed_rate: float, highlight_period: int | None = None
) -> alt.Chart:
    """Pure builder (spec §6.2 contract): the three panels stacked as one vconcat."""
    # Graceful empty-input fallback — must not raise (spec §10.1).
    if not cash_flows:
        return alt.Chart(pd.DataFrame()).mark_bar()
    # The same hover/pick parameters sit on all three bands on purpose: Altair merges them
    # into one shared selection. Silence only that notice.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Automatically deduplicated selection parameter")
        return _configure(alt.vconcat(*build_panels(cash_flows, fixed_rate, highlight_period), spacing=18))


def panel_heading_html(title: str, keys: tuple) -> str:
    """One panel's heading: bold title, then a colour key per series (text carries the meaning)."""
    swatches = "".join(
        f'<span class="irs-key"><span class="irs-swatch irs-swatch--{kind}" '
        f'style="color: {colour}" aria-hidden="true"></span>{label}</span>'
        for kind, colour, label in keys
    )
    return f'<div class="irs-panel-head"><span class="irs-panel-title">{title}</span>{swatches}</div>'


def _picked_period(event) -> int | None:
    """The period from a chart's click selection, or None when nothing is selected."""
    try:
        points = event["selection"][PICK_PARAM]
    except (KeyError, TypeError):
        return None
    return int(points[0]["Period"]) if points else None


def render_settlement_chart(
    cash_flows: list[PeriodCashFlow], fixed_rate: float
) -> None:
    """Render the panels as separate full-width charts, so each fits the column exactly.

    A new click in any panel sets the walkthrough period (spec §9.6).
    """
    st.subheader("Cash flows over time")
    st.markdown(f'<p class="irs-hint">{CHART_HINT}</p>', unsafe_allow_html=True)
    if not cash_flows:
        return
    # The walkthrough starts on period 1, so shade it before its slider has rendered.
    current = st.session_state.get(PERIOD_KEY, 1)
    highlight = current if len(cash_flows) > 1 and 1 <= current <= len(cash_flows) else None
    last_picks = st.session_state.setdefault(_LAST_PICK_KEY, {})
    new_pick = None
    panels = build_panels(cash_flows, fixed_rate, highlight)
    for key, panel, (title, keys) in zip(PANEL_KEYS, panels, PANEL_HEADINGS):
        # A label belongs to its chart: keep them close, and the panels apart.
        with st.container(gap="xsmall"):
            st.markdown(panel_heading_html(title, keys), unsafe_allow_html=True)
            event = st.altair_chart(
                _configure(panel), width="stretch", on_select="rerun",
                selection_mode=PICK_PARAM, key=key,
            )
        picked = _picked_period(event)
        # Act only on a new click, so dragging the slider afterwards is not overridden.
        if picked != last_picks.get(key):
            last_picks[key] = picked
            new_pick = picked if picked is not None else new_pick
    if new_pick is not None and 1 <= new_pick <= len(cash_flows):
        st.session_state[PERIOD_KEY] = new_pick
        st.rerun()
