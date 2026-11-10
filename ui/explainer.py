"""'How a swap works' explainer (spec §9.5). Owner: M6."""
import streamlit as st

EXPLAINER_LABEL = "How a swap works"

EXPLAINER_TEXT = """\
An **interest-rate swap** is an agreement to exchange interest payments on the same \
notional amount. One side pays a **fixed** rate; the other pays a **floating** rate that \
resets every period. The notional itself never changes hands — each period, only the \
**difference** is settled.

**Pay fixed** gains when floating rates rise above the fixed rate; **receive fixed** gains \
when they fall. Companies use swaps to hedge, for example to turn a floating-rate loan \
into a predictable fixed cost.

*Example:* on 1,000,000 at 4% fixed, paid semi-annually, the fixed leg is 20,000 a period. \
If the floating rate is 5%, the floating leg is 25,000, so the fixed payer receives a net 5,000.
"""


def render_explainer() -> None:
    """One collapsed expander, <= 120 words, using the spec §3 worked example."""
    with st.expander(EXPLAINER_LABEL, icon=":material/school:", expanded=False):
        st.markdown(EXPLAINER_TEXT)
