# Decisions — EV-1266 operational TAC delta

Session: EV-1266-operational-tac-delta. Ticket: #1266. Date: 2026-09-28.

[Corpus: product §F6] [Corpus: decisions]

| ID | Decision |
|----|----------|
| D1 | Scale **standard**. Spec→Build gate stays **closed** until documenting verify. |
| D2 | Deliverable is documentation under `docs/` (context brief + feature-list deepen + test-plan TC + selectable-profiles refresh). No product code. |
| D3 | Refresh the issue’s stale claims against #1267 (selectable profiles exist) and #1265 (matrices on `stage`). Do not claim “no convert profile” for the four catalog ids. |
| D4 | No new CORPUS member. Context briefs stay under `docs/context/`; design gates cite product / domain-profiles / tests. |
| D5 | UI preview N/A. H4–H5 N/A. No deploy. No `stage`→`main`. |
| D6 | Build band, when opened, is commit + PR into `stage` only (docs already drafted in Spec). |
| D7 | Memory Neo4j unavailable — fail-open; waive cross-project reuse for this docs ticket. |
