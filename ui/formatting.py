"""Shared display helpers and colour tokens (spec §9.3). Owner: M4."""

# Colour has a job (spec §9.3, D9): green/red = money you receive/pay, amber = the fixed
# leg and Party A, teal = the floating leg and Party B, indigo = controls and focus.
POSITIVE = "#15803D"     # you receive
NEGATIVE = "#B91C1C"     # you pay
MUTED = "#5B6475"        # secondary text, axes, zero values
FIXED = "#B45309"        # fixed leg / Party A
FLOATING = "#0E7490"     # floating leg / Party B
FIXED_LINE = FIXED       # dashed fixed-rate rule in the chart
ACCENT = "#4F46E5"       # interactive controls, selection, focus
TEXT = "#0F172A"         # body text, cumulative-net line (matches config.toml textColor)

POSITIVE_BG = "#ECFDF3"  # tinted hero surfaces, same meaning as the foreground colour
NEGATIVE_BG = "#FEF2F2"
NEUTRAL_BG = "#F1F3F8"
FIXED_BG = "#FFF7ED"
FLOATING_BG = "#ECFEFF"


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
