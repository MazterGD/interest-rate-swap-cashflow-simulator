"""Floating-rate preset picker and per-period editor (spec §7, §8). Owner: M2.

PLACEHOLDER from the kickoff skeleton — M2 replaces the body below.
"""
import streamlit as st


def render_rate_editor(num_periods: int) -> list[float]:
    """Render preset, start rate and editable table. Return num_periods decimal rates."""
    # TODO(M2): real widgets + st.data_editor. Placeholder returns a flat 3.5% path.
    st.write("rates_editor — TODO")
    return [0.035] * num_periods
