"""Unit tests for ui/explainer.py. Owner: M6."""
import re

from streamlit.testing.v1 import AppTest

from ui.explainer import EXPLAINER_LABEL, EXPLAINER_TEXT


def _render() -> None:
    from ui.explainer import render_explainer

    render_explainer()


def test_explainer_is_at_most_120_words() -> None:
    words = re.findall(r"[\w,.%]+", EXPLAINER_TEXT.replace("*", ""))
    assert len(words) <= 120


def test_explainer_uses_the_worked_example() -> None:
    # Spec §3: 1,000,000 notional, 4% fixed, semi-annual -> 20,000 fixed leg; 5% float -> net 5,000.
    for figure in ("1,000,000", "4%", "20,000", "25,000", "5,000"):
        assert figure in EXPLAINER_TEXT


def test_renders_one_collapsed_expander() -> None:
    at = AppTest.from_function(_render).run()
    assert not at.exception
    assert [e.label for e in at.expander] == [EXPLAINER_LABEL]
    assert at.expander[0].proto.expanded is False
    assert at.expander[0].markdown[0].value.strip() == EXPLAINER_TEXT.strip()
