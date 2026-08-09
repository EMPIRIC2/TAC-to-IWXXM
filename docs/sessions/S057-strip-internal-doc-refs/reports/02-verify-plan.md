# 02-verify-plan — Gate A (S057 / EV-048)

**Date**: 2026-08-08  
**Mode**: delta — F7 UI + F21 OpenAPI/error copy hygiene (#951)  
**Status**: Gate A PASS — `D-S057-gateA=1`  
**01**: completed (`D-S057-01-ac=1`; `D-S057-guard-s0=1`; UI preview `D-S057-ui-preview=1`)

## Inventory (touched)

| # | Document | Delta | Status |
|---|----------|-------|--------|
| 1 | feature-list.md | F7 / F21 EV-048 AC | audited |
| 2 | api-contract.md | Operator-facing OpenAPI/error copy policy | audited |
| 3 | user-journeys.md | UJ-055 | audited |
| 4 | test-plan.md | TC-EV048-001..005 | audited |
| 5 | evolve-decisions / requirements-decisions | EV-048 locks | reference |
| — | spec.md | No new component — `apps/frontend` + `apps/backend` already map | OK |
| — | deploy.md | N/A — no new env | OK |

## Consistency checklist

| Check | Result |
|-------|--------|
| Feature ↔ Spec | **PASS** — F7 frontend; F21 public API/OpenAPI |
| Feature ↔ Journey | **PASS** — UJ-055 |
| Journey ↔ Test | **PASS** — → TC-EV048-001..005 |
| Feature ↔ Test | **PASS** — AC1–6 ↔ TC-EV048-* |
| Feature ↔ API | **PASS** — api-contract policy section |
| Test ↔ Acceptance | **PASS** |
| Connectivity H4–H5 | **ADVISORY** — UJ-055 may be T0/T2 only; **10-e2e** on route; **12/13 waived** |

## Statements

### High (auto-approved — D-S057-01-ac=1 / Phase 0 locks)

| ID | Statement | Verdict |
|----|-----------|---------|
| S1.1 | No `[Corpus:]` / ADR / EV / S0 / `docs/` cites in operator UI strings | auto-approved |
| S1.2 | Same for public OpenAPI descriptions + client-facing errors | auto-approved |
| S1.3 | Guard patterns include `\bS0\d+\b` (`D-S057-guard-s0=1`) | auto-approved |
| S1.4 | Comments, tests, standing docs remain allowed | auto-approved |
| S1.5 | UJ-055 + TC-EV048-001..005 define verification | auto-approved |
| S1.6 | Standard route; 12/13 waived unless 11 requires deploy | auto-approved |

### Medium (user review → 04 deliverables)

| ID | Statement | Notes |
|----|-----------|-------|
| S2.1 | FE “string catalogs” = explicit module list (e.g. `operatorHelp`, SoftPreview, privacy, examples) scanned by Vitest | Inventory in 04 — recommend accept |
| S2.2 | OpenAPI scan via FastAPI `app.openapi()` (or equivalent export) in backend unit test | Recommend accept |
| S2.3 | T3 Playwright for UJ-055 only if UI audit finds visible hits; else T0/T2 unit guard sufficient | Recommend accept (matches AC) |
| S2.4 | Allowlist empty at start; add only on proven domain false positives | Recommend accept |

### Low

| ID | Statement | Notes |
|----|-----------|-------|
| S3.1 | Lint-issue catalog `source` attribution may mention external WMO URLs — not ADR/Corpus; out of guard unless it embeds planning IDs | Advisory — keep out of scope unless leak found |

## Contradictions

None blocking. Soft-preview UI copy already clean; OpenAPI `description=` still leaks ADRs (in scope for 07).

## Gate A recommendation

**PASS** — accept S2.1–S2.4 as 04/07 work; S3.1 advisory.

## Gate A decision (`D-S057-gateA=1`)

User chose **option 1**: PASS; S2.1–S2.4 as 04/07 defaults; proceed **04-tech-plan**.

| Item | Locked for 04/07 |
|------|------------------|
| S2.1 | FE string catalog inventory in 04 |
| S2.2 | OpenAPI scan via `app.openapi()` |
| S2.3 | T3 only if UI audit finds visible hits |
| S2.4 | Allowlist empty until proven false positive |
| S3.1 | Lint catalog external URLs OOS unless planning IDs leak |

## Next

**04-tech-plan**.
