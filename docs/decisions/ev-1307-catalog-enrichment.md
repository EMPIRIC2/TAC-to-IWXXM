# EV-1307 / #1308 — Decoding + Conversion catalog enrichment

**Session:** `EV-1307-epic-rules-catalog-quality-operator-trust-ux-qua`  
**Date:** 2026-09-29  
**Tickets:** epic [#1307](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1307) ·
Build slice [#1308](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1308)  
**Corpus:** [Corpus: product §F7.v] [Corpus: product §F9] [Corpus: api]
[Corpus: journeys] [Corpus: tests] [Corpus: adr/ADR-044]

## Goal (this cycle)

Decoding and Conversion `rule-catalogs` rows carry type, optional level, source/conform,
and readable Conversion descriptions so the Validation Issues Catalog is as trustworthy
for those families as TAC/IWXXM lint.

## Locked decisions

| ID | Choice |
|----|--------|
| D-REQ-01 | New journey **UJ-080** |
| D-REQ-02 | Decoding `issue_type` = EV-062 set; prefer `content` for glossary TAC codes; FE never invents |
| D-REQ-03 | Optional `severity`; null if not lint-like |
| D-REQ-04 | `source_*` + optional `conform_note`; best-effort public sources; null when unverified |
| D-REQ-05 | Family-specific type enums (conversion: `profile` \| `policy` \| `other`) |
| D-REQ-08 | 1–3 sentence Conversion descriptions per semantic profile |
| D-REQ-09 | Best-effort shrink decoding `other`; count remainder |
| D-REQ-10 | T0 + T2; defer H4–H5 unless breaking wire |
| D-REQ-11 | AC approved as written |
| D-REQ-12 | No `policy` rows this cycle — profiles use `issue_type=profile` |

## Acceptance

- [x] Decoding `rule-catalogs` additive metadata (null allowed; FE does not invent)
- [x] Conversion readable summaries + `issue_type=profile` for semantic profiles
- [ ] Family-aware catalog type filter UI
- [ ] UJ-080 + TC-EV1308-001..004
- [x] Remaining decoding `other` count recorded
- [ ] TAC/IWXXM lint-issue-catalog unchanged; EV-048 clean
- [x] PR into `stage` (M1–M2 via #1309; M3 follows on same branch)

### Decoding `issue_type` census (Build M2, 2026-09-29)

From `tac_decoding.catalog.count_issue_types()` on packaged glossary:

| issue_type | count |
|------------|------:|
| content | 44 |
| null | 8 |
| other | **0** |

Nulls are function-word / marker tokens (`AND`, `OF`, …) that must not auto-default.

## Out (sibling epic children)

Profile-only checkbox · console→lint deep links · conversion-params wiring · ToS ·
quality-metrics UI/CI · dissemination content fill · vendor-sync CI

## Standing docs touched

- `docs/feature-list.md` (F7.v / F9 deepen)
- `docs/api-contract.md` (`rule-catalogs` field table)
- `docs/user-journeys.md` (UJ-080)
- `docs/test-plan.md` (TC-EV1308-*)
- `docs/spec.md` (catalog export note)

## Tech plan lock (2026-09-29)

| ID | Choice |
|----|--------|
| D-TP-01 | Conversion descriptions in `tac2iwxxm` data map/YAML |
| D-TP-02 | Decoding sidecar `catalog_meta.yaml` + merge in `catalog_entries()` |
| D-TP-03 | Family=All type filter = EV-062 ∪ `{profile,policy}` (+ `other`) |
| D-TP-04 | M1 DTO → M2 decoding → M3 conversion → M4 FE; branch `evolve/1308-catalog-enrichment` → `stage` |
| D-TP-05 | No new deps / env / CORS; H4–H5 deferred unless wire breaks |

**Verify-tech clarifications (2026-09-29):**
- Classifier default `content` only for `_OFFICIAL_TOKENS` minus function words (`AND`, `OF`, …)
- Size M / ~8h accepted; OpenAPI regen via existing project path

Full execution plan: session `reports/tech-plan.md`.
