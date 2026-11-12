"""Unit tests for ui/walkthrough.py. Owner: M6."""
import pytest
from streamlit.testing.v1 import AppTest

from swap.engine import simulate_swap
from swap.models import Position, SwapInputs
from ui.walkthrough import WALKTHROUGH_LABEL, build_steps, settlement_sentence

# Assignment brief sample: 10M notional, 8% fixed, 1 year, quarterly.
BRIEF_RATES = [0.065, 0.07, 0.09, 0.085]


def brief_inputs(position: Position) -> SwapInputs:
    return SwapInputs(10_000_000, 0.08, 1, 4, position)


def test_steps_show_the_users_numbers_in_the_formulas() -> None:
    inputs = brief_inputs(Position.PAY_FIXED)
    flow = simulate_swap(inputs, BRIEF_RATES)[0]
    latex = [step.latex for step in build_steps(flow, inputs)]

    assert len(latex) == 5
    assert r"\frac{1}{4} = 0.25" in latex[0]
    assert r"10{,}000{,}000 \times 8.00\% \times 0.25 = \$200{,}000.00" in latex[1]
    assert r"L_{1}" in latex[2] and r"6.50\%" in latex[2] and r"\$162{,}500.00" in latex[2]
    assert latex[3].endswith(r"= -\$37{,}500.00")  # pay fixed: floating - fixed
    assert latex[4].endswith(r"= -\$37{,}500.00")


def test_receive_fixed_net_formula_is_fixed_minus_floating() -> None:
    inputs = brief_inputs(Position.RECEIVE_FIXED)
    flow = simulate_swap(inputs, BRIEF_RATES)[1]
    net_step = build_steps(flow, inputs)[3]
    assert r"P_{\text{fixed}} - P_{\text{float}}" in net_step.latex
    assert net_step.latex.endswith(r"= \$25{,}000.00")


@pytest.mark.parametrize(
    "position, period, expected",
    [
        # Floating 6.5% < fixed 8%: the fixed payer (A) pays B, whatever the user's side.
        (Position.PAY_FIXED, 0, ["Party A pays Party B $37,500.00", "You are Party A", "you pay −$37,500"]),
        (Position.RECEIVE_FIXED, 0, ["Party A pays Party B $37,500.00", "You are Party B", "you receive +$37,500"]),
        # Floating 9% > fixed 8%: B pays A.
        (Position.PAY_FIXED, 2, ["Party B pays Party A $25,000.00", "above", "you receive +$25,000"]),
    ],
)
def test_settlement_sentence_says_who_pays_whom(position, period, expected) -> None:
    inputs = brief_inputs(position)
    flow = simulate_swap(inputs, BRIEF_RATES)[period]
    sentence = settlement_sentence(flow, inputs)
    for phrase in expected:
        assert phrase in sentence


def test_settlement_sentence_for_zero_net() -> None:
    inputs = SwapInputs(1_000_000, 0.04, 1, 1, Position.PAY_FIXED)
    flow = simulate_swap(inputs, [0.04])[0]
    assert "nobody pays" in settlement_sentence(flow, inputs)


def _render(num_rates: int) -> None:
    from swap.engine import simulate_swap
    from swap.models import Position, SwapInputs
    from ui.walkthrough import render_walkthrough

    inputs = SwapInputs(1_000_000, 0.04, 1, num_rates, Position.PAY_FIXED)
    render_walkthrough(simulate_swap(inputs, [0.05] * num_rates), inputs)


def test_renders_open_expander_with_period_picker_and_formulas() -> None:
    at = AppTest.from_function(_render, args=(4,)).run()
    assert not at.exception
    assert at.expander[0].label == WALKTHROUGH_LABEL
    assert at.expander[0].proto.expanded is True
    assert len(at.select_slider) == 1
    assert len(at.latex) == 5

    at.select_slider(key="walkthrough_period").set_value(3).run()
    assert not at.exception
    assert r"L_{3}" in at.latex[2].value


def test_single_period_swap_renders_without_slider() -> None:
    at = AppTest.from_function(_render, args=(1,)).run()
    assert not at.exception
    assert len(at.select_slider) == 0
    assert len(at.latex) == 5
