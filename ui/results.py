"""Headline summary and cash-flow table with CSV download (spec §9). Owner: M4."""
import streamlit as st

from swap.export import cash_flows_to_dataframe, to_csv_bytes
from swap.models import PeriodCashFlow, SwapInputs, SwapSummary
from ui.formatting import MUTED, NEGATIVE, POSITIVE, fmt_money, fmt_rate, fmt_signed_money


def render_summary(summary: SwapSummary, inputs: SwapInputs) -> None:
    """Hero label + amount, verdict caption, Fixed leg / Floating leg metrics."""
    if summary.total_net > 0:
        label, colour = "You receive", POSITIVE
    elif summary.total_net < 0:
        label, colour = "You pay", NEGATIVE
    else:
        label, colour = "You break even", MUTED

    st.caption(label)
    st.markdown(
        f'<span style="color: {colour}; font-size: 3.5rem; font-weight: 700;">'
        f'{fmt_signed_money(summary.total_net)}</span>',
        unsafe_allow_html=True,
    )
    st.caption(
        f"over {inputs.tenor_years} years · floating averaged "
        f"{fmt_rate(summary.average_floating_rate)} vs {fmt_rate(inputs.fixed_rate)} fixed"
    )
    fixed, floating = st.columns(2)
    fixed.metric("Fixed leg", fmt_money(summary.total_fixed))
    floating.metric("Floating leg", fmt_money(summary.total_floating))


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
    with st.expander("Cash-flow table", expanded=True):
        st.dataframe(styled, hide_index=True, width="stretch")
        st.download_button(
            "Download CSV", data=to_csv_bytes(df),
            file_name="swap_cash_flows.csv", mime="text/csv",
            icon=":material/download:",
        )
