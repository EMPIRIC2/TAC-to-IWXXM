# 02-verify-plan — S019 / EV-014 (delta)

**Date**: 2026-07-21  
**Mode**: delta / evolve  
**Status**: in_progress — inventory + consistency done; medium/low review pending  
**PR**: https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/753

## Phase 1 — Document inventory (delta scope)

| # | Document | Path | Delta sections | Statements | Status |
|---|----------|------|----------------|------------|--------|
| 1 | Feature List | `docs/feature-list.md` | F16–F19; Non-Goals S008/F7/S019; F8 bullet | 14 | reviewing |
| 2 | Spec | `docs/spec.md` | BYO/dissemination; F8 non-goals; F16–F19; Component Overview | 8 | reviewing |
| 3 | User Journeys | `docs/user-journeys.md` | UJ-027–030 | 6 | reviewing |
| 4 | Test Plan | `docs/test-plan.md` | Scope; journey matrix; TC-F16..F19; H4–H5 gate | 10 | reviewing |
| 5 | ADR-021 | `docs/adr/ADR-021-…` | Destination-paste amendment | 3 | reviewing |
| 6 | ADR-029 | `docs/adr/ADR-029-…` | SSRF + allowlist (Proposed) | 4 | reviewing |
| 7 | Requirements decisions | `docs/decisions/requirements-decisions.md` | EV-014 table | reference | skip audit |
| 8 | Evolve decisions | `docs/decisions/evolve-decisions.md` | EV-014 intake | reference | skip audit |

**Deferred (01 → 04):** api-contract, config-spec, env-contract, dependency-inventory,
writer-contract DDL, wis2box service shape.

## Phase 4 — Embedded consistency (F16–F19)

| Check | Result | Notes |
|-------|--------|-------|
| Feature ↔ Spec | **Pass*** | F16–F19 section present; *Component Overview still omits dissemination (S-EV014-M1) |
| Feature ↔ Journey | **Pass** | UJ-027–030 |
| Journey ↔ Test | **Pass** | TC-F16..F19 mapped |
| Feature ↔ Test | **Pass** | Acceptance ↔ TCs |
| Spec ↔ Config | **Deferred** | `DISSEMINATION_EGRESS_ALLOWLIST` → 04 (S-EV014-L1) |
| Test ↔ Acceptance | **Pass*** | *F19 live bar ambiguous vs Q15 (S-EV014-M2) |
| Cross-doc naming | **Pass** | drawer / BYOC / wis2box / allowlist consistent |
| Scope boundaries | **Fail → review** | F8 detail still lists AMHS/push sinks as non-goals (C-EV014-1) |
| Template `static+api+worker` | **Pass** | No new deployable; H4–H5 called out for FE/API |
| Connectivity | **Pass*** | UJ claim H6′; harness H6 text not yet expanded (S-EV014-M3) |

## Auto-approved (high confidence)

Derived from `requirements-decisions.md` EV-014 / F16–F19 table + locked intake Q5–Q24.

| ID | Document | Statement (abbrev) | Source |
|----|----------|-------------------|--------|
| S1.H1 | feature-list F16 | One-shot URI; memory-only; no saved profiles | F16-R1 / Q5=A |
| S1.H2 | feature-list F16 | Supabase Auth stays deploy BYO; no auth-key paste | F16-R2 / Q10A=D |
| S1.H3 | feature-list F16 | Drawer + URI + preflight; block Send until green | F16-R3 / Q6=B Q7=A |
| S1.H4 | feature-list F16 | DDL / create-if-missing vs writer contract | F16-R4 / Q20=A |
| S1.H5 | feature-list F16 | Convert-then-send **and** drag-drop | F16-R5 / Q20=B |
| S1.H6 | feature-list F16 | Engines: Postgres, MySQL/MariaDB, SQL Server, SQLite | F16-R6 / Q23=A–D |
| S1.H7 | feature-list F16 / ADR-029 | SSRF baseline + required allowlist (empty ⇒ deny) | F16-R7 / Q11=A+B |
| S1.H8 | feature-list F16 | F5 stays; never store destination secrets | F16-R8 / Q19=A |
| S1.H9 | feature-list F17 | Staging wis2box harness; live BYOC | F17-R1/R2 / Q12=B Q17 |
| S1.H10 | feature-list F18 | EDIS → RTH Washington; BYOC SMTP/gateway | F18-R1 / Q13=A Q18≈A |
| S1.H11 | feature-list F19 | AMHS/SWIM/AFS in same drawer (non-goals overturn) | F19-R1 / Q20=D |
| S1.H12 | feature-list / test-plan | Staging OK merge; live Postgres+WIS2+EDIS before close | R-close / Q15=A Q21=A |
| S1.H13 | Non-Goals S019 | No saved profiles; no Supabase auth paste; no free-form SQL admin | Q14 / Q10 / Q11 |
| S2.H1 | spec F16–F19 | Epic purpose + close gate + ADR refs | Phase 0 / 01 delta |
| S2.H2 | spec BYO | Destination paste allowed; ADR-021 amend | Q10 / ADR-021 |
| S2.H3 | spec F8 | Operator push sinks are F16–F19, not F8 auto-push | Q20 / Non-Goals amend |
| S3.H1–H4 | UJ-027–030 | Journeys match Fn scope + TC ids | 01 delta |
| S4.H1–H4 | TC-F16-001..004 | Preflight, SSRF, multi-DB+DDL, drag-drop | F16 acceptance |
| S4.H5–H6 | TC-F17-001..002 | Staging wis2box + live BYOC | F17 |
| S4.H7–H8 | TC-F18-001..002 | Format + live EDIS BYOC | F18 |
| S5.H1 | ADR-021 | Destination paste amendment; not Supabase auth keys | Q10 |
| S6.H1–H3 | ADR-029 | Backend-only egress; memory-only; fail-closed allowlist | Q11=A+B |

**Count:** 28 high-confidence auto-approved.

## Pending user review (medium / low / contradiction)

| ID | Conf | Category | Claim |
|----|------|----------|-------|
| C-EV014-1 | Low | `[Contradiction]` | F8 § still says non-goals include AMHS/SWIM/AFS + push sinks without F8-worker qualifier |
| S-EV014-M1 | Medium | Spec completeness | Component Overview / backend purpose omit dissemination drawer + preflight APIs |
| S-EV014-M2 | Medium | `[Ambiguity]` | F19 live demo “required or waive” vs evolve-decisions note including AMHS in close gate vs Q15=A (Postgres+WIS2+EDIS only) |
| S-EV014-M3 | Medium | Connectivity | H6 harness blurb does not yet list UJ-027–030 (journeys/TCs use H6′) |
| S-EV014-M4 | Medium | ADR hygiene | ADR-029 still **Proposed** though Q11 locked |
| S-EV014-L1 | Low | Spec ↔ Config | Allowlist env documented only in ADR/feature-list until 04 |

## Progress

- Auto-approved: 28
- Remaining for review: 5 medium/contradiction + 1 low
- Next: walk statements via AskQuestion (Q26+)
