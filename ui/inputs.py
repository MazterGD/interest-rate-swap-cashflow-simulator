"""Swap-terms inputs (spec §8, §9.1). Owner: M3.

PLACEHOLDER from the kickoff skeleton — M3 replaces the body below.
"""
import streamlit as st

from swap.models import Position, SwapInputs


def render_swap_inputs() -> SwapInputs:
    """Render notional, fixed rate, tenor, frequency and position. Rates returned as decimals.

    Give every widget a stable key= (e.g. key="position") so tests can find it.
    """
    # TODO(M3): real widgets. Placeholder returns the spec §8 defaults.
    st.write("inputs — TODO")
    return SwapInputs(
        notional=1_000_000,
        fixed_rate=0.04,
        tenor_years=5,
        payments_per_year=2,
        position=Position.PAY_FIXED,
    )
