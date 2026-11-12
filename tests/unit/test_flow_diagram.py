"""Unit tests for ui/flow_diagram.py. Owner: M6."""
import xml.etree.ElementTree as ET

import pytest

from swap.engine import simulate_swap
from swap.models import Position, SwapInputs
from ui.flow_diagram import build_flow_svg, net_direction
from ui.formatting import MUTED, NEGATIVE, POSITIVE

BRIEF_RATES = [0.065, 0.07, 0.09, 0.085]


def flows(position: Position):
    inputs = SwapInputs(10_000_000, 0.08, 1, 4, position)
    return inputs, simulate_swap(inputs, BRIEF_RATES)


def test_svg_is_well_formed_and_labels_both_legs() -> None:
    inputs, cash_flows = flows(Position.PAY_FIXED)
    svg = build_flow_svg(cash_flows[0], inputs)
    ET.fromstring(svg)  # raises if malformed
    assert "Fixed 8.00% · $200,000" in svg
    assert "Floating 6.50% · $162,500" in svg
    assert "Net: Party A pays Party B $37,500" in svg
    assert 'role="img"' in svg and "aria-label" in svg


@pytest.mark.parametrize(
    "position, period, direction, colour",
    [
        (Position.PAY_FIXED, 0, "A->B", NEGATIVE),     # you are A and you pay
        (Position.RECEIVE_FIXED, 0, "A->B", POSITIVE),  # you are B and you receive
        (Position.PAY_FIXED, 2, "B->A", POSITIVE),     # floating 9% > fixed 8%
    ],
)
def test_net_arrow_direction_and_colour(position, period, direction, colour) -> None:
    inputs, cash_flows = flows(position)
    flow = cash_flows[period]
    assert net_direction(flow, inputs) == direction
    svg = build_flow_svg(flow, inputs)
    assert f'stroke="{colour}" stroke-width="4"' in svg


@pytest.mark.parametrize("position, centre_x", [(Position.PAY_FIXED, 104), (Position.RECEIVE_FIXED, 536)])
def test_you_badge_sits_on_the_users_party(position, centre_x) -> None:
    inputs, cash_flows = flows(position)
    svg = build_flow_svg(cash_flows[0], inputs)
    assert svg.count(">You</text>") == 1
    assert f'<text x="{centre_x}" y="47" text-anchor="middle" font-size="13" font-weight="700" fill="#FFFFFF">You</text>' in svg


def test_zero_net_is_dashed_and_neutral() -> None:
    inputs = SwapInputs(1_000_000, 0.04, 1, 1, Position.PAY_FIXED)
    flow = simulate_swap(inputs, [0.04])[0]
    assert net_direction(flow, inputs) is None
    svg = build_flow_svg(flow, inputs)
    assert "nothing changes hands" in svg and f'stroke="{MUTED}" stroke-width="3"' in svg
