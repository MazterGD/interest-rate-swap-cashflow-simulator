"""Shared display helpers and colour tokens (spec §9.3). Owner: M4.

The colour constants are final. The fmt_* bodies are PLACEHOLDERS — M4 replaces them.
"""

POSITIVE = "#1A7F37"    # you receive
NEGATIVE = "#CF222E"    # you pay
MUTED = "#656D76"       # secondary text, axes
FIXED_LINE = "#8C959F"  # dashed fixed-rate line
ACCENT = "#2F5BEA"      # controls, floating-rate line


def fmt_money(x: float) -> str:
    """1234567.8 -> "$1,234,568"."""
    # TODO(M4)
    return str(x)


def fmt_signed_money(x: float) -> str:
    """5000 -> "+$5,000", -2500 -> "−$2,500" (U+2212), 0 -> "$0"."""
    # TODO(M4)
    return str(x)


def fmt_rate(r: float) -> str:
    """0.0425 -> "4.25%"."""
    # TODO(M4)
    return str(r)
