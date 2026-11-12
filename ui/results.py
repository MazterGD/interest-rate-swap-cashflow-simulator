"""Hero result, insight chips and cash-flow table with CSV download (spec §9). Owner: M4."""
import streamlit as st

from swap.export import cash_flows_to_dataframe, to_csv_bytes
from swap.models import PeriodCashFlow, SwapInputs, SwapSummary
from ui.formatting import MUTED, NEGATIVE, POSITIVE, fmt_money, fmt_rate, fmt_signed_money


def _years(tenor: int) -> str:
    return f"{tenor} year" if tenor == 1 else f"{tenor} years"


def render_summary(summary: SwapSummary, inputs: SwapInputs) -> None:
    """Hero card: label, amount and verdict on the left; the two legs stacked on the right."""
    if summary.total_net > 0:
        label, tone = "You receive", "receive"
    elif summary.total_net < 0:
        label, tone = "You pay", "pay"
    else:
        label, tone = "You break even", "even"

    st.markdown(
        f'<section class="irs-hero irs-hero--{tone}" aria-label="Result">'
        '<div class="irs-hero__main">'
        f'<div class="irs-hero__label">{label}</div>'
        f'<div class="irs-hero__amount">{fmt_signed_money(summary.total_net)}</div>'
        f'<div class="irs-hero__verdict">over {_years(inputs.tenor_years)} · floating averaged '
        f"{fmt_rate(summary.average_floating_rate)} vs {fmt_rate(inputs.fixed_rate)} fixed</div>"
        "</div>"
        '<div class="irs-legs">'
        '<div class="irs-leg irs-leg--fixed"><div class="irs-leg__name">'
        '<span class="irs-leg__dot"></span>Fixed leg · Party A pays</div>'
        f'<div class="irs-leg__value">{fmt_money(summary.total_fixed)}</div></div>'
        '<div class="irs-leg irs-leg--floating"><div class="irs-leg__name">'
        '<span class="irs-leg__dot"></span>Floating leg · Party B pays</div>'
        f'<div class="irs-leg__value">{fmt_money(summary.total_floating)}</div></div>'
        "</div></section>",
        unsafe_allow_html=True,
    )


def render_insights(
    cash_flows: list[PeriodCashFlow], summary: SwapSummary, inputs: SwapInputs
) -> None:
    """Three chips that turn the totals into lessons (spec §9.6, D9)."""
    if not cash_flows:
        return
    largest = max(cash_flows, key=lambda flow: abs(flow.net_settlement))
    # Equal accruals and a constant fixed leg mean the swap nets to zero when K = average L.
    chips = [
        ("Break-even fixed rate", fmt_rate(summary.average_floating_rate),
         "The fixed rate that would make the total net settlement zero: the average floating rate."),
        ("Periods in your favour", f"{summary.periods_receiving} of {len(cash_flows)}",
         f"You pay in {summary.periods_paying}; the rest net to zero."),
        ("Largest settlement", f"{fmt_signed_money(largest.net_settlement)} in period {largest.period}",
         "The single period with the biggest net payment, from your side."),
    ]
    st.markdown(
        '<div class="irs-chips">'
        + "".join(
            f'<span class="irs-chip" title="{tip}">{name} <strong>{value}</strong></span>'
            for name, value, tip in chips
        )
        + "</div>",
        unsafe_allow_html=True,
    )


def render_cash_flow_table(cash_flows: list[PeriodCashFlow]) -> None:
    """Formatted table in an expander plus the CSV download button."""
    df = cash_flows_to_dataframe(cash_flows)

    def signed_amount(amount: float) -> str:
        sign = "+" if amount > 0 else "−" if amount < 0 else ""
        return f"{sign}{abs(amount):,.2f}"

    def net_colour(column):
        return [
            f"color: {POSITIVE if amount > 0 else NEGATIVE if amount < 0 else MUTED}"
            for amount in column
        ]

    styled = df.style.format({
        "Period": "{:.0f}",
        "Time (yrs)": "{:.2f}",
        "Floating rate (%)": "{:.2f}%",
        "Fixed payment": "{:,.2f}",
        "Floating payment": "{:,.2f}",
        "Net settlement": signed_amount,
        "Cumulative net": signed_amount,
    }).set_properties(**{"text-align": "right"}).apply(
        net_colour, subset=["Net settlement"]
    )
    with st.expander("Payment schedule: every period", expanded=False):
        st.dataframe(styled, hide_index=True, width="stretch")
        st.download_button(
            "Download CSV", data=to_csv_bytes(df),
            file_name="swap_cash_flows.csv", mime="text/csv",
            icon=":material/download:",
        )
