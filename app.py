"""Interest-Rate Swap Simulator — composition only (spec §5). No business logic here.

Run with:  streamlit run app.py
"""
import streamlit as st

from swap.engine import simulate_swap, summarize
from swap.validation import validate_inputs, validate_rates
from ui.chart import render_settlement_chart
from ui.explainer import render_explainer
from ui.inputs import render_swap_inputs
from ui.rates_editor import render_rate_editor
from ui.results import render_cash_flow_table, render_summary

st.set_page_config(page_title="IRS Simulator", layout="centered")
st.title("Interest-Rate Swap Simulator")
st.caption("See what you pay or receive each period.")

inputs = render_swap_inputs()
rates = render_rate_editor(inputs.num_periods)

errors = validate_inputs(inputs) + validate_rates(rates, inputs.num_periods)
if errors:
    for message in errors:
        st.warning(message)
    st.stop()

cash_flows = simulate_swap(inputs, rates)
summary = summarize(cash_flows)

render_summary(summary, inputs)
render_settlement_chart(cash_flows, inputs.fixed_rate)
render_cash_flow_table(cash_flows)
render_explainer()
