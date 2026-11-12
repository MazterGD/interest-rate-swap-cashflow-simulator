"""'Show the maths' walkthrough: the spec §3 formulas with the user's numbers (spec §9.6). Owner: M6.

Reads values already computed by the engine; it never recalculates a cash flow.
"""
from dataclasses import dataclass

import streamlit as st

from swap.models import PeriodCashFlow, Position, SwapInputs
from ui.formatting import MUTED, NEGATIVE, POSITIVE, fmt_rate, fmt_signed_money

WALKTHROUGH_LABEL = "Show the maths, step by step"

RULE_OF_THUMB = (
    "Rule of thumb: when floating is above fixed, the fixed payer (Party A) receives the "
    "difference. When floating is below fixed, the floating payer (Party B) receives it."
)


@dataclass(frozen=True)
class Step:
    title: str
    explanation: str
    latex: str


def _tex_money(amount: float) -> str:
    """-37500 -> '-\\$37{,}500.00' (KaTeX-safe thousands separators)."""
    sign = "-" if amount < 0 else ""
    return sign + r"\$" + f"{abs(amount):,.2f}".replace(",", "{,}")


def _tex_number(value: float) -> str:
    return f"{value:,.0f}".replace(",", "{,}")


def _tex_rate(rate: float) -> str:
    return f"{rate * 100:.2f}" + r"\%"


def _tex_alpha(alpha: float) -> str:
    return f"{alpha:g}"


def party_of(position: Position) -> str:
    return "Party A" if position == Position.PAY_FIXED else "Party B"


def settlement_sentence(flow: PeriodCashFlow, inputs: SwapInputs) -> str:
    """Plain-English 'who pays whom' for one period, plus what that means for the user."""
    floating, fixed = fmt_rate(flow.floating_rate), fmt_rate(inputs.fixed_rate)
    amount = abs(flow.net_settlement)
    you = f"You are {party_of(inputs.position)}"
    if flow.net_settlement == 0:
        return f"Floating ({floating}) equals fixed ({fixed}), so nobody pays anything this period."
    # The fixed payer (Party A) receives exactly when floating exceeds fixed.
    party_a_receives = flow.floating_rate > inputs.fixed_rate
    payer, receiver = ("Party B", "Party A") if party_a_receives else ("Party A", "Party B")
    comparison = "above" if party_a_receives else "below"
    verb = "receive" if flow.net_settlement > 0 else "pay"
    return (
        f"Floating ({floating}) is {comparison} fixed ({fixed}), so **{payer} pays {receiver} "
        f"${amount:,.2f}**. {you}, so you {verb} {fmt_signed_money(flow.net_settlement)}."
    )


def build_steps(flow: PeriodCashFlow, inputs: SwapInputs) -> list[Step]:
    """The spec §3 formulas for one period, with the user's numbers substituted."""
    i = flow.period
    n, k, f = inputs.notional, inputs.fixed_rate, inputs.payments_per_year
    alpha = inputs.accrual_fraction
    pay_fixed = inputs.position == Position.PAY_FIXED
    sign_note = (
        "As the fixed payer (Party A), your net is floating minus fixed."
        if pay_fixed
        else "As the fixed receiver (Party B), your net is fixed minus floating."
    )
    net_formula = (
        r"P_{\text{float}} - P_{\text{fixed}}" if pay_fixed else r"P_{\text{fixed}} - P_{\text{float}}"
    )
    first, second = (
        (flow.floating_payment, flow.fixed_payment) if pay_fixed
        else (flow.fixed_payment, flow.floating_payment)
    )
    return [
        Step(
            "1. Year fraction",
            "Each payment covers part of a year. With f payments a year, each period is 1/f of a year.",
            rf"\alpha = \frac{{1}}{{f}} = \frac{{1}}{{{f}}} = {_tex_alpha(alpha)}",
        ),
        Step(
            "2. Fixed leg (Party A pays)",
            "Notional × fixed rate × year fraction. It is the same every period.",
            rf"P_{{\text{{fixed}}}} = N \times K \times \alpha = {_tex_number(n)} \times "
            rf"{_tex_rate(k)} \times {_tex_alpha(alpha)} = {_tex_money(flow.fixed_payment)}",
        ),
        Step(
            "3. Floating leg (Party B pays)",
            "Notional × this period's floating rate × year fraction. It changes when the rate resets.",
            rf"P_{{\text{{float}}}} = N \times L_{{{i}}} \times \alpha = {_tex_number(n)} \times "
            rf"{_tex_rate(flow.floating_rate)} \times {_tex_alpha(alpha)} = "
            rf"{_tex_money(flow.floating_payment)}",
        ),
        Step(
            "4. Net settlement (the only cash that moves)",
            f"The notional is never exchanged; only the difference is paid. {sign_note} "
            "Positive means you receive, negative means you pay.",
            rf"\text{{Net}}_{{{i}}} = {net_formula} = {_tex_money(first)} - {_tex_money(second)} "
            rf"= {_tex_money(flow.net_settlement)}",
        ),
        Step(
            "5. Running total",
            "Add up every net settlement so far.",
            rf"C_{{{i}}} = \sum_{{j=1}}^{{{i}}} \text{{Net}}_j = {_tex_money(flow.cumulative_net)}",
        ),
    ]


def render_walkthrough(cash_flows: list[PeriodCashFlow], inputs: SwapInputs) -> None:
    """An open expander that walks through one chosen period with the real numbers."""
    if not cash_flows:
        return
    with st.expander(WALKTHROUGH_LABEL, expanded=True):
        if len(cash_flows) > 1:
            period = st.select_slider(
                "Walk through period",
                options=[flow.period for flow in cash_flows],
                value=1,
                key="walkthrough_period",
                help="Pick any period to see its numbers plugged into the formulas.",
            )
        else:
            period = 1
        flow = cash_flows[period - 1]

        for step in build_steps(flow, inputs):
            st.markdown(f"**{step.title}**  \n{step.explanation}")
            st.latex(step.latex)

        colour = POSITIVE if flow.net_settlement > 0 else NEGATIVE if flow.net_settlement < 0 else MUTED
        sentence = settlement_sentence(flow, inputs)
        st.markdown(
            f'<div style="border-left: 4px solid {colour}; padding-left: 0.75rem;">\n\n'
            f"{sentence}\n\n</div>",
            unsafe_allow_html=True,
        )
        st.caption(RULE_OF_THUMB)
