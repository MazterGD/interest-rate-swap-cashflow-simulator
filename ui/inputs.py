"""Swap-terms inputs (spec §8, §9.1). Owner: M3."""
import streamlit as st

from swap.models import Position, SwapInputs
from ui.formatting import fmt_money

# Spec §8 defaults, in UI units. They are seeded into session state once instead of being
# passed as `value=`/`default=`, which avoids Streamlit's default-vs-session-state warning.
DEFAULTS = {
    "notional": 1_000_000.0,
    "fixed_rate": 4.0,
    "tenor_years": 5,
    "payments_per_year": 2,
    "position": Position.PAY_FIXED,
}


def render_swap_inputs() -> SwapInputs:
    """Render swap terms, returning the fixed rate as a decimal."""
    for key, value in DEFAULTS.items():
        st.session_state.setdefault(key, value)
    st.subheader("Swap terms")
    # Stacked for the narrow controls rail (D10): only the two short numbers share a row.
    # The readout belongs to its field, so the two sit in one tight group.
    notional_field = st.container(gap="xxsmall")
    notional = notional_field.number_input(
        "Notional",
        min_value=1_000.0,
        max_value=1_000_000_000_000.0,
        step=100_000.0,
        format="%.0f",
        key="notional",
        help="N: the amount used to calculate interest payments. It is never exchanged.",
    )
    # st.number_input cannot group digits, so confirm the amount in a readable form.
    notional_field.caption(f"{fmt_money(notional)} · sizes the payments, never exchanged")
    left, right = st.columns(2)
    with left:
        fixed_rate_percent = st.number_input(
            "Fixed rate (%)",
            min_value=0.0,
            max_value=30.0,
            step=0.05,
            format="%.2f",
            key="fixed_rate",
            help="K: the annual rate the fixed payer (Party A) pays every period. It never changes.",
        )
    with right:
        tenor_years = st.number_input(
            "Tenor (years)", min_value=1, max_value=30,
            step=1, key="tenor_years",
            help="T: how many years the swap runs. Number of periods n = T × payments per year.",
        )
    frequency_labels = {1: "Annual", 2: "Semi-annual", 4: "Quarterly"}
    payments_per_year = st.segmented_control(
        "Frequency",
        options=[1, 2, 4],
        format_func=lambda frequency: frequency_labels[frequency],
        key="payments_per_year",
        help="f: payments per year. Each period covers α = 1/f of a year (quarterly → 0.25).",
    )

    position_labels = {
        Position.PAY_FIXED: "Pay fixed",
        Position.RECEIVE_FIXED: "Receive fixed",
    }
    position = st.segmented_control(
        "Position",
        options=list(Position),
        format_func=lambda selected: position_labels[selected],
        key="position",
        help=(
            "Pay fixed = you are Party A: you pay fixed and receive floating. "
            "Receive fixed = you are Party B: you receive fixed and pay floating."
        ),
    )
    # Segmented controls can be deselected; keep the returned terms usable.
    return SwapInputs(
        notional=notional,
        fixed_rate=fixed_rate_percent / 100,
        tenor_years=tenor_years,
        payments_per_year=payments_per_year if payments_per_year is not None else 2,
        position=position if position is not None else Position.PAY_FIXED,
    )
