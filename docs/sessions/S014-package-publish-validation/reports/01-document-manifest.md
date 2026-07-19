# Document manifest — S014 / EV-010 (01-requirements delta)

**Status:** approved (E10-16 = 16A, 2026-07-18)  
**Mode:** delta (evolve)  
**Features:** F11, F12, F13, F14

## Mandatory

| # | Document | Rationale |
|---|----------|-----------|
| 1 | Feature List | Add F11–F14; update F2/F6 package publish status |
| 2 | Spec | Package boundaries, Rust validator, msgspec HTTP, codegen |
| 3 | User Journeys | PyPI consumer journeys + operator paths if HTTP msgspec changes FE |
| 4 | Test Plan | Benches (#703), parity, wheel-install, H0c/H4–H5 if HTTP breaks |

## Recommended

| # | Document | Relevance | Rationale |
|---|----------|-----------|-----------|
| 5 | API Contract | High | msgspec HTTP / faster-than-pydantic validation may change DTO shapes |
| 6 | Dependency Inventory | High | Rust crates, maturin, schema bundle, PyPI publish tooling |
| 7 | Config Spec | Medium | PyPI trusted publishing secrets; optional schema bundle path overrides |
| 8 | Deploy / tech-spec delta | High | Render redeploy + PyPI tag workflow (E10-15) |
| 9 | ADRs | High | ADR-026 (msgspec vs pydantic); possibly Schematron/codegen ADRs |
| 10 | Acceptance Criteria | Medium | Per-Fn gates for publish + perf + parity |

## Excluded (this cycle)

- **Data Management Plan** — no new external datasets beyond existing vendor pins
- **Roadmap** — delivery is this cycle’s execution plan, not a multi-quarter roadmap doc

## Interview order (proposed)

1. Feature List (F11–F14 acceptance stubs)  
2. Spec deltas (packages + HTTP msgspec + Rust layers)  
3. API Contract (which routes leave pydantic)  
4. User Journeys + Test Plan  
5. Dependencies + Config + Deploy notes  
6. ADRs (ADR-026 required; others as decisions land)
