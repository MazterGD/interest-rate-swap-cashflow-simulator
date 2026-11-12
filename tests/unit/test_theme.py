"""Unit tests for ui/theme.py. Owner: M6."""
from ui.theme import _CSS


def test_page_has_one_scroll_only():
    """No sticky or self-scrolling regions: the whole page scrolls as one (D10 review)."""
    assert "position: sticky" not in _CSS
    assert "position: fixed" not in _CSS
    assert "overflow-y: auto" not in _CSS
    assert "max-height" not in _CSS


def test_style_block_is_well_formed():
    assert _CSS.strip().startswith("<style>") and _CSS.strip().endswith("</style>")
    assert _CSS.count("{") == _CSS.count("}")
