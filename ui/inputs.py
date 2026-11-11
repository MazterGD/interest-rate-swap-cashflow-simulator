"""Swap-terms inputs (spec §8, §9.1). Owner: M3."""
import streamlit as st

from swap.models import Position, SwapInputs


def render_swap_inputs() -> SwapInputs:
    """Render swap terms, returning the fixed rate as a decimal."""
    left, right = st.columns(2)
    with left:
        notional = st.number_input(
            "Notional",
            min_value=1_000.0,
            max_value=1_000_000_000_000.0,
            value=1_000_000.0,
            step=100_000.0,
            format="%.0f",
            key="notional",
            help="The amount used to calculate interest payments. It is never exchanged.",
        )
    with right:
        fixed_rate_percent = st.number_input(
            "Fixed rate (%)",
            min_value=0.0,
            max_value=30.0,
            value=4.0,
            step=0.05,
            format="%.2f",
            key="fixed_rate",
        )

    left, right = st.columns(2)
    with left:
        tenor_years = st.number_input(
            "Tenor (years)", min_value=1, max_value=30, value=5,
            step=1, key="tenor_years",
        )
    with right:
        frequency_labels = {1: "Annual", 2: "Semi-annual", 4: "Quarterly"}
        payments_per_year = st.segmented_control(
            "Frequency",
            options=[1, 2, 4],
            default=2,
            format_func=lambda frequency: frequency_labels[frequency],
            key="payments_per_year",
        )

    position_labels = {
        Position.PAY_FIXED: "Pay fixed",
        Position.RECEIVE_FIXED: "Receive fixed",
    }
    position = st.segmented_control(
        "Position",
        options=list(Position),
        default=Position.PAY_FIXED,
        format_func=lambda selected: position_labels[selected],
        key="position",
    )
    # Segmented controls can be deselected; keep the returned terms usable.
    return SwapInputs(
        notional=notional,
        fixed_rate=fixed_rate_percent / 100,
        tenor_years=tenor_years,
        payments_per_year=payments_per_year if payments_per_year is not None else 2,
        position=position if position is not None else Position.PAY_FIXED,
    )
