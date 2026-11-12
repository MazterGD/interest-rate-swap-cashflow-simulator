"""Party A ⇄ Party B cash-flow diagram for one period (spec §9.6, D9). Owner: M6.

A pure builder returns an inline SVG string, so it is unit-testable without Streamlit.
The two gross legs are drawn faintly because they cancel; the net arrow is the cash that moves.
"""
from html import escape

from swap.models import PeriodCashFlow, Position, SwapInputs
from ui.formatting import (
    FIXED, FIXED_BG, FLOATING, FLOATING_BG, MUTED, NEGATIVE, POSITIVE, TEXT, ACCENT, fmt_rate,
)

_W, _H = 640, 260
_A_X, _B_X, _NODE_W, _NODE_Y, _NODE_H = 24, 456, 160, 64, 84


def _money(amount: float) -> str:
    return f"${abs(amount):,.0f}"


def _node(x: int, name: str, role: str, stroke: str, fill: str, is_you: bool) -> str:
    cx = x + _NODE_W // 2
    badge = (
        f'<rect x="{cx - 26}" y="{_NODE_Y - 34}" width="52" height="24" rx="12" fill="{ACCENT}"/>'
        f'<text x="{cx}" y="{_NODE_Y - 17}" text-anchor="middle" font-size="13" '
        f'font-weight="700" fill="#FFFFFF">You</text>'
        if is_you else ""
    )
    return (
        f"{badge}"
        f'<rect x="{x}" y="{_NODE_Y}" width="{_NODE_W}" height="{_NODE_H}" rx="16" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{2.5 if is_you else 1.5}"/>'
        f'<text x="{cx}" y="{_NODE_Y + 37}" text-anchor="middle" font-size="18" '
        f'font-weight="700" fill="{TEXT}">{name}</text>'
        f'<text x="{cx}" y="{_NODE_Y + 60}" text-anchor="middle" font-size="13" '
        f'fill="{stroke}">{role}</text>'
    )


def _marker(marker_id: str, colour: str) -> str:
    return (
        f'<marker id="{marker_id}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
        f'fill="{colour}"/></marker>'
    )


def net_direction(flow: PeriodCashFlow, inputs: SwapInputs) -> str | None:
    """'A->B', 'B->A' or None. The fixed payer (A) receives exactly when floating > fixed."""
    if flow.net_settlement == 0:
        return None
    return "B->A" if flow.floating_rate > inputs.fixed_rate else "A->B"


def build_flow_svg(flow: PeriodCashFlow, inputs: SwapInputs) -> str:
    """Inline SVG: both parties, both gross legs, and the net arrow for one period."""
    you_are_a = inputs.position == Position.PAY_FIXED
    direction = net_direction(flow, inputs)
    left, right = _A_X + _NODE_W + 10, _B_X - 10
    mid = _W // 2
    fixed_y, float_y = _NODE_Y + 24, _NODE_Y + _NODE_H - 24

    if direction is None:
        net_colour, net_label = MUTED, "Net: nothing changes hands"
        net_path = f'<path d="M{_A_X + 80},{_NODE_Y + _NODE_H} V214 H{_B_X + 80} V{_NODE_Y + _NODE_H}" ' \
                   f'fill="none" stroke="{MUTED}" stroke-width="3" stroke-dasharray="6 6"/>'
    else:
        payer, receiver = ("A", "B") if direction == "A->B" else ("B", "A")
        net_colour = POSITIVE if flow.net_settlement > 0 else NEGATIVE
        net_label = f"Net: Party {payer} pays Party {receiver} {_money(flow.net_settlement)}"
        start_x = _A_X + 80 if payer == "A" else _B_X + 80
        end_x = _B_X + 80 if payer == "A" else _A_X + 80
        net_path = (
            f'<path d="M{start_x},{_NODE_Y + _NODE_H + 2} V214 H{end_x} V{_NODE_Y + _NODE_H + 8}" '
            f'fill="none" stroke="{net_colour}" stroke-width="4" stroke-linejoin="round" '
            f'marker-end="url(#irs-net)"/>'
        )

    aria = escape(
        f"Period {flow.period}: Party A owes fixed {_money(flow.fixed_payment)}, Party B owes "
        f"floating {_money(flow.floating_payment)}. {net_label}."
    )
    return (
        f'<svg viewBox="0 0 {_W} {_H}" role="img" aria-label="{aria}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="inherit">'
        f"<defs>{_marker('irs-fixed', FIXED)}{_marker('irs-float', FLOATING)}"
        f"{_marker('irs-net', net_colour)}</defs>"
        + _node(_A_X, "Party A", "pays fixed", FIXED, FIXED_BG, you_are_a)
        + _node(_B_X, "Party B", "pays floating", FLOATING, FLOATING_BG, not you_are_a)
        # Gross legs: faint, because they offset each other.
        + f'<line x1="{left}" y1="{fixed_y}" x2="{right}" y2="{fixed_y}" stroke="{FIXED}" '
          f'stroke-width="2" stroke-opacity="0.55" marker-end="url(#irs-fixed)"/>'
        + f'<text x="{mid}" y="{fixed_y - 9}" text-anchor="middle" font-size="13" '
          f'fill="{FIXED}">Fixed {fmt_rate(inputs.fixed_rate)} · {_money(flow.fixed_payment)}</text>'
        + f'<line x1="{right}" y1="{float_y}" x2="{left}" y2="{float_y}" stroke="{FLOATING}" '
          f'stroke-width="2" stroke-opacity="0.55" marker-end="url(#irs-float)"/>'
        + f'<text x="{mid}" y="{float_y + 20}" text-anchor="middle" font-size="13" '
          f'fill="{FLOATING}">Floating {fmt_rate(flow.floating_rate)} · '
          f"{_money(flow.floating_payment)}</text>"
        + f'<text x="{mid}" y="{(fixed_y + float_y) // 2 + 4}" text-anchor="middle" '
          f'font-size="12" fill="{MUTED}">they offset; only the net moves</text>'
        + net_path
        + f'<text x="{mid}" y="240" text-anchor="middle" font-size="15" font-weight="700" '
          f'fill="{net_colour}">{escape(net_label)}</text>'
        + "</svg>"
    )
