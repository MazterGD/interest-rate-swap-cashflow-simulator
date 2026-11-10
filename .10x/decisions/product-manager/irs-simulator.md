# Product Manager — irs-simulator
**User:** a student, lecturer or demo audience learning how IRS cash flows work.
**Core job (<= 30 s):** "If I pay fixed / receive floating on this notional, what do I pay or receive each period and overall?"

## User stories (MVP)
1. As a user I enter notional, fixed rate, tenor and frequency, and see results instantly.
2. As a user I toggle Pay fixed / Receive fixed to see both sides of the trade.
3. As a user I pick a rate-path preset and tweak any period to explore "what if".
4. As a user I see the total net settlement first, then a chart explaining it, then the table.
5. As a user I download the cash flows as CSV.
6. As a newcomer I open a short explainer of how swaps work.

## Success criteria
- The worked example (spec §3) reproduces +$5,000 exactly.
- A first-time user reads the answer within 30 s without instructions.
- Runs locally with two pip packages; `pytest` is green.

## Out of scope
See spec §2 (day counts, discounting, spreads, amortisation, persistence, deployment). Deliverables: code only (README D5).
