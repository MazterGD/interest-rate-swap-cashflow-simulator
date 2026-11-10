"""Headline summary and cash-flow table with CSV download (spec §9). Owner: M4.

PLACEHOLDER from the kickoff skeleton — M4 replaces the bodies below.
"""
import streamlit as st

from swap.models import PeriodCashFlow, SwapInputs, SwapSummary


def render_summary(summary: SwapSummary, inputs: SwapInputs) -> None:
    """Hero label + amount, verdict caption, Fixed leg / Floating leg metrics."""
    # TODO(M4)
    st.write("results.render_summary — TODO")


def render_cash_flow_table(cash_flows: list[PeriodCashFlow]) -> None:
    """Formatted table in an expander plus the CSV download button."""
    # TODO(M4)
    st.write("results.render_cash_flow_table — TODO")
