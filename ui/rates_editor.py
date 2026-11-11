"""Floating-rate preset picker and per-period editor (spec §7, §8). Owner: M2."""
import pandas as pd
import streamlit as st

from swap.models import RatePreset
from swap.scenarios import generate_rates


def render_rate_editor(num_periods: int) -> list[float]:
    """Render preset, start rate and editable table. Return num_periods decimal rates."""
    preset = st.segmented_control(
        "Preset",
        list(RatePreset),
        default=RatePreset.RISING,
        format_func=lambda option: option.name.title(),
    )
    start_rate_pct = st.number_input(
        "Start rate (%)",
        min_value=0.0,
        max_value=30.0,
        value=3.5,
        step=0.05,
    )
    start_rate = float(start_rate_pct) / 100

    default_rates = generate_rates(preset, num_periods, start_rate)
    rate_df = pd.DataFrame(
        {
            "Period": list(range(1, num_periods + 1)),
            "Rate (%)": [rate * 100 for rate in default_rates],
        }
    )

    data_key = f"rates-{preset.value}-{start_rate_pct}-{num_periods}"
    with st.expander(":material/edit: Edit individual periods", expanded=False):
        edited_df = st.data_editor(
            rate_df,
            key=data_key,
            hide_index=True,
            disabled=["Period"],
            column_config={
                "Period": st.column_config.NumberColumn("Period", disabled=True),
                "Rate (%)": st.column_config.NumberColumn(
                    "Rate (%)",
                    min_value=-5.0,
                    max_value=30.0,
                    step=0.05,
                ),
            },
        )

    if edited_df is None or edited_df.empty:
        return default_rates
    return [float(rate) / 100 for rate in edited_df["Rate (%)"].tolist()]
