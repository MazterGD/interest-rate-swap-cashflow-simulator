"""Interest-Rate Swap Simulator — composition only (spec §5). No business logic here.

Layout (spec §9.8, D10): full width, one page scroll. The title with its lede underneath,
then the controls rail (40%) beside the results canvas (60%), then the step-by-step maths
across the full width. Phones stack everything into one column.

Run with:  streamlit run app.py
"""
import streamlit as st

from swap.engine import simulate_swap, summarize
from swap.validation import validate_inputs, validate_rates
from ui.chart import render_settlement_chart
from ui.explainer import render_explainer
from ui.inputs import render_swap_inputs
from ui.rates_editor import render_rate_editor
from ui.results import render_cash_flow_table, render_insights, render_summary
from ui.theme import apply_theme
from ui.walkthrough import render_walkthrough

st.set_page_config(page_title="IRS Simulator", layout="wide")
apply_theme()

GRID = [2, 3]  # controls rail : results canvas

st.title("Interest-Rate Swap Simulator")
st.markdown(
    '<p class="irs-lede">Two parties swap interest payments on the same notional. '
    "Set the terms, pick how the floating rate moves, and see who pays whom each period.</p>",
    unsafe_allow_html=True,
)

rail, canvas = st.columns(GRID, gap="large")
with rail:
    with st.container(border=True, key="terms_card"):
        inputs = render_swap_inputs()
    with st.container(border=True, key="rates_card"):
        rates = render_rate_editor(inputs.num_periods)
    render_explainer()

with canvas:
    errors = validate_inputs(inputs) + validate_rates(rates, inputs.num_periods)
    if errors:
        for message in errors:
            st.warning(message)
        st.stop()

    cash_flows = simulate_swap(inputs, rates)
    summary = summarize(cash_flows)

    render_summary(summary, inputs)
    render_insights(cash_flows, summary, inputs)
    render_settlement_chart(cash_flows, inputs.fixed_rate)
    render_cash_flow_table(cash_flows)

# Last, across the full width: the period walkthrough (driven by clicks in the charts above).
render_walkthrough(cash_flows, inputs)
