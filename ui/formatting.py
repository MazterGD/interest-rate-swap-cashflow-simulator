"""Shared display helpers and colour tokens (spec §9.3). Owner: M4."""

POSITIVE = "#1A7F37"    # you receive
NEGATIVE = "#CF222E"    # you pay
MUTED = "#656D76"       # secondary text, axes
FIXED_LINE = "#8C959F"  # dashed fixed-rate line
ACCENT = "#2F5BEA"      # controls, floating-rate line


def fmt_money(x: float) -> str:
    """1234567.8 -> "$1,234,568"."""
    sign = "−" if x < 0 else ""
    return f"{sign}${abs(x):,.0f}"


def fmt_signed_money(x: float) -> str:
    """5000 -> "+$5,000", -2500 -> "−$2,500" (U+2212), 0 -> "$0"."""
    sign = "+" if x > 0 else "−" if x < 0 else ""
    return f"{sign}${abs(x):,.0f}"


def fmt_rate(r: float) -> str:
    """0.0425 -> "4.25%"."""
    return f"{r * 100:.2f}%"
