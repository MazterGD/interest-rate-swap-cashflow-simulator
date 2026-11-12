"""Full-app integration tests via Streamlit AppTest (spec §10.2). Owner: M6.

Integration day done (2026-11-12): every xfail mark is removed and all tests must pass.
"""
import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import ui.rates_editor
from swap.models import Position

pytestmark = pytest.mark.integration

APP_PATH = str(Path(__file__).resolve().parents[2] / "app.py")
HERO_LABELS = ("You receive", "You pay", "You break even")


def run_app() -> AppTest:
    return AppTest.from_file(APP_PATH, default_timeout=30).run()


def page_text(at: AppTest) -> str:
    """All plain text on the page: markdown, captions and text elements."""
    parts = [el.value for el in (*at.markdown, *at.caption, *at.text)]
    return "\n".join(str(p) for p in parts)


def hero_label(at: AppTest) -> str | None:
    """The label inside the hero card only (other copy, e.g. chart keys, may reuse the words)."""
    for element in at.markdown:
        match = re.search(r'class="irs-hero__label">([^<]+)<', str(element.value))
        if match:
            label = match.group(1)
            return label if label in HERO_LABELS else None
    return None


def test_page_shell_renders() -> None:
    at = run_app()
    assert not at.exception
    assert at.title[0].value == "Interest-Rate Swap Simulator"
    assert "How a swap works" in [e.label for e in at.expander]


def test_defaults_show_a_hero_verdict() -> None:
    at = run_app()
    assert not at.exception
    assert not at.warning
    # Spec §8 defaults: rising path from 3.50% vs 4.00% fixed, pay fixed -> floating ends above fixed.
    assert hero_label(at) == "You receive"


def test_switching_position_flips_the_hero() -> None:
    at = run_app()
    before = hero_label(at)

    # WORK_PLAN M3: st.segmented_control(key="position") whose options are the Position members.
    position = at.segmented_control(key="position")
    flipped = Position.RECEIVE_FIXED if position.value == Position.PAY_FIXED else Position.PAY_FIXED
    position.set_value(flipped).run()

    after = hero_label(at)
    assert not at.exception
    assert {before, after} == {"You receive", "You pay"}


def test_invalid_rate_stops_rendering(monkeypatch: pytest.MonkeyPatch) -> None:
    # A 40% rate is outside the spec §8 range (-5% to 30%).
    monkeypatch.setattr(ui.rates_editor, "render_rate_editor", lambda n: [0.40] * n)
    at = run_app()
    assert not at.exception
    assert at.warning, "expected a validation warning"
    assert hero_label(at) is None
    assert not at.download_button


def test_csv_download_button_is_present() -> None:
    at = run_app()
    assert not at.exception
    assert len(at.download_button) == 1


def test_walkthrough_shows_formulas_on_the_page() -> None:
    at = run_app()
    assert not at.exception
    assert "Show the maths, step by step" in [e.label for e in at.expander]
    assert len(at.latex) == 5


def test_deselecting_the_preset_does_not_crash() -> None:
    at = run_app()
    at.segmented_control(key="preset").set_value(None).run()
    assert not at.exception
    assert hero_label(at) is not None


def test_assignment_brief_sample(monkeypatch: pytest.MonkeyPatch) -> None:
    """Brief: 10M, 8% fixed, 1y quarterly, floating 6.5/7/9/8.5% -> fixed payer pays 25,000."""
    monkeypatch.setattr(
        ui.rates_editor, "render_rate_editor", lambda n: [0.065, 0.07, 0.09, 0.085]
    )
    at = AppTest.from_file(APP_PATH, default_timeout=30)
    at.session_state["notional"] = 10_000_000.0
    at.session_state["fixed_rate"] = 8.0
    at.session_state["tenor_years"] = 1
    at.session_state["payments_per_year"] = 4
    at.run()
    assert not at.exception
    assert hero_label(at) == "You pay"
    assert "−$25,000" in page_text(at)
    assert "Party A pays Party B $37,500.00" in page_text(at)

    at.segmented_control(key="position").set_value(Position.RECEIVE_FIXED).run()
    assert hero_label(at) == "You receive"
    assert "+$25,000" in page_text(at)


def test_header_is_title_then_lede() -> None:
    at = run_app()
    assert not at.exception
    assert at.title[0].value == "Interest-Rate Swap Simulator"
    assert any('class="irs-lede"' in str(m.value) for m in at.markdown)
