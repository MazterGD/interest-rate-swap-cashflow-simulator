"""Page-level styling on top of .streamlit/config.toml (spec §9.3, D9). Owner: M6.

Styles hook onto `st-key-<key>` classes that Streamlit adds to keyed containers, plus the
`irs-*` classes our own HTML blocks use, so no fragile internal selectors are needed.
"""
import streamlit as st

from ui.formatting import (
    FIXED, FIXED_BG, FLOATING, FLOATING_BG, MUTED, NEGATIVE, NEGATIVE_BG,
    NEUTRAL_BG, POSITIVE, POSITIVE_BG, TEXT,
)

CARD_KEYS = ("terms_card", "rates_card")

_CSS = f"""
<style>
.stApp ::selection {{ background: #E0E7FF; color: #1E1B4B; }}
.stApp h1 {{ letter-spacing: -0.03em; font-size: clamp(2.25rem, 3.2vw, 3.25rem); line-height: 1.05; padding-top: 0; }}
@media (min-width: 1024px) {{ .stApp h1 {{ white-space: nowrap; }} }}

/* Full-width canvas (D10): generous gutters, capped only on very large screens. */
[data-testid="stMainBlockContainer"], .block-container {{
  max-width: 1760px; padding: 1.25rem clamp(1rem, 3vw, 3.5rem) 4rem;
}}
/* One page scroll only: no sticky or self-scrolling regions (D10 follow-up). */
.stApp h3 {{ letter-spacing: -0.01em; }}

{", ".join(f".st-key-{key}" for key in CARD_KEYS)} {{
  background: #FFFFFF;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04), 0 12px 32px -18px rgba(15, 23, 42, 0.18);
}}
[data-testid="stExpander"] details {{
  background: #FFFFFF;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}}
[data-testid="stExpander"] summary p {{ font-weight: 600; }}

/* The lede sits directly under the title, on the same left edge as everything below. */
.stApp p.irs-lede {{ color: {MUTED}; font-size: 1.075rem; line-height: 1.55; max-width: 68ch; margin: -0.6rem 0 1.25rem; }}

/* Chart panels are labelled where they are read: a title plus an inline colour key. */
.stApp p.irs-hint {{ color: {MUTED}; font-size: 0.9rem; margin: -0.5rem 0 0.25rem; }}
/* Streamlit gives each markdown block `margin-bottom: -1rem` (it cancels a closing <p>'s
   1rem). A block that ends in a <div> must add that 1rem back, or the next element covers it. */
.irs-panel-head {{
  display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.25rem 1.1rem; margin: 0.5rem 0 1rem;
}}
.irs-panel-title {{ font-weight: 600; font-size: 0.95rem; color: {TEXT}; }}
.irs-key {{ display: inline-flex; align-items: center; gap: 0.4rem; font-size: 0.85rem; color: {MUTED}; }}
.irs-swatch {{ display: inline-block; flex: none; }}
.irs-swatch--line {{ width: 1.15rem; border-top: 3px solid currentColor; }}
.irs-swatch--dash {{ width: 1.15rem; border-top: 2.5px dashed currentColor; }}
.irs-swatch--box {{ width: 0.7rem; height: 0.7rem; border-radius: 2px; background: currentColor; }}

.irs-hero {{
  display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(15rem, 1fr); gap: 1.25rem 2rem;
  align-items: center; border-radius: 1.25rem; padding: 1.75rem 2rem; margin: 0 0 0.75rem;
  border: 1px solid transparent; font-variant-numeric: tabular-nums;
}}
@media (max-width: 720px) {{ .irs-hero {{ grid-template-columns: 1fr; padding: 1.5rem; }} }}
.irs-hero--receive {{ background: {POSITIVE_BG}; border-color: #BBF7D0; }}
.irs-hero--pay {{ background: {NEGATIVE_BG}; border-color: #FECACA; }}
.irs-hero--even {{ background: {NEUTRAL_BG}; border-color: #E2E5EE; }}
.irs-hero__label {{ font-weight: 600; font-size: 0.95rem; color: {TEXT}; }}
.irs-hero__amount {{ font-size: clamp(3rem, 4.6vw, 4.5rem); font-weight: 750; letter-spacing: -0.035em; line-height: 1.05; margin: 0.15rem 0 0.35rem; }}
.irs-hero--receive .irs-hero__amount {{ color: {POSITIVE}; }}
.irs-hero--pay .irs-hero__amount {{ color: {NEGATIVE}; }}
.irs-hero--even .irs-hero__amount {{ color: {MUTED}; }}
.irs-hero__verdict {{ color: {MUTED}; font-size: 0.95rem; }}
.irs-legs {{ display: flex; flex-direction: column; gap: 0.75rem; }}
.irs-leg {{
  background: rgba(255, 255, 255, 0.75); border-radius: 0.9rem;
  padding: 0.7rem 0.9rem; border: 1px solid rgba(15, 23, 42, 0.06);
}}
.irs-leg__name {{ display: flex; align-items: center; gap: 0.45rem; font-size: 0.85rem; color: {MUTED}; }}
.irs-leg__dot {{ width: 0.6rem; height: 0.6rem; border-radius: 999px; flex: none; }}
.irs-leg--fixed .irs-leg__dot {{ background: {FIXED}; }}
.irs-leg--floating .irs-leg__dot {{ background: {FLOATING}; }}
.irs-leg__value {{ font-size: 1.35rem; font-weight: 650; color: {TEXT}; letter-spacing: -0.01em; }}

.irs-chips {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0 0 1.75rem; font-variant-numeric: tabular-nums; }}
.irs-chip {{
  display: inline-flex; align-items: baseline; gap: 0.4rem; background: #FFFFFF;
  border: 1px solid #E2E5EE; border-radius: 999px; padding: 0.35rem 0.85rem;
  font-size: 0.875rem; color: {MUTED};
}}
.irs-chip strong {{ color: {TEXT}; font-weight: 650; }}

.irs-flow {{ background: #FBFBFE; border: 1px solid #E2E5EE; border-radius: 1rem; padding: 0.75rem; overflow-x: auto; }}
.irs-flow svg {{ display: block; width: 100%; max-width: 780px; min-width: 480px; height: auto; margin: 0 auto; }}
/* Long formulas scroll sideways on phones instead of being clipped. */
.stApp .katex-display {{ overflow-x: auto; overflow-y: hidden; padding: 0.25rem 0; }}
.stApp p.irs-flow__note {{ color: {MUTED}; font-size: 0.85rem; text-align: center; margin: 0.5rem 0 0; }}
.stApp p.irs-verdict {{ font-size: 1.05rem; line-height: 1.5; margin: 1rem 0; max-width: 70ch; }}
/* Formula steps sit beside the diagram at a slightly smaller size so long lines fit. */
.st-key-maths_steps {{ margin-top: 0; }}
.stApp .st-key-maths_steps .katex-display {{ font-size: 1.05em; }}
.irs-verdict strong {{ font-weight: 650; }}
.irs-fixed {{ color: {FIXED}; font-weight: 600; }}
.irs-floating {{ color: {FLOATING}; font-weight: 600; }}

</style>
"""


def apply_theme() -> None:
    """Inject the page styles once per run, before anything else renders."""
    st.markdown(_CSS, unsafe_allow_html=True)
