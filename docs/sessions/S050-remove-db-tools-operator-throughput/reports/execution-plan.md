# Execution plan — S050 / EV-042

**Preset:** Standard  
**Branch:** `evolve/EV-042-remove-db-tools-operator-throughput`  
**Features:** F33 (new); deepen F7, F16–F19  
**Issues:** [#897](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/897), [#898](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/898)  
**Corpus:** [Corpus: product §F7/F16–F19/F33], [Corpus: system-spec], [Corpus: api],
[Corpus: tests], [Corpus: tech-spec], [Corpus: decisions §EV-042], [Corpus: adr/ADR-029]

## Decisions locked for build

| ID | Choice |
|----|--------|
| D-S050-C1 | Global `MAX_REQUEST_BODY_BYTES` stays 2 MiB; mass route uses `MASS_INGEST_MAX_*` + route body ≥50 MiB |
| D-S050-ac | AC1–AC7 |
| R2 | Hide **all** operator dissemination destinations |

## Milestone M1 — Hide destinations UI (F16–F19 deepen)

| Task | Spec Source | Depends On | Status | Data Deps |
|------|-------------|------------|--------|-----------|
| T1.1 | Hide/disable Convert&Send + DisseminationDrawer sink entry in `FileConverter`; no sink chooser for operators | [Corpus: product] AC1; UJ-053; feature-list F16–F19 deepen | — | **completed** | |
| T1.2 | Vitest/Playwright: destinations absent; Convert/Validate remain | TC-EV042-001; UJ-053 | T1.1 | **completed** | |
| T1.3 | Confirm harness still hits `/dissemination/preflight`+`/send` (no API delete) | AC2; TC-EV042-002 | — | **completed** | |

## Milestone M1 notes

- Flag: `apps/frontend/src/utils/operatorDisseminationUi.ts` → `OPERATOR_DISSEMINATION_DESTINATIONS_ENABLED=false`
- `DatabaseUploadDialog` / Upload to Database left visible (Phase 0)
- Operator Playwright UJ-027–030 + F16 live SQL UI skipped until #898; DisseminationDrawer Vitest + package tests retained
- Dissemination package: 143 passed (engine docker errors env-local, unrelated to UI hide)

## Milestone M2 — F33 secure mass ingest (API + FE)

| Task | Spec Source | Depends On | Status | Data Deps |
|------|-------------|------------|--------|-----------|
| T2.1 | Env: `MASS_INGEST_MAX_FILES/FILE_BYTES/TOTAL_BYTES`; route body limit; `.env.example` + env-contract | D-S050-C1; [Corpus: tech-spec] | — | **completed** | |
| T2.2 | `POST /api/v1/ingest/mass` — JWT required; multipart files and/or zip; sniff + zip-bomb; per-file results | [Corpus: api]; AC4–AC5; TC-F33-001..004 | T2.1 | **completed** | |
| T2.3 | FE: folder (`webkitdirectory`) + zip picker; auth gate; progress toast; queue handoff | UJ-051; AC4 | T2.2 | **completed** | |
| T2.4 | Unit/integration tests for caps, sniff, zip-bomb, 401/403 | TC-F33-001..004 | T2.2 | **completed** | |

## Milestone M2 notes

- API: `apps/backend/src/routers/mass_ingest.py` + `services/mass_ingest.py`; body limit via abuse_controls D-S050-C1
- FE: Folder/Zip controls on compact drop zone; JWT gate; toast progress; accepted → `pendingFiles`
- Tests: TC-F33 guards (unit) + auth route tests; Vitest guest auth gate + zip handoff
- Queue/keyboard/batch polish remains M3 (T3.1–T3.3)

## Milestone M3 — Operator churn UX (F7 deepen)

| Task | Spec Source | Depends On | Status | Data Deps |
|------|-------------|------------|--------|-----------|
| T3.1 | Result/work queue UI + keyboard next/prev + Enter convert/validate | AC3; UJ-052 | T1.1 | **completed** | |
| T3.2 | Multi-select batch convert + batch validate (no disseminate) | AC3; R4 | T3.1 | **completed** | |
| T3.3 | Wire mass-ingest successes into queue; Vitest/Playwright TC-EV042-003..004 + TC-F33-005 | AC3/AC6; UJ-051/052 | T2.3, T3.2 | **completed** | |

## Milestone M3 notes

- Sticky work queue with focus ring; ↑/↓ + Enter convert + Shift+Enter lint validate
- Multi-select Batch Convert / Batch Validate (no disseminate)
- Mass ingest already hands accepted items into `pendingFiles` (T2.3); Vitest TC-EV042-003 + helpers
- Playwright H4–H5 for mass route deferred to M4

## Milestone M4 — Verify / connectivity / docs close

| Task | Spec Source | Depends On | Status | Data Deps |
|------|-------------|------------|--------|-----------|
| T4.1 | H4–H5 smoke for new mass route + FE URLs | AC6; connectivity-gates | M1–M3 | **completed** | |
| T4.2 | Update test-plan TC details if needed; ops note destinations deferred | [Corpus: tests] | T4.1 | **completed** | |
| T4.3 | 08–13 per Standard routing | routing-plan | T4.1 | **in_progress** (08 local PASS @ 05893ccb; CI watch) | |


## Proposed tech defaults (pending AskQuestion)

| Topic | Recommendation |
|-------|----------------|
| Zip | Server unpacks zip on mass route; client expands `webkitdirectory` to files before upload | **approved** |
| Auth | Reuse F31 JWKS JWT gate (`utilities/security.py`) on mass route only | **approved** |
| ADR | No new ADR — document in api-contract + env-contract; amend ADR-031 abuse controls note if needed | **approved** |
| Rate limit | New `RATE_LIMIT_MASS_INGEST_PER_MIN` (default 10) separate from public/dissemination | **approved** |
| Dependencies | Prefer stdlib `zipfile` + existing content-type checks; no new PyPI dep unless AskQuestion | **approved** |

## Gate notes

- A→B: Gate A PASS (D-S050-gate-a)
- B→C: 05-verify-tech after this plan approved
- C→D: 08 + tests green before 09–13

## PR Plan

| PR | Scope | Status | URL |
|----|-------|--------|-----|
| Minor (M1–M3) | Hide destinations UI; F33 mass ingest; work queue/batch | **open** | https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/899 |
| M4 follow-up | H4–H5 / 09–13 close | pending | — |
