# Routing plan — S047 / EV-039

**Preset:** Standard (+05 for B→C)  
**Route:** `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`  
**Skip:** `03-plan-tooling`, `06-tech-tooling` (revisit if teardown needs new hooks/deps inventory tooling)  
**Branch:** `evolve/EV-039-sql-ingest-live-e2e`  
**Features:** deepen **F16** (no new Fn expected)  
**Status:** in_progress — **13-deploy-smoke** evidence green (`D-S047-resume`=2); awaiting `D-S047-13`  
**Approved:** 2026-08-06 (chat intake `1,1,1,1,2`); resumed 2026-08-08  

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 00-context | yes | scoped | **completed** | S047 open; D-S047-open |
| 16-evolve | yes | orchestrator | **in_progress** | EV-039; 13 pending sign-off |
| 01-requirements | yes | delta | **completed** | F16 deepen ACs + teardown; D-S047-ac |
| 02-verify-plan | yes | delta | **completed** | Gate A PASS (`D-S047-02-gate-a`=2); S02.M3 fixed |
| 03-plan-tooling | no | — | skipped | No new Cursor rules planned |
| 04-tech-plan | yes | delta | **completed** | `D-S047-04-plan`=1; execution-plan approved |
| 05-verify-tech | yes | delta | **completed** | Gate B PASS (`D-S047-05-gate-b`=1) |
| 06-tech-tooling | no | — | skipped | Unless new deps force inventory pass |
| 07-build | yes | full | **completed** | M1+M2 done |
| 08-verify-build | yes | delta | **completed** | PASS; Docker LIVE harness |
| 09-qa | yes | delta | **completed** | PASS + advisories; `reports/qa-report.md` |
| 10-e2e | yes | full | **completed** | H6′ 7/7 + LIVE 001/002/004; `reports/e2e-report.md` |
| 11-verify-impl | yes | delta | **completed** | `D-S047-11`=1 AC1–AC7 + SQL Server waive |
| 12-verify-deploy | yes | delta | **completed** | `D-S047-12`=1; checklist approved |
| 13-deploy-smoke | yes | delta | **in_progress** | #891 merged; CD 31130303373; H0c/H1/H4–H5 re-PASS 2026-08-08 |

## Skip rationale

| Skipped | Why |
|---------|-----|
| 03 | No new plan-adherence / SSRF rule expected (ADR-029/030 stand) |
| 06 | No new publishable dependency tooling; Compose uses existing images |

## Gates

| Gate | Result | When |
|------|--------|------|
| Phase 0 open | **PASS** (`D-S047-open`) | 2026-08-06 |
| A→B / 02 | **PASS** (`D-S047-02-gate-a`=2) | 2026-08-06 |
| B→C / 05 | **PASS** (`D-S047-05-gate-b`=1) | 2026-08-06 |
| C→D / 11 | **PASS** (`D-S047-11`=1) | 2026-08-06 |
| Deploy 12 | **PASS** (`D-S047-12`=1) | 2026-08-06 |
| Deploy 13 | evidence PASS | merge + CD + H0c/H1/H4–H5; awaiting `D-S047-13` |
