"""'How a swap works' explainer (spec §9.5). Owner: M6."""
import streamlit as st

EXPLAINER_LABEL = "How a swap works"

EXPLAINER_TEXT = """\
An **interest-rate swap** is an agreement between two parties to exchange interest payments \
on the same **notional** amount. **Party A** pays a **fixed** rate; **Party B** pays a \
**floating** rate that resets every period. The notional itself never changes hands. Each \
period, only the **difference** is settled.

| Symbol | Meaning |
|---|---|
| N | Notional |
| K | Fixed rate (a year) |
| Lᵢ | Floating rate in period i |
| α = 1/f | Year fraction (quarterly → 0.25) |

Fixed payment = N × K × α · Floating payment = N × Lᵢ × α

**Who pays whom:** if floating > fixed, Party B pays Party A the difference. If floating < \
fixed, Party A pays Party B. **Pay fixed** (Party A) gains when rates rise; **receive fixed** \
(Party B) gains when they fall. Companies use swaps to hedge, e.g. to turn a floating-rate \
loan into a predictable fixed cost.

*Example:* on 1,000,000 at 4% fixed, paid semi-annually, the fixed leg is 20,000 a period. \
If the floating rate is 5%, the floating leg is 25,000, so Party B pays the fixed payer a net 5,000.
"""


def render_explainer() -> None:
    """One collapsed expander, <= 200 words, with symbols, formulas and the spec §3 example."""
    with st.expander(EXPLAINER_LABEL, icon=":material/school:", expanded=False):
        st.markdown(EXPLAINER_TEXT)
