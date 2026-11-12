"""M3 validation boundaries and isolated input-widget behavior (spec §8)."""
from dataclasses import replace

import pytest
from streamlit.testing.v1 import AppTest

from swap.models import Position, SwapInputs
from swap.validation import validate_inputs, validate_rates


DEFAULT_INPUTS = SwapInputs(1_000_000, 0.04, 5, 2, Position.PAY_FIXED)


def test_defaults_are_valid() -> None:
    assert validate_inputs(DEFAULT_INPUTS) == []
    assert validate_rates([0.035] * 10, DEFAULT_INPUTS.num_periods) == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("notional", 1_000), ("notional", 1_001),
        ("notional", 999_999_999_999), ("notional", 1_000_000_000_000),
        ("fixed_rate", 0.0), ("fixed_rate", 0.000001),
        ("fixed_rate", 0.299999), ("fixed_rate", 0.30),
        ("tenor_years", 1), ("tenor_years", 2),
        ("tenor_years", 29), ("tenor_years", 30),
        ("payments_per_year", 1), ("payments_per_year", 2),
        ("payments_per_year", 4),
        ("position", Position.PAY_FIXED), ("position", Position.RECEIVE_FIXED),
    ],
)
def test_valid_terms_at_and_inside_limits(field: str, value: object) -> None:
    assert validate_inputs(replace(DEFAULT_INPUTS, **{field: value})) == []


@pytest.mark.parametrize(
    "field,value,label",
    [
        ("notional", 999, "Notional"),
        ("notional", 1_000_000_000_001, "Notional"),
        ("fixed_rate", -0.000001, "Fixed rate"),
        ("fixed_rate", 0.300001, "Fixed rate"),
        ("tenor_years", 0, "Tenor"), ("tenor_years", 31, "Tenor"),
        ("tenor_years", 1.5, "Tenor"), ("tenor_years", True, "Tenor"),
        ("payments_per_year", 0, "Frequency"),
        ("payments_per_year", 3, "Frequency"),
        ("payments_per_year", 5, "Frequency"),
        ("payments_per_year", 2.5, "Frequency"),
        ("payments_per_year", True, "Frequency"),
        ("position", "invalid", "Position"), ("position", None, "Position"),
    ],
)
def test_invalid_term_returns_one_clear_error(
    field: str, value: object, label: str,
) -> None:
    errors = validate_inputs(replace(DEFAULT_INPUTS, **{field: value}))
    assert len(errors) == 1
    assert label in errors[0]


@pytest.mark.parametrize("field", ["notional", "fixed_rate"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_terms_are_invalid(field: str, value: float) -> None:
    assert len(validate_inputs(replace(DEFAULT_INPUTS, **{field: value}))) == 1


@pytest.mark.parametrize("rate", [-0.05, -0.049999, 0.0, 0.299999, 0.30])
def test_rates_at_and_inside_limits(rate: float) -> None:
    assert validate_rates([rate], 1) == []


@pytest.mark.parametrize(
    "rate", [-0.050001, 0.300001, 0.40, float("nan"), float("inf"), -float("inf")],
)
def test_bad_rate_names_its_one_based_period(rate: float) -> None:
    assert validate_rates([0.035, 0.04, rate, 0.05], 4) == [
        "Period 3 rate must be between −5% and 30%."
    ]


@pytest.mark.parametrize("length", [0, 3, 5])
def test_wrong_rate_count(length: int) -> None:
    assert validate_rates([0.035] * length, 4) == [
        f"Expected 4 floating rates, but received {length}."
    ]


def test_length_and_rate_errors_are_both_reported() -> None:
    assert validate_rates([0.40, -0.06], 4) == [
        "Expected 4 floating rates, but received 2.",
        "Period 1 rate must be between −5% and 30%.",
        "Period 2 rate must be between −5% and 30%.",
    ]


def test_independent_input_errors_are_all_reported() -> None:
    inputs = replace(DEFAULT_INPUTS, notional=0, fixed_rate=-0.01, tenor_years=31)
    errors = validate_inputs(inputs)
    assert len(errors) == 3
    assert all(any(label in error for error in errors) for label in ("Notional", "Fixed rate", "Tenor"))


@pytest.mark.parametrize("tenor,frequency,count", [(1, 1, 1), (30, 4, 120)])
def test_minimum_and_maximum_period_counts(tenor: int, frequency: int, count: int) -> None:
    inputs = replace(DEFAULT_INPUTS, tenor_years=tenor, payments_per_year=frequency)
    assert inputs.num_periods == count
    assert validate_inputs(inputs) == []
    assert validate_rates([0.035] * count, inputs.num_periods) == []


def _render_inputs() -> None:
    """Expose the component's return value without depending on other workstreams."""
    import streamlit as st
    from ui.inputs import render_swap_inputs

    st.session_state["result"] = render_swap_inputs()


def test_input_widgets_defaults_bounds_and_labels() -> None:
    at = AppTest.from_function(_render_inputs).run()
    assert not at.exception
    assert not at.warning
    assert at.session_state["result"] == DEFAULT_INPUTS
    for key, label, minimum, maximum, step in [
        ("notional", "Notional", 1_000, 1_000_000_000_000, 100_000),
        ("fixed_rate", "Fixed rate (%)", 0, 30, 0.05),
        ("tenor_years", "Tenor (years)", 1, 30, 1),
    ]:
        widget = at.number_input(key=key)
        assert widget.label == label
        assert widget.min == minimum
        assert widget.max == maximum
        assert widget.step == step
        assert widget.help  # every term explains itself (spec §9.6 learning aids)
    assert at.segmented_control(key="position").options == ["Pay fixed", "Receive fixed"]
    assert "Party A" in at.segmented_control(key="position").help
    assert at.segmented_control(key="payments_per_year").options == [
        "Annual", "Semi-annual", "Quarterly"
    ]
    assert not at.button


def test_input_edits_return_decimal_rate_and_selected_terms() -> None:
    at = AppTest.from_function(_render_inputs).run()
    at.number_input(key="notional").set_value(2_000_000.0)
    at.number_input(key="fixed_rate").set_value(4.25)
    at.number_input(key="tenor_years").set_value(30)
    at.segmented_control(key="payments_per_year").set_value(4)
    at.segmented_control(key="position").set_value(Position.RECEIVE_FIXED).run()
    assert not at.exception
    result = at.session_state["result"]
    assert result == SwapInputs(2_000_000, 0.0425, 30, 4, Position.RECEIVE_FIXED)
    assert result.num_periods == 120
    assert validate_inputs(result) == []


def test_deselected_controls_fall_back_to_defaults() -> None:
    at = AppTest.from_function(_render_inputs).run()
    at.segmented_control(key="payments_per_year").set_value(None)
    at.segmented_control(key="position").set_value(None).run()
    assert not at.exception
    assert at.session_state["result"] == DEFAULT_INPUTS


@pytest.mark.parametrize("rate_percent", [0.0, 30.0])
def test_fixed_rate_widget_boundaries_convert_to_decimals(rate_percent: float) -> None:
    at = AppTest.from_function(_render_inputs).run()
    at.number_input(key="fixed_rate").set_value(rate_percent).run()
    assert not at.exception
    assert at.session_state["result"].fixed_rate == pytest.approx(rate_percent / 100)
