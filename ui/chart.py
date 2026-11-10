"""Rate-path and net-settlement charts (spec §9.4). Owner: M5.

PLACEHOLDER from the kickoff skeleton — M5 replaces build_settlement_chart.
"""
import altair as alt
import pandas as pd
import streamlit as st

from swap.models import PeriodCashFlow


def build_settlement_chart(cash_flows: list[PeriodCashFlow], fixed_rate: float) -> alt.Chart:
    """Pure builder: rate lines (top) + net settlement bars (bottom), shared x = Period."""
    # TODO(M5): real vconcat chart. Placeholder is an empty bar chart.
    return alt.Chart(pd.DataFrame()).mark_bar()


def render_settlement_chart(cash_flows: list[PeriodCashFlow], fixed_rate: float) -> None:
    """Render the chart at full container width."""
    st.altair_chart(build_settlement_chart(cash_flows, fixed_rate), width="stretch")
