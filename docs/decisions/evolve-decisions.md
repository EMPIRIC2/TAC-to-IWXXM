# Evolve Decisions

> Standing log of approved evolve-cycle scope and product decisions.
> Cycle metadata also recorded in `workflow-state.yaml` §`evolve_cycles`.

## Cycle EV-033 — F8 worker INGEST_POLLER_URL hardening (S041)

**Session**: S041-worker-poller-hardening  
**Features**: deepen **F8**  
**Started**: 2026-08-04  
**Branch**: `evolve/EV-033-worker-poller-hardening` (from `main`)  
**Status**: **in_progress**  
**Prior**: S040 / EV-032 **suspended** (not cancelled) during this cycle

### Scope (Phase 0 — locked 2026-08-04; AskQuestion unavailable — user “proceed 1–5”)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E33-1 | decision | Session vs S040? | New session S041; suspend S040 |
| E33-2 | decision | Scope? | All prevention items **1–5** + worker code refuse placeholder/non-https |
| E33-3 | decision | Preset? | **Standard** |

**Scope (verbatim)**: Harden F8 `metar-worker` so `INGEST_POLLER_URL` cutover cannot
leave `REPLACE_ME_*` or non-HTTPS values running at replicas &gt; 0: (1) fail-closed
scale default/preflight; (2) CI/ops validate script; (3) pin non-prod fixture URL in
docs/env; (4) runbook — do not copy unverified Render poller URLs; (5) CrashLoop check
+ optional PrometheusRule; plus code `validate_ingest_poller_url` / exit 2 on bad URL.

**Out of scope**: Completing S040/EV-032 deploy smoke; new operational ingest source
beyond the fixture URL; Prometheus operator install on DOKS.

### Intake decisions
| ID | Category | Question | Decision | ADR |
|----|----------|----------|----------|-----|
| E33-1 | decision | Proceed hardening 1–5? | Yes (+ code guard) | ADR-018 deepen |

### Stage log
| Stage | Completed | Notes |
|-------|-----------|-------|
| 00-context | 2026-08-04 | S041 open; S040 suspended |
| 16-evolve | | orchestrating |
| 01–13 | | Standard path — docs+code+scripts this cycle |

## Cycle EV-032 — Official IWXXM corpus quality / WMO source parity (S040)

**Session**: S040-iwxxm-corpus-quality  
**Features**: **F32** (new — VONA quality bar) + deepen **F23** (#835) + **F4** / **F6** / **F2** / **F13** (#808 + corpus)  
**Issues**: [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) (epic), [#835](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/835), [#741](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/741), [#808](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/808)  
**Started**: 2026-08-04  
**Branch**: `evolve/EV-032-iwxxm-corpus-quality` (from `main`)  
**Status**: **in_progress** — Gate A PASS; entering 04-tech-plan

### Scope (Phase 0 — locked 2026-08-04 via 00-context)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E32-1 | decision | Umbrella ticket? | **1** — new Epic **#846** (`D-S040-open` Q1) |
| E32-2 | decision | Cycle scope? | **1** — #835 + #741 + #808 + corpus/WMO-source track |
| E32-3 | decision | VONA Fn? | **1** — allocate **F32** VONA quality bar |
| E32-4 | decision | Order? | **1** — #835 → #741 → #808 → corpus |
| E32-5 | decision | Routing preset? | **1** — Standard (`D-S040-route`) |
| E32-6 | decision | Branch base? | **1** — cut from `main`; park EV-031 dirt in stash (`D-S040-branch`) |

**Scope (verbatim)**: Under epic #846, raise and prove quality against the official WMO IWXXM
corpus and related WMO sources (wmo-im/iwxxm, iwxxm-translation, iwxxm-codelists,
codes.wmo.int, iwxxm-modelling). Execute (1) #835 TC SIGMET A6-2-TC ADR-032 equality →
`wmoPass`; (2) #741 / **F32** VONA lint→convert→validate quality bar; (3) #808 adopt-new-line
maintainability assessment + checklists (no re-pin in-ticket); (4) file corpus parity
children under #846 as discovered. Exclude #836 metrics UI / #840 workbench epic.

**Out of scope**: Metrics UI #836; hand-edit `vendor/schemas/*` outside sync PRs; ship a new
IWXXM pin inside #808; unrelated platform/dissemination/DOKS work.

**Parked**: `stash@{0}` — S039/EV-031 WIP (`S039-EV031-WIP park for S040/EV-032`).

### Document Manifest (01 — locked 2026-08-04)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E32-M1 | decision | Spec delta breadth? | **2** — Full product pack: `feature-list` + `spec` + `user-journeys` + `api-contract` + `test-plan` (+ domain/#808 notes) (`D-S040-E32-M`) |
| E32-M2 | decision | VONA operator exposure? | **3** — **Full F7 product surface** this cycle (picker + Examples/catalog when quality path green) |
| E32-M3 | decision | UI preview (interview)? | **1** — N/A for interview (implement UI in-cycle; H4–H5 at verify/deploy) |
| E32-M4 | decision | After manifest? | **1** — write deltas; close 01 → **02-verify-plan** |

**Affected artifacts (01)**: `docs/feature-list.md`, `docs/spec.md`, `docs/user-journeys.md`,
`docs/api-contract.md`, `docs/test-plan.md`, `docs/decisions/evolve-decisions.md`,
`docs/context/iwxxm-corpus-quality-846.md` (pointer); #808 deliverables remain docs under
`docs/domain/iwxxm/` in later milestones.

### Gate A / 02 (locked 2026-08-04)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E32-02F | decision | 02 Batch F? | **1,1,1,1** — VONA AHL→04; incremental Examples unlock; #808 docs+children only (+#847); Gate A (`D-S040-02-batch-f` / `D-S040-02-phase-a`) |
| E32-02A | gate | Gate A / 02 close? | **PASS** — start **04-tech-plan** |
| E32-02-M1 | decision | VONA AHL / T1T2? | **1** — defer detail to 04 (“when known”) (`S02.M1`) |
| E32-02-M2 | decision | Examples unlock? | **1** — incremental when F32 golden greens (`S02.M2`) |
| E32-02-M3 | decision | #808 depth? | **1** — docs + child issues only; link #847 for non-technical review (`S02.M3`) |

**Audit**: `docs/sessions/S040-iwxxm-corpus-quality/reports/02-verify-plan-audit.md`

### Tech plan Batch 1 (04 — locked 2026-08-04)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E32-T1 | decision | Milestone structure? | **1** — M0–M4 (`D-S040-04-batch-1`) |
| E32-T2 | decision | #835 equality bar? | **1** — strict ADR-032 required for `wmoPass` |
| E32-T3 | decision | F32 encode approach? | **1** — cookbook + fixtures; VAA/SWXA-peer plugin; gaps → children |
| E32-T4 | decision | VONA AHL / T1T2? | **1** — discover in M2; no provisional lock |

### Tech plan Batch 2 (04 — locked 2026-08-04)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E32-T5 | decision | New deps? | **1** — none (`D-S040-04-batch-2`) |
| E32-T6 | decision | Deploy / connectivity? | **1** — API+static; H1–H3; **H4–H5 required** |
| E32-T7 | decision | CI packaging? | **custom** — path-filtered **pre-commit** smokes; long packs on **pre-push**/`make`; document improvements (not dump full matrices into default pre-commit) |
| E32-T8 | decision | Corpus / #847 home? | **1** — M0 session inventory + durable `docs/domain/iwxxm/` |

### Gate B (04 — locked 2026-08-04)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E32-T9 | gate | Approve execution plan? | **PASS** — M0–M4 (28 tasks) → **07 @ T0.1** (`D-S040-04-plan`=1) |

**Status**: **in_progress** — Phase C build (`07-build`); M1 #835 **closed**; next M2 F32 @ T2.1

---

## Cycle EV-030 — Quality residuals #831 / #829 / #820 (S037)

**Session**: S037-quality-residuals-831  
**Features**: **F29** (new — rule matrices) + deepen **F23** / **F12** / **F2** / **F13** / **F9** / **F26** / **F27**  
**Issues**: [#831](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/831), [#829](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/829), [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820)  
**Started**: 2026-08-02  
**Branch**: `evolve/EV-030-quality-residuals-831`  
**Status**: **completed** — closed 2026-08-03 (`D-S037-13=1`); M4 done; #831/#829/#820 closed; #835 residual; live H1–H5 PASS (`8bd111c`)

### Scope (Phase 0 — locked 2026-08-02 via 00-context)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E30-1 | decision | Session open? | **1** — S037 / EV-030 feature + 16-evolve (`D-S037-open`) |
| E30-2 | decision | Residuals? | **1** — all three; order #831 → #829 → #820 |
| E30-3 | decision | Routing preset? | **1** — Standard (`00→16→01→02→04→07→08→09→10→11→12→13`; skip 03/05/06) |
| E30-4 | decision | UI preview? | **2** — docs/repo only (no non-deployed UI) |
| E30-5 | decision | Session type? | **1** — feature → 16-evolve |
| E30-6 | decision | Routing approve? | **1** — Standard path (`D-S037-route`) |
| E30-7 | decision | Fn allocation? | **1** — F29 + deepen F23/F12/F2/F13/F9/F26/F27 (`D-S037-fn`) |
| E30-8 | decision | Start 01? | **1** — start 01-requirements |
| E30-9 | decision | Commit open? | **1** — yes (`D-S037-fn` Q3) |
| E30-M | decision | Document Manifest? | **2,1** — lean + API/catalog note for #829; close 01 → 02 (`D-S037-E30-M`) |
| E30-02F | decision | 02 Batch F? | **1,1,1,1** — M1/M2/M3/L1 approve (`D-S037-02-batch-f`) |
| E30-02A | gate | Gate A / 02 close? | **PASS** — start **04-tech-plan** (`D-S037-02-phase-a`) |
| E30-T1 | decision | Milestone structure? | **1** — M0–M4 (`D-S037-04-batch-1`) |
| E30-T2 | decision | #831 case storage? | **1** — YAML/JSON under testdata + pytest load |
| E30-T3 | decision | Rule inventory SoT? | **1** — unified index → matrix slots |
| E30-T4 | decision | #829 catalog unlock? | **1** — unlock when quality path green (ADR-032) |
| E30-T5 | decision | New deps? | **2** — PyYAML OK if needed → **reuse** `tac2iwxxm` pyyaml; no new dep (`D-S037-04-batch-2`) |
| E30-T6 | decision | Deploy / connectivity? | **1** — API redeploy; H1–H3; H4–H5 for FE catalog unlock |
| E30-T7 | decision | F29 CI? | **1** — PR smoke subset + optional full-matrix marker/job |
| E30-T8 | decision | Harness doc + home? | **1** — session design note + `tests/quality_matrices/` |
| E30-T9 | gate | Gate B / plan approve? | **PASS** — approve M0–M4 (27 tasks) → **07 @ T0.1** (`D-S037-04-plan`) |
| E30-semver | decision | Bump `tac-validate` after T2.2 codes? | **1** — **no bump** (remain `0.1.1`); defer to M2/M4 close (`D-S037-semver-none`) |
| E30-semver-tac2iwxxm | decision | Bump `tac2iwxxm` after #820 decode deepen? | **2** — **patch** `0.2.3 → 0.2.4` (pyproject + Cargo + `__version__` + locks); no tags/PyPI (`D-S037-semver-tac2iwxxm`) |
| E30-ui-preview | decision | Non-deployed UI preview (FE unlock)? | **2** — decline; H4–H5 at 13 (`D-S037-ui-preview`) |
| E30-11 | decision | 11+12 signoff? | **1** — approve UJ-044 + F29 + deepen + start 13 (`D-S037-11` / `D-S037-12`) |
| E30-13 | decision | Close EV-030 / S037? | **1** — mark cycle + session complete (`D-S037-13`); leave #835 open |
| E30-T2.3 | decision | #829 STNR / exceptional geometry? | **OOS cite** for geometry beyond `WI … OF TC CENTRE`; **STNR in-cycle** via pack (`D-S037-T2.3-oos`; S02.M2) |
| E30-ui-preview | decision | Non-deployed UI preview after FE catalog unlock? | **2** — **decline** (written interview; AskQuestion unavailable); **H4–H5 still required at M4/13** (`D-S037-ui-preview`) |

**Scope (verbatim)**: Close EV-029 residuals — (1) #831 parameterized happy/sad/edge
matrices for lint/convert/validate with design-before-bulk-fixtures; (2) #829 TC SIGMET
tac-validate pack, STNR/geometry negatives or explicit OOS, A6-2-TC catalog/menu tier;
(3) #820 deepen VAA/TCA decode beyond F9 G4 best-effort. Work order #831 → #829 → #820.

**In:** Harness evaluation + pilot runners; TC SIGMET lint deepen + menu tier decision;
VAA/TCA structured decode residual shrink; CI/docs for matrix authoring.

**Out:** New deployables; #830 Supabase strip; #806 WIS2 mining; SIGWX/VONA/QVACI;
non-deployed UI preview this session (H4–H5 only if FE menu unlock ships).

### Acceptance (cycle)

1. **F29** / #831: harness recommendation + runners + pilot or explicit `needs-fixture` (**TC-F29-001..007**; **TC-EV030-001..003**).
2. #829: TC lint pack + STNR/geometry (or OOS) + A6-2-TC catalog tier (**TC-EV030-004/005**).
3. #820: VAA/TCA decode residual deepen (**TC-EV030-006**).
4. **UJ-044**; deploy smoke green or waived if no contract/FE change.

### Journeys / tests

- **UJ-044**; **TC-EV030-001..006**; **TC-F29-001..007**

---

## Cycle EV-029 — #823 Eight-family AHL / lint / convert / validate gap sweep (S036)

**Session**: S036-eight-family-ahl-rules-823  
**Features**: **F28** (new SWXA quality bar) + deepen **F6** / **F6.bulletin** / **F12** / **F2** / **F13** / **F15** / **F20** / **F23** / **F24** / **F26** / **F27**  
**Issues**: [#823](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/823) (umbrella); absorb [#738](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/738), [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820), [#740](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/740)  
**Started**: 2026-08-01  
**Branch**: `evolve/EV-029-eight-family-ahl-rules`  
**Status**: **completed** (2026-08-02) — T12.7 closeout; #823/#740 closed; PR #828 @ `4e6577a`; smoke PASS

### Scope (Phase 0 — locked 2026-08-01)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E29-1 | decision | Session open? | **1** — S036 / EV-029 feature + 16-evolve (`D-S036-open`) |
| E29-2 | decision | Work shape? | **1** — Phase A mine/promote first, then Phase B per product family |
| E29-3 | decision | Product order? | **1** — Bulletin/AHL/COM → METAR → SPECI → TAF → SIGMET (gen/VA/TC/CNL) → AIRMET → VAA → TCA → SWXA |
| E29-4 | decision | Dissemination AHL? | **1** — shared AHL + filename/`bulletinIdentifier` in-cycle; sink UI later |
| E29-5 | decision | Routing preset? | **1** — Standard (`00→16→01→02→04→07→08→09→10→11→12→13`; skip 03/05/06) |
| E29-6 | decision | UI preview? | **1** — N/A (no UI this session) |
| E29-7 | decision | Fn allocation? | **1** — F28 new + deepen set (`D-S036-fn`) |
| E29-8 | decision | Related issues? | **1** — absorb #738 / #820 / #740 into Phase B |
| E29-9 | decision | Proceed? | **1** — lock → start 01-requirements |
| E29-10 | decision | Commit session open? | **1** — yes (`D-S036-fn` Q4) |
| E29-M | decision | Document Manifest? | **2** — lean + amend API contract for `product=swxa` (`D-S036-E29-M`) |
| E29-E1 | decision | Close 01 → 02? | **1** — mark 01 completed; start **02-verify-plan** |
| E29-02F | decision | 02 Batch F? | **1,1,1,1** — M1/M2/M3/L1 approve (`D-S036-02-batch-f`) |
| E29-02A | gate | Gate A / 02 close? | **PASS** — start **04-tech-plan** (`D-S036-02-phase-a`) |
| E29-T1 | decision | Milestone structure? | **3** — one milestone per product (METAR/SPECI/TAF separate) (`D-S036-04-batch-1`) |
| E29-T2 | decision | AHL model home? | **1** — extend `tac2iwxxm` bulletin/AHL; dissemination imports (`D-S036-04-batch-1`) |
| E29-T3 | decision | Phase A mining? | **2** — full re-mine all eight families before Phase B (`D-S036-04-batch-1`) |
| E29-T4 | decision | CI packaging? | **2** — separate workflow per family (`D-S036-04-batch-1`) |
| E29-T5 | decision | New deps? | **1** — none; AskQuestion per new dep (`D-S036-04-batch-2`) |
| E29-T6 | decision | Deploy / smoke? | **1** — API redeploy; H1–H3; H4–H5 waive unless FE (`D-S036-04-batch-2`) |
| E29-T7 | decision | SIGMET milestones? | **1** — gen / VA / TC as three Ms (`D-S036-04-batch-2`) |
| E29-T8 | decision | Kill-switch? | **1** — HARD; block → AskQuestion (`D-S036-04-batch-2`) |
| E29-T9 | gate | Plan approve / Gate B? | **1** — approve M0–M12; → **07 @ T0.1** (`D-S036-04-plan`) |
| E29-semver | decision | Publishable semver after M2? | **1** — `tac2iwxxm` only **0.1.1 → 0.2.0** (pyproject + Cargo); no tags/PyPI (`D-S036-semver-minor`) |
| E29-semver-patch | decision | Publishable semver after M6 T6.2? | **2** — `tac2iwxxm` only **0.2.0 → 0.2.1** (pyproject + Cargo + `__version__`); no tags/PyPI (`D-S036-semver-patch`) |
| E29-semver-patch-2 | decision | Publishable semver after M9 T9.2? | **2** — `tac2iwxxm` only **0.2.1 → 0.2.2** (pyproject + Cargo + `__version__`); no tags/PyPI (`D-S036-semver-patch-2`) |
| E29-semver-patch-3 | decision | Publishable semver after M10? | **2** — `tac2iwxxm` only **0.2.2 → 0.2.3** (pyproject + Cargo + `__version__`); no tags/PyPI (`D-S036-semver-patch-3`) |
| E29-11 | gate | 11-verify-impl? | **2,1,1,1** — no UI preview; approve UJ-043 + F28 + deepen (`D-S036-11`) |
| E29-12 | gate | 12-verify-deploy? | **1,1,1** — mitigations + rollback + READY for T12.6 (`D-S036-12`); H4–H5 **required** (FE Examples unlocked; amends E29-T6 waive) |
| E29-13 | gate | 13-deploy-smoke / T12.6? | **1** — approve smoke → T12.7 (`D-S036-13`); close #823/#740; residuals #829/#820/#831 |
| E29-close | decision | T12.7 closeout? | **1** — evolve summary + `docs/evolve-report-EV-029.md`; F28 Done |

**Scope (verbatim)**: Go 1-by-1 across the eight TAC→IWXXM product families and ensure
validation, linting, and conversion rules (plus examples for all TAC input shapes) have no
silent gaps. Umbrella #823 — mine then implement IWXXM 2025-2 AHL/bulletin, VAA/TCA, and
three-SIGMET family gaps. Report states: Normal / Amendment / Correction / Cancellation /
Missing or NIL where permitted. Exclude SIGWX / VONA / QVACI as converter inputs.

**In:** Phase A domain mine + promote + example inventory; Phase B engine deltas product-by-product;
shared AHL/`T1T2`/filename model for tac2iwxxm + dissemination consumers; child issues for residuals.

**Out:** SIGWX/VONA/QVACI TAC conversion; dissemination drawer/sink UI; #806 WIS2 topic mining;
hand-edits to `vendor/schemas/*`; GIFTs-as-normative.

### Acceptance (cycle)

1. Coverage matrix + canonicals filled or child-issued for eight families × lint/convert/IWXXM-validate × report states × TAC shapes (**TC-EV029-001/006**).
2. Example inventory covers TAC shapes + IWXXM peers (**TC-EV029-002**).
3. Shared AHL/`T1T2`/BBB model enforced; filename/`bulletinIdentifier` ready for F16–F19 (**TC-EV029-003**).
4. TC SIGMET → `iwxxm:TropicalCycloneSIGMET` (#738) (**TC-EV029-004**).
5. VAA/TCA #823 B4 / #820 residuals closed or child-issued (**TC-EV029-005**).
6. **F28** SWXA quality bar green or deferred with child (**TC-F28-***).
7. Phase B product-order smoke green (**TC-EV029-007**); #823 closable or children linked.

### Journeys / tests

- **UJ-043**; **TC-EV029-001..008**; **TC-F28-001..006**

---

## Cycle EV-028 — #781 EMPIRIC2 Codecov purge + PyPI Trusted Publisher + landing pages (S035)

**Session**: S035-empiric2-ops-leftovers-781  
**Features**: none (general ops cycle; deepens F12–F14 publish path only)  
**Issues**: [#781](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/781)  
**Started**: 2026-08-01  
**Branch**: `evolve/EV-028-empiric2-ops-leftovers-781`  
**Status**: **completed** (2026-08-01) — PR [#824](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/824) @ `70312dd`; #781 closed

### Scope (Phase 0 — locked 2026-08-01)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E28-1 | decision | Session type? | **1b** — feature + 16-evolve / EV-028 (`D-S035-open`) |
| E28-2 | decision | Scope? | **2a** — Codecov purge + Trusted Publisher + landing READMEs; out e2e/load secrets, Render rename, Supabase Site URL, #777 publish |
| E28-3 | decision | Landing packages? | **3b** — three public + `packages/dissemination/README.md` polish |
| E28-4 | decision | OIDC proof? | **4b** — configure + tag publish |
| E28-5 | decision | Routing? | **5a** — Lean+build (`D-S035-routing`) |
| E28-6 | decision | Which packages to bump? | **6b** — all three → `0.1.1` |
| E28-M | decision | Document Manifest? | **7a** — lean set (`D-S035-E28-M`) |
| E28-E1 | decision | Close 01 → 02? | **8a** — mark 01 completed; start **02-verify-plan** (`D-S035-E28-E1`) |
| E28-S2.1 | decision | UJ-023 vs 0.1.1? | **9a** — minimal UJ-023 amend |
| E28-02 | decision | Gate A? | **10a** — PASS → **04-tech-plan** |
| E28-T2 | decision | Tag timing? | **11b** — tag from evolve branch before merge |
| E28-04 | decision | Gate B? | **12a** — approve plan → **07-build** @ T0.1 |
| E28-14d | decision | Cosmetic `0.1.3` vs T3.4? | **1** — skip `0.1.3`; T3.4 smoke @ `iwxxm-validate==0.1.2`; defer `__version__` string (`D-S035-14d`) |

**Scope (verbatim)**: Finish #781 leftovers — remove Codecov from product CI/docs/secrets;
point PyPI Trusted Publishers at `EMPIRIC2/TAC-to-IWXXM` + `pypi-publish.yml`; prove OIDC by
publishing `tac-validate`, `iwxxm-validate`, and `tac2iwxxm` `0.1.1`; rewrite public package
landing READMEs (and dissemination README) so PyPI/library consumers do not need internal
ADR / Feature / E10 identifiers.

**In:** Codecov purge; Trusted Publisher cutover; `0.1.1` tag publishes ×3; consumer-facing
README + `pyproject.toml` `description` cleanup for the three published packages + dissemination
README polish (not published this cycle).

**Out:** optional e2e/load Actions secrets; Render hostname rename; Supabase Site URL; publishing
`iwxxm-dissemination` (#777).

**Unblocks:** #777 packaging work (Trusted Publisher path proven under EMPIRIC2).

### Acceptance (cycle)

1. CI on branch/`main` green without Codecov steps; repo secret `CODECOV_TOKEN` deleted; `.codecov.yml` removed.
2. PyPI Trusted Publisher for each of `tac-validate`, `iwxxm-validate`, `tac2iwxxm` uses Owner `EMPIRIC2`, Repository `TAC-to-IWXXM`, Workflow `pypi-publish.yml`, Environment `pypi`.
3. Tags `tac-validate-v0.1.1`, `iwxxm-validate-v0.1.1`, `tac2iwxxm-v0.1.1` → `pypi-publish.yml` green; versions visible on PyPI.
4. Public READMEs (three packages + dissemination) and published `description` fields have no required ADR / Fn / E10 references for a library consumer.
5. #781 closable for Codecov + PyPI leftovers.

### Document Manifest (approved — E28-M / 7a)

| Document | Delta |
|----------|--------|
| `docs/decisions/evolve-decisions.md` | This cycle section |
| `docs/deploy.md` | Trusted Publisher owner/repo; note `0.1.1` proof |
| `docs/config-spec.md` | Tag pattern beyond first `0.1.0`; EMPIRIC2 publisher |
| `docs/test-plan.md` | TC-EV028-001..003 (Codecov absent; Trusted Publisher; `0.1.1` publish) |
| `docs/feature-list.md` | F12–F14 note: subsequent tags via EMPIRIC2 OIDC; landing pages consumer-facing |
| Package READMEs + `description` | Build stage (07) |

Skip this cycle: Spec architecture rewrite, API contract, user-journeys (UJ-023 reused), new ADR (deploy/config delta only).

### Stage log

| Stage | Completed | Notes |
|-------|-----------|-------|
| 00-context | 2026-08-01 | S035 open |
| 01-requirements | 2026-08-01 | E28-M / E28-E1 |
| 02-verify-plan | 2026-08-01 | Gate A PASS; UJ-023 amend |
| 04-tech-plan | 2026-08-01 | Gate B PASS; E28-T2=11b |
| 07-build | 2026-08-01 | M0–M3 complete; PR #824 merged |
| 08-verify-build | 2026-08-01 | T3.1 PASS |
| 10-e2e | 2026-08-01 | T3.2 packaging smoke PASS |
| 13-deploy-smoke | 2026-08-01 | OIDC publishes + T3.4 install smoke PASS |

---

## Cycle EV-027 — Official WMO decode residual matrix (#815) (S034)

**Session**: S034-wmo-decode-residual-matrix  
**Features**: Deepen **F25** / **F9** / **F7.g** — no new Fn  
**Issues**: [#815](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/815) (**closed**); child [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820) (**open**)  
**Started**: 2026-07-31  
**Completed**: 2026-07-31 (`D-S034-EV027-phase4-close`)  
**Branch**: `evolve/EV-027-wmo-decode-residual-matrix`  
**PR**: [#821](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/821) → `ad36aa0`  
**Closeout**: [#822](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/822) → `9ff0157`  
**Status**: **completed**  

### Scope (Phase 0 — locked 2026-07-31)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E27-1 | decision | Session + scope? | **1** — S034 / EV-027; #815 inventory + residual matrix + CI (`D-S034-open=1`) |
| E27-2 | decision | Routing? | **1** — Lean+build `00→16→01→02→04→07→08→10` (+13 when ships) |
| E27-3 | decision | UI preview now? | **2** — no; proceed from docs/repo; re-offer after build |
| E27-4 | decision | Residual triage? | **1** — fix decode in-cycle when cheap; else allowlist + child issue (no silent leftovers) |
| E27-M | decision | Document Manifest? | **1** — lean: feature-list + UJ-042 + test-plan TC-EV027 + decisions; skip Spec/Config/API/Deploy (`D-S034-E27-M`) |
| E27-UJ | decision | Journey id? | **1** — new **UJ-042**; deepen UJ-039 / UJ-020 |
| E27-TC | decision | TC ids? | **1** — new **TC-EV027-001..005** |
| E27-E1 | decision | Close 01 → 02? | **1** — mark 01 completed; start **02-verify-plan** (`D-S034-E27-E1`) |
| S02.M1 | decision | Allowlist SoT? | **1** — package test artifact; FIXTURE_GAPS = catalog/load only (`D-S034-EV027-s02m1-1`) |
| S02.M2 | decision | Gate C residual bar? | **2** — all seven target empty; allowlist only if standing docs say intentional (F9 G4 / ADR-025) + child issue (`D-S034-EV027-s02m2-2`) |
| S02.L1 | decision | Inventory SoT? | **1** — pytest-discovered vendor/mirrored peers (`D-S034-EV027-s02l1-1`) |
| E27-02 | decision | Gate A / 02 close? | **PASS** — Batch F 1,2,1; Lean → **04-tech-plan** (`D-S034-02-phase-a`) |
| E27-T1 | decision | Build order? | **2** — catalog completeness first, then residual matrix (`D-S034-E27-T-batch`) |
| E27-T2 | decision | Decode fix grain? | **1** — one commit per product family / theme |
| E27-T3 | decision | New deps? | **2** — AskQuestion per new dep (prefer none) |
| E27-T4 | decision | Gate C? | **1** — matrix + catalog∪gaps + #815/children required (no soft escape) |
| E27-T5 | decision | Draft plan? | **1** — M0–M3 as written (catalog-first order) |
| E27-04 | decision | Gate B? | **1** — approve → **07-build** @ T0.1 (`D-S034-04-plan-approve`) |
| E27-GC | decision | Gate C / PR? | **1** — push + PR to main; close #815 on merge; link #820; waive TC-EV027-005 / 13 (`D-S034-gate-c`) |
| E27-13 | decision | 13-deploy-smoke? | **waived** — no FE deploy this cycle |
| E27-merge | decision | Merge #821? | **1,1** — merge green tip `eb3ffe3`; leave local tip for closeout (`D-S034-merge`) → merged `ad36aa0` |
| E27-P4 | decision | Phase 4 close? | **1** — merge #822 + close EV-027 / S034 (`D-S034-EV027-phase4-close`) |

**Scope (verbatim)**: Every in-scope official WMO IWXXM TAC peer from the vendor pin is
loadable from the workbench sample menu (or explicitly deferred in `FIXTURE_GAPS`) and
decode leaves no residuals unless on a documented expected-residual allowlist; unexpected
residuals fail CI.

**In:** inventory SoT; load-path parity; decode residual matrix; parametrized CI; child
issues for stems that cannot close in-cycle.

**Out:** inventing TAC; `wmoReference`→`wmoPass` encode equality; IWXXM-US in WMO menu;
new products beyond F6 seven; deferred SWX/VONA/WAFS/QVACI / TC-SIGMET A6-2 unless already
catalogued.

**Supersedes:** S029 / EV-022 (parked) narrow SIGMET A6-1a residual work — broadened by #815.

---

## Cycle EV-026 — #809 VA multi-location ADR-032 equality / wmoPass (S033)

**Session**: S033-va-multi-location-equality  
**Features**: Deepen **F23** / **F6** / **F7.g** — no new Fn  
**Issues**: [#809](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/809)  
**Started**: 2026-07-31  
**Branch**: `evolve/EV-026-va-multi-location-equality`  
**Status**: **completed** — #817 merged `101f555`; 13 PASS; closed 2026-07-31  
**Closeout PR**: [#818](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/818)

### Scope (Phase 0 — locked 2026-07-31)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E26-1 | decision | Session + cycle? | **1** — S033 / EV-026; #809 equality only (`D-S033-open=1`) |
| E26-2 | decision | Depth / AC? | **1** — ADR-032 equality under defaults → catalog `wmoPass` → close #809 |
| E26-3 | decision | Routing? | **1** — Lean+build `00→16→01→02→04→07→08→10` (+13 when ships) |
| E26-4 | decision | Out-of-scope? | **1** — no US REMARKS reopen; no #738 |
| E26-ui | decision | UI preview? | **N/A** — catalog/Vitest only |
| E26-M | decision | Document Manifest? | **1** — lean: feature-list + UJ-041 + test-plan 008/009 + decisions; skip Spec/Config/API/Deploy (`D-S033-E26-M`) |
| E26-TC | decision | TC ids? | **1** — reuse TC-EV025-008..009 with strict/`wmoPass` semantics (`D-S033-E26-TC`) |
| E26-E1 | decision | Close 01 → 02? | **1** — mark 01 completed; start **02-verify-plan** (`D-S033-E26-E1`) |
| S02.M1 | decision | Example stamps? | **1** — calendar / ATS–MWO stamps OK for this stem (`D-S033-EV026-s02m1-1`) |
| S02.M2 | decision | Geometry normalize? | **1** — ring order + coord format toward vendor for this stem (`D-S033-EV026-s02m2-1`) |
| S02.L1 | decision | New UJ? | **1** — deepen UJ-041 only (`D-S033-EV026-s02l1-1`) |
| E26-02 | decision | Gate A / 02 close? | **PASS** — Batch F 1,1,1; Lean → **04-tech-plan** (`D-S033-02-phase-a`) |
| E26-T1 | decision | Build order? | **1** — dig → red → encoder themes → green → catalog → verify/close (`D-S033-E26-T-batch`) |
| E26-T2 | decision | Encoder grain? | **1** — one commit per blocker theme then equality green |
| E26-T3 | decision | New deps? | **2** — AskQuestion per new dep (prefer none) |
| E26-T4 | decision | Gate C? | **1** — equality + `wmoPass` + #809 closed required (no soft escape) |
| E26-T5 | decision | Draft plan? | **1** — plan as written |
| E26-04 | decision | Gate B? | **1** — approve M0–M3 → **07-build** @ T0.1 (`D-S033-04-plan-approve`) |
| E26-817 | decision | Merge #817? | **1** — merge to main (`D-S033-817-merge`) |
| E26-13 | decision | Run 13? | **1** — optional 13 after merge (`D-S033-13-start`) |
| E26-13p | decision | 13 results? | **PASS** — H0c–H5 + catalog + VA convert (`D-S033-13-smoke-pass`) |
| E26-close | decision | Phase 4 close? | **1** — approve deploy + close S033/EV-026 (`D-S033-EV026-phase4-close`) |

**Scope (verbatim)**: Residual from EV-025 soft path — make
`canonicalize_xml(convert(sigmet-multi-location-VA.tac))` equal vendor XML under annex3 +
default pin (ADR-032); promote TC/catalog to `wmoPass`; close #809.

**In:** encoder deltas for known blockers (calendar stamp, ATS/MWO metadata, ring order,
coord format, phenomenonTime); strict golden flip; catalog + FIXTURE_GAPS; issue close.

**Out:** #810–#812 reopen; #738 TC SIGMET A6-2; sample-menu removal.

### Fn allocation (approved)

| Fn | Role |
|----|------|
| Deepen **F23** | VA multi-location convert equality |
| Deepen **F6** | annex3 encode shape |
| Deepen **F7.g** | Catalog tier `wmoPass` (ADR-032) |

### Routing (approved)

Lean+build + **13 when ships**: `00→16→01→02→04→07→08→10` (+ `13` if API behavior ships).

---

## Cycle EV-025 — iwxxm-us REMARKS encode + VA multi-location (#810–#812 + #809) (S032)

**Session**: S032-iwxxm-us-remarks-va  
**Features**: Deepen **F6** / **F6.b** / **F12** / **F2** / **F13** + deepen **F23** (#809) — no new Fn  
**Issues**: [#810](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/810), [#811](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/811), [#812](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/812) **closed**; [#809](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/809) **open** (soft done)  
**Started**: 2026-07-31  
**Completed**: 2026-07-31  
**Branch**: `evolve/EV-025-iwxxm-us-remarks-va`  
**PR**: [#816](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/816) merged `2412312`  
**Status**: **completed** — Phase 4 close (`D-S032-EV025-phase4-close`); #809 equality → next cycle

### Phase 4 close (2026-07-31)

| ID | Category | Decision |
|----|----------|----------|
| D-S032-EV025-phase4-close | gate | **1** — Close EV-025/S032 after #816 merge; waive T7.3/13; hand #809 equality to new SNNN/EV |
| D-S032-EV025-809-handoff | decision | Soft path closed in #816; residual ADR-032 equality / `wmoPass` is **new** deepen (not Lane A reopen) |

**Report**: `docs/evolve-report-EV-025.md` · `docs/sessions/S032-iwxxm-us-remarks-va/reports/evolve-summary.md` · [Context: va-multi-location-809](../context/va-multi-location-809.md)

### Scope (Phase 0 — locked 2026-07-31)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E25-1 | decision | Session + bundling? | **1** — S032 / EV-025; #810+#811+#812 in one cycle |
| E25-2 | decision | Depth / AC? | **1** — full ticket AC (lint as needed + encode + goldens + validate smoke; US-only) |
| E25-3 | decision | Routing? | **1** — Lean+build `00→16→01→02→04→07→08→10` (+13 when ships); skip 03/05/06/09/11/12 |
| E25-4 | decision | Out-of-scope? | **2+3** clarified → see E25-4b / E25-4c |
| E25-4b | ambiguity | #809 + adjacent? | **2** — **dual lane**: US pack + #809 VA multi-location same cycle |
| E25-4c | decision | Adjacent US breadth? | **3** — **all remaining ❌ US types** from dig checklist |
| E25-ui | decision | UI preview? | **1** — N/A (no UI this session) |
| E25-M | decision | 01 Document Manifest? | **2** — lean delta + **new UJ-040/041**; deepen UJ-010/026/034/039; skip Spec/Config/API/Deploy |
| E25-E1 | decision | Close 01 → 02? | **1** — mark 01 completed; start **02-verify-plan** (`D-S032-E25-E1`) |
| S02.M1 | decision | #809 soft→strict? | **1** — soft-compare first; `wmoPass` only when ADR-032 equality holds (`D-S032-EV025-s02m1-1`) |
| S02.M2 | decision | Dig ❌ residuals? | **1** — aim close all in-cycle; soft child-issue deferral **superseded by E25-T5=3** (encode residual blocks Gate C) (`D-S032-EV025-s02m2-1` → `D-S032-EV025-t5-3`) |
| S02.L1 | decision | SCH deferrals? | **1** — TC-EV025-010 may document SCH deferrals without blocking Lane A goldens (`D-S032-EV025-s02l1-1`) |
| E25-02 | decision | Gate A / 02 close? | **PASS** — Batch F 1,1,1; Lean → **04-tech-plan** (`D-S032-02-phase-a`) |
| E25-T1 | decision | Milestone order? | **1** — M0→#810→#811→#812→adjacent→#809 soft→strict→validate→Gate C (`D-S032-EV025-t1-1`) |
| E25-T2 | decision | Golden grain? | **1** — encode (+lint) per dig type/row where feasible (`D-S032-EV025-t2-1`) |
| E25-T3 | decision | New deps? | **2** — AskQuestion per new dep (prefer none) (`D-S032-EV025-t3-2`) |
| E25-T4 | decision | Dual-lane sequencing? | **1** — finish Lane A then Lane B (`D-S032-EV025-t4-1`) |
| E25-T5 | decision | Dig ❌ residuals / Gate C? | **3** — any encode residual **blocks Gate C**; supersedes S02.M2 soft deferral (`D-S032-EV025-t5-3`) |
| E25-T6 | decision | Draft plan? | **1** — draft execution plan from T1–T5; Gate B next (`D-S032-EV025-t6-1`) |
| E25-04 | decision | Gate B / plan approve? | **1** — M0–M7 approved; B→C → **07-build** @ T0.1 (`D-S032-04-plan-approve`) |

**Scope (verbatim)**:
Dual-lane engine cycle from EV-024 children: (A) encode/lint/golden/validate all ❌
iwxxm-us METAR/SPECI REMARKS types from the #773 dig (named #810/#811/#812 plus full
adjacent checklist); (B) #809 WMO `sigmet-multi-location-VA` annex3 golden soft→strict.
US never enters WMO sample menu. No USWX, no vendor hand-edits, no #808.

**In:**
- #810 Variable RVR / meanRVR withheld
- #811 Lightning / VisuallyObservablePhenomena (+ related frequency/type)
- #812 SnowIncrease + sensor outage remarks
- All other dig ❌/still-⚠ US extension types (WindShift, sky/convective, hail, sector,
  obscuration, second-site/tower, variable CIG/SKY/VIS, max/min temps, ProcessedProperty,
  Addendum residuals, codelist hrefs, …)
- #809 `sigmet-multi-location-VA` package golden + catalog tier promote only under ADR-032

**Out:**
- USWX; vendor schema hand-edits; US in WMO menu; #808; #738 TC SIGMET; roadmap products

### Fn allocation (approved)

| Fn | Role |
|----|------|
| Deepen **F6** / **F6.b** | RMK → iwxxm-us encode + US goldens |
| Deepen **F12** | US REMARKS tac-validate / registry as needed |
| Deepen **F2** / **F13** | Combined catalog / extension-block validate smoke |
| Deepen **F23** | #809 VA multi-location convert golden |

### Routing (approved)

Lean+build + **13 when ships**: `00→16→01→02→04→07→08→10` (+ `13` if API behavior ships).

## Cycle EV-024 — IWXXM domain mine (#804 + #807 + #773) (S031)

**Session**: S031-iwxxm-domain-mine  
**Features**: Deepen **F6** / **F2** / **F4** / **F12** / **F13** / **F25** (+ **F6.b** US map via #773) — no new Fn  
**Issues**: [#804](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/804), [#807](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/807), [#773](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/773) — **exclude** [#806](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/806)  
**Started**: 2026-07-30  
**Branch**: `evolve/EV-024-iwxxm-domain-mine`  
**Status**: **completed** (2026-07-30) — PR #813 `864783e`; 13-deploy-smoke PASS; `D-S031-merge-close`

### Scope (Phase 0 — locked 2026-07-30)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E24-1 | decision | Session open? | **1a+Build** — open feature session via 00-context; Lean+build path |
| E24-2 | decision | Issue set? | **2b** — #804 + #807 + #773 (IWXXM-US/MDL in same cycle) |
| E24-3 | decision | Depth / deliverables? | **3a** — full ticket acceptance: mining notes + relevancy/examples matrices + in-scope fixture/catalog wiring + durable doc promotions + child engine issues |
| E24-4 | decision | Routing preset? | **4b** — Lean+build `00→16→01→02→04→07→08→10`; skip 03/05/06/09/12; **11** optional; **13** when catalog/API ships |
| E24-x | decision | Exclude? | **#806** — F8/F17 WIS2 lane (user locked) |
| E24-ui | decision | Non-deployed UI preview? | **UIb** — No; proceed from docs/repo only (2026-07-30); re-offer at 11 if catalog ships |
| E24-M | decision | 01 Document Manifest? | **M3** — lean delta + **new UJ-039** (not only deepen UJ-036); skip Spec/Config/API/Deploy |
| E24-C | decision | Catalog / fixture policy? | **C3+C2+C1 hybrid** — discovery + validate/CI wire + **WMO IWXXM examples loadable from sample menu**; strict `wmoPass` vs WMO reference tiers; ADR-032 amend; encode gaps → child issues (do not block menu listing) |
| E24-E1 | decision | Close 01 → 02? | **1** — mark 01 completed; start **02-verify-plan** |
| S02.M1 | decision | Catalog reference field? | **1** — defer to **04**; prefer `wmoReference?: boolean` (`D-S031-EV024-s02m1-1`) |
| S02.M2 | decision | Which stems in sample menu? | **1** — product-in-scope + TAC peers; SWX/VONA/WAFS/QVACI deferred (`D-S031-EV024-s02m2-1`) |
| S02.L1 | decision | Vitest catalog policy? | **1** — amend tests in **07** for pass **or** reference (`D-S031-EV024-s02l1-1`) |
| E24-02 | decision | Gate A / 02 close? | **PASS** — Batch F 1,1,1; Lean → **04-tech-plan** (`D-S031-02-phase-a`) |
| E24-T1 | decision | Milestone order? | **1** — M0→#804→#807→#773→promote→catalog→validate→children/smoke |
| E24-T2 | decision | Badge UX? | **1** — “WMO passer” vs “WMO reference”; no new route |
| E24-T3 | decision | New deps? | **2** — AskQuestion per new dep (prefer none) |
| E24-T4 | decision | Mine parallelism? | **2** — sequential M1→M2→M3 |
| E24-T5 | decision | Approve plan → 07? | **1** — M0–M7 approved; B→C → 07 @ T0.1 |

**Scope (verbatim)**:
Domain mine (strongest bundle): deep IWXXM/ tree ingest (#804) vs org-level sibling refresh
for encode/validate (#807), plus IWXXM-US / MDL (#773). Same archetype as #800 prep —
discovery-first; child engine tickets later. Full ticket acceptance (3a). Keep #806 out.
**Operator ask (E24-C)**: WMO IWXXM examples must be loadable from the sample menu (UJ-039).

**In:**
- #804 folder-by-folder relevancy + official examples matrix + wire in-scope stems
- #807 org/sibling refresh (iwxxm family + lineage; skip WIS2)
- #773 METAR/SPECI PDF + modelling coverage checklist + RULE_SOURCE_URLS / COVERAGE_MATRIX
- Sample menu: official WMO stems with TAC peers (strict passer **or** WMO reference)
- Promote durable findings; file child issues for ❌/⚠ encode/lint/SCH gaps

**Out:**
- #806 WIS2; new product encode engines this cycle; hand-edit vendor schemas; USWX;
  mixing US examples into WMO catalog; committing PDF/full clones;
  translation-failed as happy-path Examples

### Fn allocation (approved)

| Fn | Role |
|----|------|
| Deepen **F6** / **F6.b** | Convert goldens + US RMK→iwxxm-us map from #773 (wiring/docs; engine gaps → children) |
| Deepen **F2** / **F13** | Validate fixtures / Schematron relevancy from package `rule/` + examples |
| Deepen **F4** | Pin vs tip drift notes; version-aware example surfaces |
| Deepen **F12** | Lint citation / registry rows where mining promotes durable TAC rules |
| Deepen **F25** / **F7.g** | Expand sample menu (UJ-039) + strict vs reference tiers (ADR-032 amend) |

### Routing (approved)

Lean+build + **13 when ships**: `00→16→01→02→04→07→08→10` (+ `13` if catalog/API ships).  
Build skills: `mine-domain-sources`, `extract-pdf-to-repo`.

### Docs updated in 01 (delta)

| Doc / area | Delta |
|------------|-------|
| `docs/feature-list.md` | S031 deepen; EV-023 → Done |
| `docs/user-journeys.md` | **UJ-039** + UJ-036 deepen |
| `docs/test-plan.md` | TC-EV024-001..008 |
| `docs/adr/ADR-032-*.md` | Catalog gate amend (strict vs reference) |
| `docs/decisions/requirements-decisions.md` | EV-024 table |
| `docs/domain/mining/*` | (07-build) New notes for #804/#807/#773 + README index |
| Frontend fixtures | (07-build) `examplesCatalog` / `FIXTURE_GAPS.md` |

---

## Cycle EV-023 — APAC FAQ + codes + WMO-306 encode/validate deltas (#800) (S030)

**Session**: S030-apac-encode-validate  
**Features**: Deepen **F6** / **F2** / **F12** / **F13** (no new Fn)  
**Issues**: [#800](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/800) (supersedes #797 implementation backlog; continues optional QA from #798/#719)  
**Started**: 2026-07-30  
**Branch**: `evolve/EV-023-apac-encode-validate`  
**Status**: **in_progress** (Phase A — **01-requirements**)

### Scope (Phase 0 — locked 2026-07-30)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E23-1 | decision | Feature allocation? | **A** — deepen **F6 + F2 + F12** (+ **F13** SCH as needed); no new Fn; `cycle_type: general` |
| E23-2 | decision | Scope this cycle? | **All ticket backlog items** (P0 + P1 + actionable P2) — see verbatim scope; exclude Out-of-scope section + #740/#741 |
| E23-3 | decision | Routing? | **A** — Lean+build `00→16→01→02→04→07→08→10`; skip 03/05/06/09/12; **11 optional** |
| E23-4 | decision | Deploy? | **B** — include **13-deploy-smoke** when convert/validate behavior ships |
| E23-ui | decision | Non-deployed UI preview? | **N/A** — engine + goldens; no new UI surface |
| E23-park | decision | Prior cycle? | **D-S029-park** — cancel/park EV-022 (F9 decode) to prioritize #800 |
| E23-E1 | decision | Close 01 → 02? | **1** — mark 01 completed; start **02-verify-plan** |
| S02.M1 | decision | translationCentre wire? | **1** — defer Form field name to **04**; default omit locked |
| S02.M2 | decision | COLLECT P2 depth? | **1** — F16–F19/bulletin hooks only; not full dissemination re-epic |
| S02.L1 | decision | Informative suite CI? | **1** — pytest marker; job wiring in **04** |
| E23-02 | decision | Gate A / 02 close? | **PASS** — Batch F 1,1,1; Lean → **04-tech-plan** (`D-S030-02-phase-a`) |
| E23-T1 | decision | Milestone order? | **1** — M0→P0→P1→P2→smoke |
| E23-T2 | decision | translationCentre wire? | **1** — Form `emit_translation_centre` + optional designator/name |
| E23-T3 | decision | New deps? | **2** — AskQuestion per new dep (prefer none) |
| E23-T4 | decision | Informative suite CI? | **2** — marker in main CI as **soft/xfail** |
| E23-T5 | decision | Kill-switch? | **1** — AskQuestion; no silent defer HARD P0 |
| E23-T6 | decision | Approve plan → 07? | **1** — M0–M7 approved; B→C → 07 @ T0.1 |

**Scope (verbatim)**:
Implement encode / lint / Schematron / fixture deltas from completed mining (#800) under
runtime SoT `vendor/manifest.json` → IWXXM **v2025-2**. Digs are done — engine + goldens only.

**P0:** NSC vs layered cloud (FAQ §14.3); missing WX / Guidance nils (`common/nil` vs `iwxxm/nil`);
`translationFailedTAC` quarantine (no partial translate; no operational TAC-in-XML-comments;
attr matrix vs official `*-translation-failed.xml`).

**P1:** codes.wmo.int dual-register colour + dual nil encode policy (offline vendor RDF/CSV);
iwxxm-translation Amd79-80-2023 METAR/TAF/VAA/TCA TAC → our 2025-2 as **informative**
(XSD+SCH; no 2023-1 XML byte-match); `translationCentre*` emit only for cross-State /
Translation Centre use (default in-State omit or config-gate).

**P2 (actionable this cycle):** SIGMET FIR / “S OF” → polygon helpers coordinated with #738 /
F23 geometry; COLLECT / multi-version namespaces as dissemination/bulletin work (F16–F19)
with convert SoT remaining single-report; optional #798/#719 encode QA if gaps survive
defer-to-latest; confirm coverage matrix / conversion citations after P0/P1.
**Not in cycle:** #740 SWX / #741 VONA / QVA; PDF remine; AMHS/FTBP ops; replacing Annex 3 /
vendor XSD with FAQ; 2019/upd-2021 as equal-weight SoT; `.local/` binaries; SAF/runway-state
under 2025-2.

### Fn allocation (approved)

| Fn | Role |
|----|------|
| Deepen **F6** | Encode correctness (NSC, nils, translationFailedTAC, translationCentre gate, FIR polygon helpers, COLLECT hooks as needed) |
| Deepen **F2** / **F13** | SCH/XSD negative fixtures + dual-register / nil policy tests |
| Deepen **F12** | Lint tighten beyond research `NSC_PRESENT` if needed; registry codes |
| Coord **F16–F19** / **#738** | COLLECT namespaces; SIGMET geometry — implement helpers here, full product bars stay on those tickets |

### Routing (approved)

Lean+build + **13 when behavior ships**: `00→16→01→02→04→07→08→10` (+ `13` if API/convert ships).

---

## Cycle EV-021 — VAA + TCA quality bars (#736 / #737) (S027)

**Session**: S027-vaa-quality  
**Features**: **F26** (VAA quality #736) + **F27** (TCA quality #737) + deepen **F6.f** / **F12** / **F7.g**  
**Issues**: [#736](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/736) (VAA), [#737](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/737) (TCA)  
**Started**: 2026-07-29  
**Branch**: `evolve/EV-021-vaa-quality`  
**Status**: **in_progress** (Phase C — **07-build** @ T1.1; M0 done)

### Scope (Batch 1 — locked 2026-07-29)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E21-1 | decision | Product encode scope? | **2** — VAA #736 **and** TCA #737 this cycle (assign **F26** + **F27**) |
| E21-2 | decision | WMO golden bar? | **1** — strict **`canonicalize_xml`** equality under **default** convert settings (`profile=annex3`, pinned 2025-2) for vendor goldens |
| E21-3 | decision | UI Examples catalog? | **1** — only list VAA/TCA examples that pass the golden bar; hide non-passers; **research/dig WMO IWXXM examples** (vendor + translation package) |
| E21-4 | decision | Routing + lock? | **1** — Lean+build+11 (`00→16→01→02→04→07→08→10→11→13`); lock Phase 0 → **01-requirements** |
| E21-ui | decision | Non-deployed UI preview? | **No** (default) — docs/repo only unless re-asked |
| E21-D1 | decision | Document Manifest? | **2** — all recommended (feature-list + AC + journeys/tests + coverage + ADR note + api + config) |
| E21-D2 | decision | Journeys / tests? | **1** — **UJ-037** VAA + **UJ-038** TCA; TC-F26-001..006 / TC-F27-001..006; deepen UJ-032 / TC-F7-008 |
| E21-D3 | decision | Matrix themes? | **1** — VAA **V1–V3+C1**; TCA **T1–T3+C1** |
| E21-D4 | decision | Translation-package fixtures? | **1** — mine TAC themes into accept/negatives; no Amd79 XML byte-match under 2025-2 |
| E21-E1 | decision | Close 01 → 02? | **1** — mark 01 completed; start **02-verify-plan** |

**Scope (verbatim)**:
Raise VAA (`iwxxm:VolcanicAshAdvisory`) and TCA (`iwxxm:TropicalCycloneAdvisory`) to the
F15/F20/F23/F24 quality bar: registry-backed lint, WMO vendor TAC→IWXXM
`canonicalize_xml`-equal under defaults (`va-advisory-A7-2`, `tc-advisory-A2-2`),
XSD+Schematron round-trip, exceptional-rule accept/negative fixtures from #736/#737
tables + guidance, F7.g catalog only for passers. Mine WMO examples from
`vendor/schemas/iwxxm/2025-2/IWXXM/examples/` and
`vendor/schemas/iwxxm-translation/Amd79-80-2023/{volcanic-ash,tropical-cyclone}-advisory/`.
Do not conflate with VA SIGMET (#739) or TC SIGMET (#738). OOS: SWX #740, VONA #741,
PyPI bumps, non-default profile/version golden equality, treating `*-translation-failed`
as happy-path golden.

### Fn allocation (approved)

| Fn | Title | Role |
|----|-------|------|
| **F26** | VAA quality bar | #736 lint/convert/validate/goldens/matrix |
| **F27** | TCA quality bar | #737 lint/convert/validate/goldens/matrix |
| Deepen **F6.f** | VAA + TCA plugins | Encode fidelity to vendor shapes |
| Deepen **F12** | tac-validate | ADR-028 registry codes for VAA/TCA |
| Deepen **F7.g** | Examples catalog | Only WMO-passing VAA/TCA demos |

### Routing (approved)

**Required:** 00 → 16 → 01 → 02 → 04 → 07 → 08 → 10 → 11 → 13  
**Skipped:** 03, 05, 06, 09, 12 (re-add if 04 introduces deps/ADR tooling)

### Research seed

See `docs/sessions/S027-vaa-quality/reports/wmo-vaa-tca-examples-inventory.md`.

### 02-verify-plan PASS (2026-07-29)

12 auto-approved; Batch F all **1** (S02.M1/M2/L1).  
Report: `docs/sessions/S027-vaa-quality/reports/02-verify-plan-audit.md`.  
Consistency: `spec.md` F24/F25 → Done; F26/F27 Planned (fixed in audit).

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| S02.M1 | ambiguity | Theme ids collide with F23 V1–V3? | **1** — keep F26 V1–V3 / F27 T1–T3 + mandatory “F26/F27 theme” prefix (`D-S027-EV021-s02m1-1`) |
| S02.M2 | decision | Catalog unlock cadence? | **1** — incremental per product (VAA when F26 greens; TCA when F27 greens) (`D-S027-EV021-s02m2-1`; peer E20-F4) |
| S02.L1 | uncertainty | CI packaging? | **1** — extend combined `wmo-quality.yml` with VAA+TCA; finalize in 04 (`D-S027-EV021-s02l1-1`) |
| D-S027-02-phase-a | gate | Phase A → 04? | **PASS** — Lean skip AskQuestion; start **04-tech-plan** |

### 04-tech-plan approved (2026-07-29)

Batch T all **1**. Report: `docs/sessions/S027-vaa-quality/reports/04-tech-plan.md`.  
Execution plan: `docs/sessions/S027-vaa-quality/reports/execution-plan.md`.

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E21-T1 | decision | Milestone order? | **1** — M0→VAA lint→VAA golden→TCA lint→TCA golden→catalog→smoke |
| E21-T2 | decision | Research depth? | **1** — close inventory; light dig |
| E21-T3 | decision | New deps? | **1** — none |
| E21-T4 | decision | Deploy/smoke? | **1** — redeploy; H1–H3 if API; H4–H5 when FE |
| E21-T5 | decision | Kill-switch? | **1** — AskQuestion if theme scope explodes |
| E21-T6 | decision | Approve plan → 07? | **1** — yes; skip 05/06; 07 @ T0.1 |

## Cycle EV-020 — AIRMET quality + WMO official golden parity + decode glossary (S026)

**Session**: S026-airmet-quality-wmo-examples  
**Features**: **F24** (AIRMET quality #731) + **F25** (WMO official golden parity METAR/SPECI/TAF + UI gate) + deepen **F9** / **F7.g** / **F6** / **F3** (lookup)  
**Issues**: [#731](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/731) (AIRMET); deepen prior quality bars for vendor example parity  
**Started**: 2026-07-29  
**Branch**: `evolve/EV-020-airmet-quality`  
**Status**: **in_progress** (Phase C — **07-build** @ T3.1; M0–M2 / A1–A4 done)

### Scope (locked 2026-07-29)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E20-1 | decision | WMO golden bar? | **A** — strict vendor equality via **`canonicalize_xml`** under **default** convert settings (clarified E20-D3; not alternate profiles/versions) |
| E20-2 | decision | Product encode scope? | **A=2** — AIRMET **and** METAR/SPECI/TAF official WMO examples to default golden equality this cycle (large) |
| E20-3 | decision | UI Examples catalog? | **A** — only list examples that pass the strict bar; remove/hide non-passers for in-scope products |
| E20-4 | decision | Decode glossary? | **B=2+3** — full 7-product plain-English token glossary + **OpenAIP/F3 names** where available + **extensible YAML/JSON registry** |
| E20-5 | decision | Routing preset (initial)? | Lean+build proposed → **amended C=1** |
| E20-6 | decision | UI preview now? | **No** — docs/repo only |
| E20-A | decision | Confirm encode scope after gap audit? | **2** — keep METAR+SPECI+TAF+AIRMET WMO byte-parity in this cycle |
| E20-B | decision | Glossary enrichment? | **2+3** — OpenAIP/F3 + operator-extensible registry |
| E20-C | decision | Routing amend? | **C=1** — Lean+build **+ 11-verify-impl** (`00→16→01→02→04→07→08→10→11→13`) |
| E20-8 | decision | Proceed? | **Yes** — Phase 0 locked; start **01-requirements** |
| E20-D1 | decision | 01 Document Manifest? | **2** — all recommended (acceptance + coverage + ADR + api-contract + config-spec) |
| E20-D2 | decision | Journeys / tests? | **1** — **UJ-035** AIRMET; **UJ-036** WMO catalog/METAR·SPECI·TAF; deepen UJ-020/032; TC-F24/TC-F25 |
| E20-D3 | decision | Golden compare rule? | **1** — `canonicalize_xml` equality (F23 pattern); **under default convert settings only** (`profile=annex3`, default pinned `iwxxm_version` e.g. 2025-2; no special flags) |
| E20-E1 | decision | TAF WMO cases? | **1** — both `taf-A5-1` and `taf-A5-2` |
| E20-E2 | decision | Glossary data? | **1** — package `decode_glossary.yaml` as **overrides**; prefer **official / near-official** sources (WMO codes / Annex cites / F3·OpenAIP) as primary augmentation |
| E20-E3 | decision | Close 01 → 02? | **Yes** |
| E20-F1 | decision | Milestone order? | **1** — Research → AIRMET lint → AIRMET golden → METAR/SPECI → TAF → glossary+catalog → smoke |
| E20-F2 | decision | Research depth? | **1** — full mining catalog AIRMET + METAR/SPECI/TAF → session research doc |
| E20-F3 | decision | CI? | **3** — combined `wmo-quality.yml` (SIGMET + AIRMET + METAR/SPECI/TAF packs) |
| E20-F4 | decision | FE Examples unlock? | **1** — incremental SIGMET-first until each product golden greens |

### 02-verify-plan PASS (2026-07-29)

18 auto-approved; Batch F all **1** (S02.M1/M2/L1/L2).  
Report: `docs/sessions/S026-airmet-quality-wmo-examples/reports/02-verify-plan-audit.md`.

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| S02.M1 | uncertainty | Include `taf-A5-2` as F25 golden? | **1** — yes (AMD/CNL peer; `D-S026-EV020-s02m1-1`) |
| S02.M2 | decision | ADR-032 status? | **1** — **Accepted** (`D-S026-EV020-s02m2-1`) |
| S02.L1 | ambiguity | Glossary env name? | **1** — `TAC2IWXXM_DECODE_GLOSSARY_PATH` (`D-S026-EV020-s02l1-1`) |
| S02.L2 | decision | Catalog unlock policy? | **1** — incremental (SIGMET-first until goldens green) (`D-S026-EV020-s02l2-1`) |
| D-S026-02-phase-a | gate | Phase A → 04? | **PASS** — Lean skip AskQuestion; start **04-tech-plan** |

### 04-tech-plan (approved 2026-07-29)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E20-F1 | decision | Milestone order? | **1** — Research → AIRMET lint → AIRMET golden → METAR/SPECI → TAF → glossary+catalog → smoke |
| E20-F2 | decision | Research depth? | **1** — full mining catalog |
| E20-F3 | decision | CI? | **3** — combined `wmo-quality.yml` |
| E20-F4 | decision | FE unlock? | **1** — incremental SIGMET-first |
| E20-F5 | decision | New deps? | **2** — PyYAML allowed if not usable transitively |
| E20-F6 | decision | Deploy/smoke? | **1** — redeploy; H1–H3 if API; H4–H5 required |
| E20-F7 | decision | Mid-build block? | **1** — AskQuestion kill-switch |
| E20-F8 | decision | Approve plan → 07? | **1** — yes; skip 05/06; 07 @ T0.1 |

Plan: `docs/sessions/S026-airmet-quality-wmo-examples/reports/execution-plan.md`.

### 07-build M2 close (2026-07-29)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| D-S026-T2.3-A | decision | Close F24 A1–A3? | **Close** — T2.1–T2.2 green; residuals (vendor MWO YUDD vs TAC YUSO; STNR motion) documented; A4 closed in T2.4 |

Plan: `docs/sessions/S026-airmet-quality-wmo-examples/reports/execution-plan.md`.

**Scope (verbatim)**:
Strict WMO vendor IWXXM golden equality via `canonicalize_xml` (2025-2) for AIRMET (#731) and
METAR/SPECI/TAF official examples this cycle **under default convert settings**. UI Examples
catalog only lists examples that pass that bar. Decode: official/near-official meanings + YAML
**overrides** + OpenAIP/F3 names when available. SIGMET already passes (F23) — keep green.
OOS unless added: TC SIGMET #738, new SWX/VONA quality bars, PyPI bumps.

### Fn allocation (approved)

| Fn | Title | Role |
|----|-------|------|
| **F24** | AIRMET quality bar | #731 lint/convert/validate/goldens/matrix (peer F15/F20/F23) |
| **F25** | WMO official example parity (METAR/SPECI/TAF) + UI gate | Vendor A3/A5 TAC→XML `canonicalize_xml` equality (defaults); catalog policy |
| Deepen **F9** | Decode glossary | Registry + 7-product meanings + summary |
| Deepen **F7.g** | Examples catalog | Only WMO-passing demos |
| Deepen **F6** | Encode fidelity | AIRMET + METAR/SPECI/TAF vendor shapes |
| Deepen **F3** | Name lookup | Optional airport/FIR names for decode when resolvable |

## Cycle EV-019 — SIGMET quality: general + VA (#733 / #739) (S025)

**Session**: S025-sigmet-quality  
**Features**: **F23** (Done) + deepen **F6.d** / **F12**  
**Issues**: [#733](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/733), [#739](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/739)  
**Started**: 2026-07-29  
**Completed**: 2026-07-29  
**Branch**: `evolve/EV-019-sigmet-quality`  
**PR**: [#792](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/792) **merged** (`afffe86`); API `dep-d9l11761egvs738ho3r0` + FE `dep-d9l1187avr4c739rfl10` live  
**Status**: **completed** (D-S025-close)

### Close (2026-07-29)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| D-S025-13-deploy-A | gate | Merge #792 + live smoke + close? | **A** — merge; H1–H5 + F23 catalog/lint/convert; close cycle |
| D-S025-close | gate | Close cycle + session? | **A** — commit/push closeout docs to `main` |

### Scope (Batch 1 — locked 2026-07-29)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E19-1 | decision | Open session? | **A** — `S025-sigmet-quality` → 16-evolve / EV-019; scoped context |
| E19-2 | decision | Product scope? | **A** — Full #733 + #739; #738 TC SIGMET OOS |
| E19-3 | decision | Fn allocation? | **A** — F23 (general+VA quality) + deepen F6.d/F12; ADR-028 reuse |
| E19-4 | decision | Routing preset? | **A** — Lean+build (`00→16→01→02→04→07→08→10→13`) |

### Scope (Batch 2 — locked 2026-07-29)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E19-5 | decision | Research / encode depth? | **A** — full #733/#739 AC (guidance + fixtures + goldens + matrix) |
| E19-6 | decision | Out of scope? | **A** — siblings OOS; no PyPI; no F16–F19; F7 Planned (smoke only) |
| E19-7 | decision | Deploy / smoke (13)? | **A** — redeploy if API/FE changes; H1–H3 if API; H4–H5 workbench sigmet + VA |
| E19-8 | decision | Proceed? | **B** — lock Phase 0; write F23; **pause before 01-requirements** |
| E19-ui | decision | Non-deployed UI preview? | **B** confirmed at 01 (E19-10=A — docs/repo only) |

### 01-requirements (locked 2026-07-29)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E19-9 | decision | Document manifest? | **A** — mandatory + coverage matrix + full API review + light plan-adherence |
| E19-10 | decision | UI reference preview? | **A** — docs/repo only |
| E19-11 | decision | Journey + TCs? | **A** — UJ-034; TC-F23-001..006 |
| E19-12 | decision | Matrix themes? | **A** — G1–G3 / V1–V3 / C1 |
| E19-13 | decision | VA product / API wire? | **A** — keep `product=sigmet`; content-selected `VolcanicAshSIGMET` root |
| E19-14 | decision | FE catalog? | **A** — no new FE filters; smoke only |

**01 complete** (user confirmed Continue → 02, 2026-07-29).  
**02-verify-plan PASS** (2026-07-29): 14 auto-approved; F21/F22 summary fix; medium all **1**
(S1.M1 full HARD + kill-switch; S6.M1 keep G1–G3 with prefix; S9.M1 skip 05).  
Report: `docs/sessions/S025-sigmet-quality/reports/02-verify-plan-audit.md`.

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| S1.M1 | uncertainty | Full themes under Lean+build? | **1** — HARD G1–G3/V1–V3/C1; 04 kill-switch (`D-S025-EV019-s1m1-1`) |
| S6.M1 | ambiguity | G1–G3 theme vs gate collision? | **1** — keep ids; prefix “F23 theme” vs “gate” (`D-S025-EV019-s6m1-1`) |
| S9.M1 | uncertainty | Skip 05? | **1** — keep skip; light pass at 04 exit (`D-S025-EV019-s9m1-1`) |
| D-S025-02-phase-a-A | gate | Phase A → 04? | **A** — Pass Gate A; start **04-tech-plan** (2026-07-29) |

### 04-tech-plan (in progress)

#### Batch 1 (locked 2026-07-29)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E19-15 | decision | Milestone order? | **A** — Research → G1–G2 lint → G3 goldens → V1–V2 → V3 → C1/matrix → smoke |
| E19-16 | decision | Research depth (M0)? | **B** — Full mining pass → `reports/sigmet-research-catalog.md` |
| E19-17 | decision | FE / catalog UI? | **B** — Add SIGMET/VA tag filters (**amends E19-14**) |
| E19-18 | decision | New deps? | **B** — AskQuestion per new dep (prefer none) |

**E19-14 amend**: Prior “no new FE catalog filters” superseded by **E19-17=B** for this cycle — additive catalog panel filters/copy for SIGMET (+ VA) tags; H4–H5 required after FE deploy.

#### Batch 2 (locked 2026-07-29)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E19-19 | decision | CI? | **B** — dedicated `.github/workflows/sigmet-quality.yml` |
| E19-20 | decision | Mining siblings? | **B+A** — dig SIGMET+VA; light sibling notes (cite-only) |
| E19-21 | decision | Deploy/smoke M5? | **A** — redeploy; H1–H3 if API; H4–H5 required |
| E19-22 | gate | Approve plan? | **A** — M0–M5 (~29 tasks); skip 05/06; B→C → **07 @ T0.1** (`D-S025-04-plan-approve-A`) |

**04 COMPLETE** — 04-exit consistency PASS; handoff **07-build** @ T0.1.

### 07-build (in progress)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| D-S025-16-continue | decision | Resume CONTINUE? | Resume @ T2.1 (2026-07-29) |
| D-S025-T2.3-A | decision | F23 themes G1–G3 close? | **1 / A** — Close G1–G3 with documented residuals (TOP ABV/BLW light; OBS/FCST collections thin); continue M3 VA lint |

**M2 complete** — T2.1 annex3 goldens + T2.2 exceptional convert + T2.3 matrix close (`D-S025-T2.3-A`).

### Routing (`D-S025-E19-batch1` + Batch 2)

**Required:** 00 → 16 → 01 → 02 → 04 → 07 → 08 → 10 → 13  
**Skipped:** 03, 05, 06, 09, 11, 12 (unless later needed)

---

## Cycle EV-018 — Dissemination multi-file export selection (#785) (S024)

**Session**: S024-dissemination-file-select  
**Features**: **Deepen F16** (F17–F19 reuse selection contract); no F23  
**Issues**: [#785](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/785)  
**Started**: 2026-07-28  
**Completed**: 2026-07-29  
**Branch**: `evolve/EV-018-dissemination-file-select`  
**PR**: [#791](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/791) **merged** (`2f552b9`); FE `dep-d9kkjj5bedkc73au0aeg` live  
**Status**: **completed** (D-S024-close)

### Scope (Batch 1 — locked 2026-07-28)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E18-1 | decision | Open session? | **A** — `S024-dissemination-file-select` → 16-evolve / EV-018 |
| E18-2 | decision | Feature id? | **B** — Deepen **F16**; F17–F19 reuse same selection contract (no new Fn) |
| E18-3 | decision | Routing preset? | **B** — Lean (amended by E18-7 → Lean+build) |
| E18-4 | ambiguity | History sources in v1? | **A** — Current-session + dropped files only; Finished history deferred |

### Scope (Batch 2 — locked 2026-07-28)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E18-5 | decision | Batched API vs N sends? | **A** — N sequential `/preflight`+`/send`; UI aggregates |
| E18-6 | decision | Selection / payload size caps? | **A** — Count cap **≤20** + existing body/size limits |
| E18-7 | ambiguity | Lean vs Lean+build? | **A** — **Lean+build** `00→16→01→02→04→07→08→10→13` |
| E18-8 | decision | UI preview (non-deployed)? | **A** — Open local UI now |

### Approved scope (D-S024-E18-scope-lock — 2026-07-28)

Deepen **F16** multi-file export selection in the dissemination drawer: selectable
candidates from current-session conversion outputs and dropped files only; multi-select
with select-all/clear; empty selection disables Preflight/Send; N sequential preflight/send
with per-file results; ≤20 selection cap; F17–F19 reuse the same UI selection contract;
BYOC memory-only and egress allowlist unchanged. No batch dissemination API, no history
sources, no saved profiles in v1. Routing: **Lean+build**.

### Stage log

| Stage | Completed | Notes |
|-------|-----------|-------|
| 00-context | 2026-07-28 | D-S024-E18-scope-lock |
| 01-requirements | 2026-07-28 | D-S024-01-requirements-delta — corpus deltas approved |
| 02-verify-plan | 2026-07-28 | Phase A PASSED (D-S024-02-phase-a-A); C1/C2 fixed; M1/M2 → 04 |
| 04-tech-plan | 2026-07-28 | D-S024-04-plan-approve-A — plan approved; B→C; handoff 07 @ T1.1 |
| 07-build | 2026-07-28 | M1–M4 / 14 tasks COMPLETE |
| 08-verify-build | 2026-07-28 | PASS |
| 10-e2e | 2026-07-28 | UJ-027–030 7/7 PASS |
| 13-deploy-smoke | 2026-07-29 | **PASS** — PR #791 merged; H4–H5 + H6′ 7/7 |

### Phase A checkpoint (2026-07-28)

| ID | Decision |
|----|----------|
| D-S024-02-phase-a-A | **A** — Pass Gate A; complete 02 → **04-tech-plan**; accept M1/M2 deferrals (single-candidate UX; preflight-all-then-send vs interleaved) |

### 04-tech-plan Batch 1 (locked 2026-07-28)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E18-9 | decision | Single-candidate UX (M1)? | **A** — Auto-select sole candidate; Export selection collapsed/optional |
| E18-10 | decision | Preflight→Send sequencing (M2)? | **B** — **Interleaved** per file: preflight→send, then next; interactive per-file progress graphic (mail→destination along arrow; red mark on fail) |
| E18-11 | decision | Mid-run failure? | **A** — Continue remaining files; aggregate pass/fail/skip |
| E18-12 | decision | Milestone shape? | **A** — M1 selection state → M2 sequential aggregator → M3 drawer UI (+ progress graphic) → M4 Vitest/e2e |

### 04-tech-plan Batch 2 (locked 2026-07-28)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E18-13 | decision | Progress graphic impl? | **A** — CSS + existing `motion` + lucide; **no new deps** |
| E18-14 | decision | Reduced motion / a11y? | **C** — Hide graphic; text-only progress list when `prefers-reduced-motion` |
| E18-15 | decision | Combined Preflight+Send? | **A** — Primary **Disseminate** (preflight→send per file); optional **Preflight only** secondary |
| E18-16 | decision | Tests / connectivity? | **B** — Vitest + Playwright UJ-027–030 + **visual snapshot** of progress row; H6′ at 13 |

### Phase B checkpoint / plan approve (2026-07-28)

| ID | Category | Decision |
|----|----------|----------|
| D-S024-04-plan-approve-A | gate | **A** — Approve execution plan (M1–M4 / 14 tasks); skip 05/06 (Lean+build); start **07-build** @ T1.1 |

**Execution plan artifact**: `docs/sessions/S024-dissemination-file-select/reports/execution-plan.md` (**approved** — D-S024-04-plan-approve-A).

### Deploy gate (2026-07-29)

| ID | Category | Decision |
|----|----------|----------|
| D-S024-13-deploy-A | gate | **A** — Push + open PR #791; after merge run live H4–H5 + H6′ |

**Deploy smoke**: `docs/sessions/S024-dissemination-file-select/reports/deploy-smoke.md` — **PASS** (2026-07-29). PR [#791](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/791) merged `2f552b9`; FE `dep-d9kkjj5bedkc73au0aeg` live; main CI [30411047349](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/30411047349) success.

### Phase 4 close (2026-07-29)

| ID | Category | Decision |
|----|----------|----------|
| D-S024-close | gate | **A** — Close cycle + session; commit/push closeout docs to `main` |

**Report**: `docs/evolve-report-EV-018.md` · `docs/sessions/S024-dissemination-file-select/reports/evolve-summary.md`

---

## Cycle EV-017 — Public app + local history + privacy (#783) (S023)

**Session**: S023-public-app-privacy
**Features**: **F21**, **F22**; deepen **F5** / **F7**; deprecate operator **M4**
**Issues**: [#783](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/783)
**Started**: 2026-07-27
**Completed**: —
**Branch**: `evolve/EV-017-public-app-privacy`
**Status**: **in_progress** — Phase A (02-verify-plan)

### Scope (Batch 1 — session open 2026-07-27)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E17-1 | decision | Open session? | **A** — `S023-public-app-privacy` → 16-evolve / EV-017 |
| E17-2 | decision | Architecture baseline? | **B** — adopt recommended architecture **with tweaks** |
| E17-3 | decision | Routing preset? | **A** — **Standard** (`00→16→01→02→04→07→08→09→10→11→12→13`; skip 03/05/06) |

### Scope (Batch 2 — tweaks — locked 2026-07-27)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E17-4 | decision | Feature IDs? | **A** — **F21** public unauthenticated app + **F22** privacy preference center; deepen **F5/F7** → IndexedDB; deprecate operator **M4** |
| E17-5 | decision | Legacy Supabase sessions? | **A** — no public API to old rows; archive/delete after **~30-day** window; optional one-time export if prod data exists |
| E17-6 | decision | Abuse controls? | **A** — ship baseline now (per-IP + global rate, body/batch size, timeouts; keep SSRF/allowlist) |
| E17-7 | decision | Privacy UI? | **A** — Solution A: footer Privacy settings + short first-visit notice; GPC; no CMP; categories only for tech in use |
| E17-8 | decision | Auth model? | **1** — public + local IndexedDB history (not anonymous server sessions / optional accounts) |
| E17-9 | decision | Tracking? | **Solution A** — no non-essential analytics/marketing |
| E17-10 | decision | Sequence? | Local history replacement **before** JWT / `/auth/*` teardown |
| E17-11 | decision | UI preview (Phase 0) | Deferred to **11-verify-impl** (AskQuestion unavailable; default) |

### Scope summary (approved)

Public/stateless operator convert→validate→download/send without login. F5/F7 work
history in browser IndexedDB (client UUID; export/import JSON; no cross-device sync v1).
No public access to legacy `tac_work_sessions` / per-user rows; ~30-day archive then
drop. Public APIs with baseline abuse controls; F8 service-role remains private.
Privacy: Solution A + one global preference center + GPC. Retire operator Auth UX and
`DISABLE_AUTH` dual path. F8 machine auth unchanged. Dissemination BYOC stays memory-only
(ADR-021/029).

### Deliverable sequence (milestones — for 04-tech-plan)

1. ADR: public app + local-only history
2. Storage/tracker inventory
3. IndexedDB F5/F7 + export/import (before auth strip)
4. Public API abuse controls
5. Frontend auth removal
6. Backend JWT / `/auth/*` teardown
7. Privacy preference center + GPC
8. Docs, env matrix, E2E, secret cleanup

### Fn allocation

| Fn | Title | Role |
|----|-------|------|
| **F21** | Public unauthenticated operator app | Strip login/JWT gates; public convert/validate/lint/decode/preview/dissemination-drawer; abuse controls; retire operator `/auth/*` |
| **F22** | Privacy preference center | Inventory disclosure; settings + notice; GPC; Solution A schema |
| **F5** (deepen) | Work history → IndexedDB | METAR/SPECI local history; no server ownership |
| **F7** (deepen) | Multi-product sessions → IndexedDB | Unified local sessions; slice **F7.h** |
| **M4** | Auth merged into backend | **Deprecated** for operator Auth (library may remain only if F8/internal still needs helpers — decide in ADR) |

### Phase A — 02-verify-plan (2026-07-27)

| ID | Category | Decision |
|----|----------|----------|
| D-S023-02-verify-plan-gate-A | decision | Run 02 delta consistency pass (user **A**) |
| D-S023-02-C-EV017-A | contradiction | **A** — apply C-EV017.1–4 + C6 now; C5 = stale-until-F21 banner + defer full env-contract rewrite to 04/12 |

**Corpus fixes applied**: `api-contract.md`, `spec.md`, `user-journeys.md`, `test-plan.md`
(TC-004 IndexedDB + TC-F21-auth-gone + TC-F22-001..003 stubs); `env-contract.md` banner only.

### Phase A checkpoint (2026-07-28)

| ID | Decision |
|----|----------|
| D-S023-02-phase-a-A | **A** — Phase A pass; start **04-tech-plan** (03 skipped) |

### Tech plan Batch 1 — Architecture (2026-07-28)

| ID | Category | Decision |
|----|----------|----------|
| E17-12 | decision | IndexedDB library = **`idb`** (Jake Archibald) |
| E17-13 | decision | Local session schema = **reuse** `workSessionPayload` / ConverterSnapshot |
| E17-14 | decision | **One-time** migrate guest `sessionStorage` → IndexedDB on first F7.h load |
| E17-15 | decision | Abuse controls = **`slowapi`** (in-memory; Render single-instance baseline) |

### Tech plan Batch 2 — Privacy / Auth / ops (2026-07-28)

| ID | Category | Decision |
|----|----------|----------|
| E17-16 | decision | GPC = honor **`Sec-GPC: 1`** + `navigator.globalPrivacyControl` → opt-out non-essential prefs |
| E17-17 | decision | Prefs in **`localStorage`**; work sessions in **IndexedDB** only |
| E17-18 | decision | **Single deploy** cutover: IndexedDB live + `/auth/*` + work-sessions → 404 same release |
| E17-19 | decision | slowapi baseline: **60/min/IP** convert+lint+decode; **10/min** dissemination; **2 MB** body (exact table in ADR-031) |
| E17-20 | decision | Export/import = JSON **`tac-work-sessions-export-v1`** download/upload in Privacy or History UI |

### Tech plan Batch 3 — Milestones / ADR / packages / env (2026-07-28)

| ID | Category | Decision |
|----|----------|----------|
| E17-21 | decision | **7 milestones**: ADR+deps → IndexedDB+migrate+export → slowapi → FE Auth strip → BE Auth/work-sessions 404 → Privacy+GPC → env/E2E/docs |
| E17-22 | decision | **Delete `packages/auth` entirely** this cycle; inline any F8 helpers if needed |
| E17-23 | decision | **Supersede ADR-020** with **ADR-031** (IndexedDB local history) |
| E17-24 | decision | **Full env-contract rewrite now** (closes C-EV017.5) |
| E17-25 | decision | Draft ADR-031 + execution-plan + dependency-inventory; then approve plan |

### Plan approve (2026-07-28)

| ID | Category | Decision |
|----|----------|----------|
| D-S023-04-plan-approve-A | gate | **A** — ADR-031 **Accepted**; execution plan approved (M1–M7); 05/06 skipped (Standard); start **07-build** @ T1.1 |

---

## Cycle EV-016 — Workbench golden examples (#780) (S021)

**Session**: S021-golden-examples-ui
**Features**: deepen **F7** only (no new Fn)
**Issues**: [#780](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/780)
**Started**: 2026-07-22
**Completed**: —
**Branch**: `evolve/EV-016-golden-examples-ui`
**Status**: **in_progress** — 11 approved (E16-19); minor PR → 13-deploy-smoke

### Scope (Batch 1 — locked 2026-07-22)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E16-1 | decision | Open session? | **A** — `S021-golden-examples-ui` → 16-evolve / EV-016 |
| E16-2 | decision | Feature id? | **A** — deepen **F7** only (no F21) |
| E16-3 | decision | Routing preset? | **A** — Lean+build (`00→16→01→02→04→07→08→09→10→11→13`) |
| E16-4 | decision | Scope lock? | **A** — #780 AC (FE fixtures + Examples UX + Vitest; no backend) |

### Scope (Batch 2 — 01-requirements — locked 2026-07-22)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E16-5 | decision | User journey? | **A** — **UJ-032** + **TC-F7-008** |
| E16-6 | decision | F7 status? | **A** — stay **Planned**; add slice **F7.g** |
| E16-7 | decision | Optional #780 items? | **A** — happy-path IWXXM only; skip soft-fail + file-upload queue |
| E16-8 | ambiguity | Thin hazard fixtures? | **A** — use in-repo only; allow **1** + document gap; no invented TAC |
| E16-9 | decision | Spec delta set? | **A** — feature-list + user-journeys + test-plan + light spec; no api/config/deploy env |

### Scope summary (approved)

Frontend-only pre-loaded goldens for convert + validate: ≥2 TAC/product × 7 products
(or documented 1-fixture gap for thin hazard products); ≥1 AHL + ≥1 happy-path IWXXM COLLECT;
Examples control in FileConverter sets product/inputMode; copy from package goldens into
`apps/frontend`; Vitest TC-F7-008; no API/env/DB. Soft-fail XML and file-upload queue OOS v1.

### Phase A gate (02-verify-plan)

| ID | Decision |
|----|----------|
| E16-02-pass | Consistency PASS 2026-07-22 — audit `reports/02-verify-plan-audit.md` |
| E16-10 | decision | Phase A→B | **Approve** — proceed to 04-tech-plan (2026-07-26) |

### Tech plan (04 Batch 1 — locked 2026-07-26)

| ID | Category | Topic | Decision |
|----|----------|-------|----------|
| E16-11 | decision | Catalog shape | **A** — typed TS catalog + copied fixtures under `apps/frontend/src/fixtures/examples/` |
| E16-12 | decision | Examples placement | **A** — control next to product / Manual TAC Input |
| E16-13 | decision | Fixture pairing | **A** — annex3 + product_matrix + iwxxm_us; VAA/TCA 1 + documented gap |
| E16-14 | decision | IWXXM sample | **A** — happy-path single-report golden XML → `collect_iwxxm` |
| E16-15 | decision | Select component | **B′** — reuse existing Radix `ui/select` (no new npm dep) |
| E16-16 | decision | Execution plan | **A** — approve M1–M3 / 11 tasks as written; B→C; start 07 @ T1.1 |

### Verify / Phase C→D (2026-07-26)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E16-18 | decision | After 08: run 09+10 now? | **A** — run 09-qa + 10-e2e (not push/PR first) |
| E16-19 | decision | 11-verify-impl sign-off? | **A** — Approve UJ-032 + F7.g (T0 + local UI preview; H4–H5 waived to 13; QA-001–004 accepted) |

### Phase 4 close (`D-S021-EV016-phase4-close`) — 2026-07-27

| ID | Decision |
|----|----------|
| D-S021-EV016-13-waive-live-h4h5 | User option **3** — waive live H4–H5 / UJ-032 goldens UI; defer to [#781](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/781) |
| D-S021-EV016-phase4-close | Complete 13 as waived; mark EV-016 completed; close S021; F7 stays Planned |

**Completed**: 2026-07-27
**Branch**: `evolve/EV-016-golden-examples-ui` → PR [#782](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/782) @ `c49f22b`
**Status**: **completed** — #780 closed; live FE smoke owned by #781

### Tech plan artifacts

| Artifact | Path |
|----------|------|
| 04 report | `docs/sessions/S021-golden-examples-ui/reports/04-tech-plan.md` (**completed**) |
| Execution plan | `docs/sessions/S021-golden-examples-ui/reports/execution-plan.md` (**approved** E16-16) |
| 11 verify | `docs/sessions/S021-golden-examples-ui/reports/verify-impl.md` (**approved** E16-19) |
| 13 deploy | `docs/sessions/S021-golden-examples-ui/reports/deploy-smoke.md` (**waived** live H4–H5) |
| Evolve summary | `docs/sessions/S021-golden-examples-ui/reports/evolve-summary.md` |
| Evolve report | `docs/evolve-report-EV-016.md` |

## Cycle EV-015 — F15 sequel: TAF + SPECI quality (#735 / #734) (S020)

**Session**: S020-aerodrome-quality
**Features**: **F20** (new) + deepen **F6.b / F6.c** + **F12**
**Issues**: [#735](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/735), [#734](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/734)
**Started**: 2026-07-22
**Completed**: 2026-07-22 (`D-S020-EV015-phase4-close`)
**Branch**: `evolve/EV-015-aerodrome-quality` → PR [#778](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/778) @ `eae8bdc`
**Status**: **completed** — F20 Done; #735/#734 closed; Render live `…-eae8bdc`

### Phase 4 close (`D-S020-EV015-phase4-close`)

| ID | Decision |
|----|----------|
| D-S020-EV015-merge-778 | Merge #778; Deploy; H1–H5 + catalog taf/speci; close M5/Phase D |
| D-S020-EV015-phase-d | T5.7 PASS; gates c_to_d + deploy passed; F20 Done |
| D-S020-EV015-phase4-close | Commit+push closeout; close #735/#734; evolve-summary; complete EV-015; close S020 |

### Scope (Batch 1 — locked 2026-07-22; S1.M2 rename amend)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E15-1 | decision | Open session? | **A** then **amended** → `S020-aerodrome-quality` (`D-S020-EV015-s1m2-2`) |
| E15-2 | decision | #734 SPECI scope? | **A** — full parallel quality bar + #735 TAF |
| E15-3 | decision | Fn allocation? | **A** — F20 (TAF+SPECI quality) + deepen F6/F12; ADR-028 reuse |
| E15-4 | decision | Routing preset? | **C** Lean — **superseded** by E15-route-amend |
| E15-route-amend | decision | Lean vs build? | **A** Lean+build — `D-S020-EV015-route-1` |

### Scope (Batch 2 — locked 2026-07-22)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E15-5 | decision | Research / encode depth? | **A** — full #735/#734 AC (guidance + fixtures + goldens + matrix) for TAF **and** SPECI |
| E15-6 | decision | Out of scope? | **A** — siblings OOS; no PyPI bump; no F16–F19; F7 Planned (smoke only) |
| E15-7 | decision | Deploy / smoke (13)? | **A** — redeploy if API/FE changes; H1–H3 if API; H4–H5 workbench `taf`/`speci` |
| E15-8 | decision | Proceed to F20 + 01? | **A** — lock Phase 0; hand off 01-requirements delta |

**Phase 0 scope approved** — proceed to allocate F20 in `feature-list.md` and 01 delta.

### Routing (`D-S020-EV015-route-1`)

**Required:** 00 → 16 → 01 → 02 → 04 → 07 → 08 → 09 → 10 → 11 → 13
**Skipped:** 03, 05, 06, 12 (unless later needed)

### Stage log

| Stage | Completed | Notes |
|-------|-----------|-------|
| 00-context | 2026-07-22 | brief + routing + Phase 0 Batch1/2 locked |
| 01-requirements | 2026-07-22 | F20 + UJ-031 + TC-F20 + API review; E15-10=A |
| 02-verify-plan | 2026-07-22 | PASS; S1.M1=1, S1.M2=2 rename, S9.M1=1 |
| 04-tech-plan | 2026-07-22 | M0–M5 approved E15-16..19; 04-exit consistency PASS |
| 07–11 | 2026-07-22 | M0–M5 28/28; 08/09/10/11 PASS |
| 13-deploy-smoke | 2026-07-22 | #778 merge; H1–H5 + catalog taf/speci PASS |
| 16-evolve Phase 4 | 2026-07-22 | `D-S020-EV015-phase4-close` |

### 02 medium verdicts

| ID | Verdict |
|----|---------|
| S1.M1 | Keep full HARD themes; 04 kill-switch |
| S1.M2 | Rename → aerodrome-quality |
| S9.M1 | Keep skip 05; 04-exit consistency |

---

## Cycle EV-014 — Dissemination epic (#729 / #2 / #6) (S019)

**Session**: S019-dissemination-upload
**Features**: **F16–F19 Planned** (Phase 0 approved Q24=A 2026-07-21)
**Issues**: [#729](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/729), [#2](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/2), [#6](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/6)
**Started**: 2026-07-20
**Branch**: `main` @ `3c9ee81` (#753 MERGED); build branches `cursor/*-b45b` off main
**Status**: Phase B **in progress** — **05-verify-tech PASS** (D-S019-EV014-Q35A-05); next **06-tech-tooling**

### Intake (Batch 1 Assumed — AskQuestion waived / cloud written interview) — still locked (**amended Batch 5**)

| ID | Decision |
|----|----------|
| Creds | One-shot session credentials (paste in UI); never persist / never saved profiles |
| UI | Drawer for send/upload destination + preflight |
| Schema | **Superseded by Q20=A:** DDL / create-if-missing allowed (overrides earlier require-existing-only) |
| Q1 | **Amended by Q20=B:** Convert-in-app then send **plus** drag-drop upload of external IWXXM/TAC |
| Q2=A | Any authenticated user |
| Q3=A | Schema preflight clarity is success metric |
| Q4=D | Include WIS2 + EDIS scaffolding in ONE BIG dissemination cycle with #729 |

### Intake (Batch 2 Assumed — AskQuestion waived / cloud written interview) — locked 2026-07-20

| ID | Decision |
|----|----------|
| Q5=A | Paste in drawer → backend memory-only for preflight+upload (never persist) |
| Q6=B | URI-only + preflight + send (no discrete field form in v1) |
| Q7=A | Structured schema diff in drawer; block Send until preflight green |
| Q8=C | Ship all three to usable MVP — live wis2box + live EDIS path (highest risk) |
| Q9=A | Same drawer: destination type Postgres (now) / WIS2 / EDIS |

### Intake (Batch 3 Assumed — AskQuestion waived / cloud written interview) — clarifications 2026-07-20/21

| ID | Status | Decision / note |
|----|--------|-----------------|
| Q10 | **Locked Assumed** | **NOT** dropping Supabase Auth — login stays Supabase-handled. “Dropping Supabase for database” = Sending/converting dissemination destination only: one-shot BYO Postgres URI for upload/send (not Supabase as ops/send DB). **Q10A=D:** deploy-time BYO for app auth (operator sets Supabase env once; users don’t paste app auth) — aligned with ADR-021. **Q10B:** N/A. |
| Q11=A+B | **Locked Assumed** | Max-security SSRF: full recommended baseline (backend-only egress, deny private/metadata ranges, DNS rebinding guard, TLS preferred, timeouts/size limits, secret redaction, rate limit) **PLUS require** `DISSEMINATION_EGRESS_ALLOWLIST` (host/CIDR) — empty allowlist = no user-URI egress in prod (staging may use explicit list). |
| Q12=B | **Locked Assumed** (amended Batch 4 / Q17) | Staging wis2box in this project's infra = **test harness only**; live WIS2 acceptance = user-supplied endpoint creds (BYOC). |
| Q13=A | Locked Assumed | Real SMTP/submission to NWS Telecommunications Gateway (RTH Washington) |
| Q14=A | **Locked Assumed** (literal kept) | Only saved/encrypted profiles out of scope (B-only from OOS list). Literal Q14=A kept; see Q14r for intentional expand. |
| Q15=A | Locked Assumed → **amended** | Keep Q8=C — block cycle close until Postgres + WIS2 + EDIS all green on real targets. **Amended 2026-07-21** by `D-S019-EV014-Q15-mock-waive`: operator authorized mock/harness credentials (gitignored `.env` + committed fixture shapes + transport mocks / Compose when Docker available) in lieu of live destination BYOC for EV-014 T6.6 / cycle close. |
| Q16 | **Locked Assumed** | BYO credentials (EDIS/RTH; WIS2/DB as applicable). Not provisioned by us except staging wis2box **test harness** (Q12=B/Q17). Live-green close gate still applies (Q15=A). |

### Intake (Batch 4 Assumed — AskQuestion waived / cloud written interview) — locked 2026-07-21

| ID | Status | Decision / note |
|----|--------|-----------------|
| Q14r=B | **Locked Assumed** (enum resolved Batch 5) | Keep Q14=A literally. Epic **also designs** DDL, drag-drop, multi-DB, **and** AMHS — user chose **expand scope (B)** over recommended pack (A). v1 IN-set enumerated Batch 5 Q20 (all four). |
| Q17=A | **Locked Assumed** (**testing only**) | Staging wis2box on Render/Docker for **test**; live WIS2 = BYOC user node/creds. Amends Q12=B. |
| Q18≈A (BYOC) | **Locked Assumed** | User BYOC for EDIS (and live paths). **Q18≈A:** one-shot user-pasted SMTP/gateway settings in drawer (memory-only), **not** deploy-only operator SMTP. Testing also BYOC. |
| Q19=A | **Locked Assumed** | Work history stays Supabase `tac_work_sessions` / `kv_upload_key`; **never** store destination secrets. |

### Intake (Batch 5 Assumed — AskQuestion waived / cloud written interview) — locked 2026-07-21

| ID | Status | Decision / note |
|----|--------|-----------------|
| Q20=B,C,A,D | **Locked Assumed** | **All four extras IN:** DDL; drag-drop; multi-DB; AMHS/SWIM/AFS. |
| Q21=A | **Locked Assumed** → **amended** | Staging/test OK for merge; **live BYOC demos required before cycle close** (with Q15=A). **Amended** with Q15 mock waive (`D-S019-EV014-Q15-mock-waive`): mock BYOC + staging harness evidence satisfies close for EV-014. |
| Q22=A | **Locked Assumed** | **Full routing** approved with Q24=A. |
| Q23=A–D | **Locked Assumed** | Multi-DB vendors: Postgres, MySQL/MariaDB, SQL Server, SQLite (no other named). Resolves **I-S019-EV014-Q20C-vendors**. |
| Q24=A | **Locked Assumed** | Approve F16–F19 + Full routing; write feature-list; start 01-requirements. |

### Fn allocation (APPROVED — in `feature-list.md`)

| Fn | Title | Issues |
|----|-------|--------|
| F16 | Dissemination drawer + multi-DB upload (URI, preflight, DDL, drag-drop) | #729 |
| F17 | WIS2 live pathway (staging wis2box test + live BYOC) | #2 |
| F18 | EDIS → RTH Washington (BYOC SMTP/gateway) | #6 |
| F19 | AMHS / SWIM / AFS adapters | non-goals overturn |

### Phase 0 approval

- **Approved** 2026-07-21 (Q23 + Q24=A). Proceed to Phase A: 01 → 02 → 03.

### Resolved Batch 5

- **I-S019-EV014-Q14r-extras-enum** — all four extras IN (Q20=A,B,C,D)
- Batch 1 Schema require-existing-only — **superseded** by Q20=A
- Batch 1 Q1=A convert-then-send-only — **amended** by Q20=B

### Resolved Batch 4

- **I-S019-EV014-Q14-batch1** — resolved as **scope expanded intentionally** (Q14r=B vs recommended pack A); extras enum → I-S019-EV014-Q14r-extras-enum (now resolved Batch 5)
- Prior Batch 3: I-S019-EV014-Q10-supabase-byo, I-S019-EV014-Q11-pending-rec, I-S019-EV014-Q14-multiselect

### Corpus amendments required (after Phase 0 approval → 01-requirements)

| Corpus | Required change |
|--------|-----------------|
| Non-Goals push sinks | Overturn / narrow — push sinks IN (WIS2/EDIS/AMHS/SWIM/AFS) |
| Non-Goals paste-keys | Clarify: paste for **upload/destination creds only** (not app auth) |
| Non-Goals AMHS/SWIM/AFS | Overturn — adapters IN (Q20=D → F19) |
| ADR-021 | Amend for destination paste (URI/SMTP memory-only; app auth stays deploy-time) |
| ADR new | Dissemination security / SSRF (Q11=A+B) |

### Corpus contradictions (updated)

| Corpus | Status / tension |
|--------|------------------|
| ADR-021 BYO deploy-env Supabase (no paste-keys for app auth) | **Eased by Q10** — Q10A=D deploy-time Supabase auth; paste is destination URI/SMTP only (Q5/Q18≈A) — **ADR-021 amend required** |
| F5 work history on Supabase | **Locked by Q19=A** — Auth+F5 remain Supabase; never store destination secrets |
| Non-goals: push sinks; paste-keys; AMHS/SWIM/AFS | **Inventory pending** after Phase 0 approval — Q8=C + Q20=D overturn push sinks / AMHS; paste = dest only |
| Batch 1 require-existing + Q1=A | **Superseded/amended** by Q20=A (DDL) + Q20=B (drag-drop) |

### 04-tech-plan Batch 1 — Architecture (LOCKED — Q32=A / D-S019-EV014-Q32A-04-batch1)

| ID | Answer | Decision |
|----|--------|----------|
| E14-01 | B | New `packages/dissemination` + thin `apps/backend` routers |
| E14-02 | A | SQLAlchemy 2 async + dialect drivers; versioned writer-contract DDL per engine |
| E14-03 | A | Unified `POST /api/v1/dissemination/preflight` + `…/send` |
| E14-04 | B | Staging wis2box = Docker Compose / CI harness (not Render web service) |
| E14-05 | A | EDIS via `aiosmtplib`; F19 AMHS/SWIM/AFS on same sink adapter interface |

**ADR-030** Accepted. Corpus back-adds: spec Component Overview, plan-adherence,
template-conformance, api-contract Planned routes, dependency-inventory Planned deps.

### 04-tech-plan Batch 2 — Deploy / test / integration (LOCKED — all A / D-S019-EV014-Q33A-04-batch2)

| ID | Answer | Decision |
|----|--------|----------|
| E14-06 | A | SQL Server via `aioodbc` + documented ODBC requirement |
| E14-07 | A | msgspec encode for dissemination routes (ADR-026 align) |
| E14-08 | A | `DISSEMINATION_EGRESS_ALLOWLIST` in env-contract + config-spec + Render API; empty fail-closed; staging lists Compose/CI hosts |
| E14-09 | A | Unit + Testcontainers/Compose (PG/MySQL/SQLite) + mocked SMTP/WIS2; Playwright drawer; live BYOC = close gate only |
| E14-10 | A | Ship FE drawer this cycle; H4–H5 required after FE+API redeploy |

### 04-tech-plan complete (Q34=A / D-S019-EV014-Q34A-04-approve)

- Execution plan **approved** — M1–M6 + T0.1 (**29** tasks after 05 count fix; was mislabeled 32).
- 04-tech-plan stage **completed**; #753 MERGED to `main` @ `3c9ee81`.

### 05-verify-tech complete (D-S019-EV014-Q35A-05)

- Audit **PASS** — 22 high auto-approved; S1–S8 Modify applied (task count, git strategy,
  secrets matrix allowlist, ADR-029/030 stale language, api-contract wording, rate-limit on
  T2.3/T2.4, F17 Compose/CI align). AskQuestion waived / cloud Assumed.
- Report: `docs/sessions/S019-dissemination-upload/reports/05-verify-tech-audit.md`
- Next: **06-tech-tooling** (T0.1) → Phase B checkpoint → 07-build M1 T1.1.

### 06-tech-tooling complete (D-S019-EV014-Q36A-06)

- Assumed approve-all delta tooling (cloud AQ waived).
- T0.1: dissemination coverage runner (≥95% when scaffolded) + wis2box Compose CI hooks
  (skip until T3.3); Makefile + `ci-cd.yml` matrix; optional Cursor rule; hook maps.
- Report: `docs/sessions/S019-dissemination-upload/reports/06-tech-tooling.md`
- Next: Phase B checkpoint → **07-build** M1 T1.1.

### Phase B checkpoint (D-S019-EV014-Q37A-phase-b)

- Assumed PASS (cloud AQ waived): 05 audited; 06 T0.1 installed; B→C open.
- Next: **07-build** M1 T1.1.

### T3.3 wis2box harness image (D-S019-EV014-T33-harness)

- **A — Lightweight MQTT + HTTP dataset stand-in** under
  `packages/dissemination/docker/wis2box-harness` (`python:3.12.11-slim-bookworm` + Debian
  `mosquitto`); Compose overlay `docker-compose.wis2box.yml` profile `wis2box`; CI hook
  `scripts/ci/run_wis2box_harness.sh` on integration matrix.
- Reject full WMO wis2box-release multi-container stack for CI cost/ops (E14-04 / Q17
  testing-only). Live WIS2 remains BYOC (TC-F17-002).
- Merged session stack before T3.3: PR #761 (T2.7), #762 (T3.1–T3.2) → `main`.

### T3.4 harness publish transports (D-S019-EV014-T34-transports)

- **A — httpx + aiomqtt≥2.3,<3** concrete transports in `dissemination.transports`
  (`HttpxDatasetClient`, `AiomqttClient`) for TC-F17-001 Compose harness publish.
- Reject aiomqtt 3.x alpha for this milestone (API churn).

### Notes

- Prior: S018/EV-013 closed 2026-07-20 (Q0=A waive leftover 08/09/11/12); #750 remarks live
- Phase 0 approved 2026-07-21 — F16–F19 in feature-list; Full routing; 01-requirements delta landed
- **Close gate (Q15=A + Q8=C + Q21=A + Q16/Q17/Q18):** staging/test OK for merge; originally
  block cycle close until live BYOC demos green for **Postgres + WIS2 + EDIS**. F19
  (AMHS/SWIM/AFS) requires staging/test path green; live F19 demo optional with AskQuestion
  waive (S-EV014-M2 / Q28=A).
- **`D-S019-EV014-Q15-mock-waive` (2026-07-21):** Operator chose mock credentials / mock DB /
  mocked WIS2+EDIS (and Compose wis2box when Docker available) instead of live destination
  services. Evidence: `make test-mock-byoc-smoke` (134 passed this session; Docker optional
  extras skipped). Secrets stay gitignored (`.env`); fixture shapes committed under
  `docs/sessions/S019-dissemination-upload/fixtures/mock-byoc-destinations.json`.
- PR (04): https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/753 MERGED
- 2026-07-21: 04 Batch 1–2 locked; plan approved; 05 PASS; 06 T0.1 complete; Phase B Assumed
- 2026-07-21: #771 MERGED; T6.6 completed via mock BYOC waive (PR #772)
- 2026-07-21: #772 MERGED (`c61273a`); Phase C Assumed PASS → Phase D bookkeeping → cycle close

### Phase C checkpoint (D-S019-EV014-Q38A-phase-c)

- Assumed PASS (cloud AQ waived; operator continue authorized): M1–M6 **29/29**; T6.4 08 PASS;
  T6.6 mock BYOC complete; C→D open.
- Report: `docs/sessions/S019-dissemination-upload/reports/phase-c-checkpoint.md`

### Phase D (08–13 bookkeeping) + checkpoint (D-S019-EV014-Q39A-phase-d)

- 08 = T6.4 `verification-report.md` PASS
- 09 = `qa-report.md` PASS (advisories: live BYOC / Render allowlist / H3)
- 10 = `e2e-report.md` PASS (UJ-027–030 + mock BYOC)
- 11 = `verify-impl.md` PASS (`D-S019-EV014-Q40A-11`)
- 12 = T6.5 `deploy-checklist.md` PASS
- 13 = T6.6 `deploy-smoke.md` COMPLETE (mock waive)
- Phase D Assumed PASS (cloud AQ waived).
- Report: `docs/sessions/S019-dissemination-upload/reports/phase-d-checkpoint.md`

### Phase 4 close (D-S019-EV014-phase4-close)

- Close EV-014 / S019: F16–F19 **Done**; evolve-report + evolve-summary written;
  leftover live destination BYOC remains optional follow-up (not blocking).
- Artifacts: `docs/evolve-report-EV-014.md`,
  `docs/sessions/S019-dissemination-upload/reports/evolve-summary.md`

### Closeout hygiene (D-S019-EV014-closeout-1)

- 2026-07-21: Bookkeeping PR [#774](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/774)
  MERGED (`915f41e`).
- Closed superseded draft [#770](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/770)
  (T6.3 already on `main` via #771/#772).
- Closed tracking issues [#729](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/729),
  [#2](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/2),
  [#6](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/6) (F16–F18 Done).
- `workflow-state.yaml` hygiene: S019 branches marked merged/superseded; top-level
  `16-evolve` / `11-verify-impl` / `overall_status` → completed.

---

## Cycle EV-013 — Handle METAR remarks (#667) (S018)

**Session**: S018-metar-remarks-667
**Features**: F6 (deepen)
**Issues**: [#667](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/667)
**Started**: 2026-07-20
**Completed**: 2026-07-20 (D-S018-EV013-Q0A-close-waive)
**Deploy**: #750 live; 13-deploy-smoke `pass_with_advisories`

### Close

| ID | Decision |
|----|----------|
| D-S018-EV013-Q0A-close-waive | Close EV-013/S018; waive leftover 08/09/11/12 bookkeeping; start S019/EV-014 dissemination |

---

## Cycle EV-012 — Validate Manual TAC Input modes (#730) (S016)

**Session**: S016-manual-tac-input-modes
**Features**: F7 (validation deepen only; status stays Planned)
**Issues**: [#730](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/730)
**Started**: 2026-07-20
**Branch**: `evolve/EV-012-manual-tac-input-modes`
**Completed**: 2026-07-20 (D-S016-EV012-phase4-close-1)

### Scope (Phase 0 locked 2026-07-20)

1. Test/acceptance under **F7 / ADR-024** for Manual TAC Input modes (TAC / AHL / COLLECT)
2. Playwright T1–T4 + Vitest anchors + staging H4–H5 + AHL happy path + COLLECT **501** UX
3. Auto-switch on paste/upload is **required**
4. **No new Fn**; COLLECT member extract out of scope; F7 remains **Planned**
5. Routing **lean + 13**: 00 → 16 → 01 → 02 → 10 → 13

### Intake decisions

| ID | Category | Question | Decision | ADR |
|----|----------|----------|----------|-----|
| E12-1 | decision | Cycle type | A — F7 validation; no new Fn; COLLECT 501 | ADR-024 |
| E12-2 | decision | Automation depth | Vitest + Playwright T1–T6 (hard) + live staging all green | — |
| E12-3 | decision | Auto-switch (T3) | Required acceptance | ADR-024 |
| E12-4 | decision | Deploy | Include 13-deploy-smoke | — |
| D-S016-EV012-route-1 | decision | Routing vs lean/deploy contradiction | Lean + 13 (skip 03–09, 11–12) | — |
| S2.1 | contradiction | H6 omits UJ-025 | Fix: add UJ-025 to H6/H6′ row | — |
| S2.2 | ambiguity | T5/T6 vs all tests | T1–T6 all hard gates | — |
| S2.3 | decision | UJ id | Keep UJ-025 (not fold into UJ-013) | — |
| D-S016-EV012-13-path-A | decision | Deploy path | Push/PR then smoke after merge/deploy | — |
| D-S016-EV012-13-pass | decision | 13 result | Deploy smoke PASS @ `37be5f8` | — |
| D-S016-EV012-phase4-close-1 | decision | Phase 4 | Close EV-012/S016; close #730 | — |

### Stage log

| Stage | Completed | Notes |
|-------|-----------|-------|
| 00-context | 2026-07-20 | Session + scoped brief |
| 16-evolve | 2026-07-20 | Phase 4 closed |
| 01-requirements | 2026-07-20 | UJ-025 + TC-F7-007 + F7 validation note |
| 02-verify-plan | 2026-07-20 | PASS — S2.1 fix H6; S2.2 T1–T6 hard; S2.3 UJ-025 |
| 10-e2e | 2026-07-20 | PASS — TC-F7-007 T1–T6 Playwright + Vitest anchors |
| 13-deploy-smoke | 2026-07-20 | PASS — H0ci–H5 + AHL + COLLECT 501 + live workbench |

---

## Cycle EV-011 — METAR lint registry + #732 quality (S015)

**Session**: S015-metar-lint-quality
**Features**: F15 (new) + deepen F6/F12
**Issues**: [#732](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/732)
**Started**: 2026-07-19
**Branch**: `evolve/EV-011-metar-lint-quality`
**Completed**: 2026-07-20 (D-S015-EV011-phase4-close-1)
**Merge**: PR [#742](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/742) → `b405a96`; deploy-smoke PR [#743](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/743)

### Close

| ID | Decision |
|----|----------|
| D-S015-EV011-phase4-close-1 | Close EV-011/S015; F15 **Done**; defer PyPI `tac-validate-v0.1.1`; close #732 |

### Scope (Phase 0–1 locked 2026-07-19)

1. Maintainable METAR lint **issue registry** (`info` / `warning` / `error`), additive and documented
2. Full [#732](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/732) METAR quality bar — lint, convert, IWXXM validate, API/UI path
3. Golden TAC → IWXXM → XSD+Schematron where fixtures exist or are expanded
4. **Max research + validation/conversion expansion** — research catalog in 01 **and** aggressive encode of R1–R6 **and** registry/goldens **and** any other in-scope METAR quality wins (MetarCentral, AviationRef, iwxxmConverter)
5. New **F15**; deepen **F6** (convert/goldens) and **F12** (tac-validate METAR pack)
6. Routing **00–13** including 03/06 and Render 12–13

**Out**: FMS flight-plan spec as METAR authority; new products beyond seven; COLLECT/dissemination; sibling product tickets unless registry sharing requires it.

### Prior cycle close

| Item | Decision |
|------|----------|
| S011 / EV-008 | Completed 2026-07-19 — user close; PR #716 already merged (`22a6199`); 13 waived |

### Intake decisions

| ID | Category | Question | Decision | ADR |
|----|----------|----------|----------|-----|
| E11-1 | Decision | EV-008 disposition | Close S011/EV-008; start new | — |
| E11-2 | Decision | Session open | S015 feature → 16-evolve | — |
| E11-3 | Decision | Scope | Full #732 + registry + goldens + research/validation/conversion expansion | — |
| E11-4 | Decision | Fn allocation | New F15 + deepen F6/F12 | — |
| E11-5 | Decision | Routing | Approve 00–13 incl. 03/06 + Render 12–13 | — |
| E11-6 | Decision | Research depth | 1+2+3+: aggressive R1–R6 + catalog in 01 + registry/goldens + opportunistic METAR improvements | — |
| E11-7 | Decision | Doc manifest | Approve as proposed (feature-list, spec, journeys, test-plan, coverage/research, ADR; API if shape changes) | — |
| E11-8 | Decision | Registry home | `packages/tac-validate` registry module + docs/generated catalog | ADR-028 |
| E11-9 | Decision | F15 Feature List | Approve as written | — |
| E11-10 | Decision | Code stability | Stable public codes; severities may tighten in minor releases | ADR-028 |
| E11-11 | Decision | F7 status | Leave Planned; METAR workbench smoke under F15 only | — |
| E11-12 | Decision | Spec/ADR/catalog | Approve + api-contract note: lint-tac wire shape unchanged | — |
| E11-13 | Decision | UJ/TC | Approve UJ-024 + TC-F15 **with SPECI adjacency** (TC-F15-005) | — |
| E11-14 | Decision | After 01 | Phase A checkpoint → 02-verify-plan | — |
| E11-15 | Decision | S1.M1 | Keep METAR+SPECI in F15; note #732 SPECI shares pack | — |
| E11-16 | Decision | S1.M2 | Max R1–R8 scope; 04 kill-switch if blocked | — |
| E11-17 | Decision | S9.M1 | CORPUS product scope → F1–F15 / M1–M6 | — |
| E11-18 | Decision | 03 tooling | plan-adherence + registry rule + issue_registry_guard hook | — |
| E11-19 | Decision | 04 milestones | M1 registry+CI+catalog stub; M2 migrate codes; M3 R1–R5(+R8 capacity); M4 goldens R6 + SPECI R7; M5 coverage/smoke/verify-deploy; soft kill-switch → deferred + coverage note (E11-16) — **superseded for R themes by E11-23** | — |
| E11-20 | Decision | 04 registry API | `packages/tac-validate` `issue_registry.py` — frozen IssueSpec + ISSUES/by_code(); rules emit via helpers (no severity literals) | — |
| E11-21 | Decision | 04 code namespace | Keep SCREAMING_SNAKE public codes; optional product/tags on registry row, not in code string | — |
| E11-22 | Decision | 04 catalog | `docs/domain/rules/ISSUE_CATALOG.md` (+ optional JSON); make/pytest drift check vs registry module | — |
| E11-23 | Decision | 04 kill-switch | **HARD** — every R1–R8 theme ships green rule+fixture this cycle; NO deferred rows for R themes; overrides soft E11-16 deferral for quality themes; registry M1–M2 still mandatory; if blocked mid-build stop + AskQuestion (do not silently defer) | — |
| E11-24 | Decision | 04 fixtures | Convert goldens stay in tac2iwxxm `annex3_golden` + `iwxxm_us_golden` (extend manifests); lint accept/negative under `tac-validate` `tests/fixtures/{accept,negative}/metar` or `speci/`; short synthetic TAC only | — |
| E11-25 | Decision | 04 PyPI | Implement on 0.1.0 line; tag/publish `tac-validate-v0.1.1` after F15 acceptance; no iwxxm-validate/tac2iwxxm bump unless convert goldens force it | — |
| E11-26 | Decision | 04 deploy | Full Render 12–13; no new CORS/VITE knobs; H1–H3 always; H4–H5 when FE redeployed for TC-F15-004; if FE unchanged document reuse/waive with evidence — **H4–H5 now required via E11-29 FE work** | — |
| E11-27 | Decision | 04 CI | CI = pytest unknown-code + catalog drift + expanded golden M-xsd/M-sch + negative `expected_codes`; no new GHA workflow | — |
| E11-28 | Decision | 04 R8 pack | R8 HARD full pack mandatory — AUTO, COR, NIL, NOSIG, TEMPO, RVR, wind VRB/gust — each green registry+fixture this cycle | — |
| E11-29 | Decision | 04 FE | FE this cycle — registry catalog UI + code tooltips (not wire-shape change to lint-tac); implies FE redeploy + H4–H5 required | — |
| E11-30 | Decision | 04→06 tooling | 06 delta — Makefile catalog regen; fixture README; optional pre-commit; guard stays **warn** until T2.2a escalates to **error** (E11-32); no new deps | — |
| E11-31 | Decision | 04 plan approve | Approve M1–M5 + T6.0; FE catalog via **`GET /api/v1/lint-issue-catalog`** (not static-only); lint-tac wire still unchanged | — |
| E11-32 | Decision | 05 audit S1–S4 | All option 1: task count → 35 (+T2.2a); HARD product docs; T6.0 warn→error after T2.2; ADR/research/acc4/msgspec/H0c bundle | ADR-028 amend |

### Stage log

| Stage | Completed | Notes |
|-------|-----------|-------|
| 00-context | 2026-07-19 | Session + scoped brief; routing approved E11-5/E11-6 |
| 01-requirements | 2026-07-19 | F15 + ADR-028 + spec/api/journeys/test-plan + research catalog; SPECI adjacency |
| 02-verify-plan | 2026-07-19 | PASS — 12 auto + S1.M1/M2/S9.M1 = 1; CORPUS fixed |
| 03-plan-tooling | 2026-07-19 | plan-adherence + registry rule + afterFileEdit guard |
| 04-tech-plan | 2026-07-19 | Execution plan approved E11-31 (GET catalog); later 35 tasks after E11-32 |
| 05-verify-tech | 2026-07-19 | PASS — S1–S4 = 1/1/1/1 (E11-32); HARD docs + ADR-028 amend |
| 06-tech-tooling | 2026-07-19 | T6.0 — catalog-regen, fixture README, warn pre-commit; connectivity OK |
| 05-verify-tech | | |
| 06-tech-tooling | | |
| 07-build | | |
| 08-verify-build | | |
| 09-qa | | |
| 10-e2e | | |
| 11-verify-impl | | |
| 12-verify-deploy | | |
| 13-deploy-smoke | | |

---

## Cycle EV-010 — Package publish + validation stack (S014)

**Session**: S014-package-publish-validation
**Features**: F11–F14 (proposed — pending Phase 1 approval)
**Issues**: #703, #699, #698, #693
**Started**: 2026-07-18
**Branch**: `evolve/EV-010-package-publish-validation`

### Scope (approved Phase 0–1)

Measure-first validation stack review (#703), then must-ship packages + HTTP msgspec:

1. `tac-validate` — full TAC product validation + all-product `docs/domain/` rule encoding (#698)
2. `iwxxm-validate` — Rust core + Python SDK; schemas bundled; **Rust Schematron implemented** (#699)
3. `tac2iwxxm` — convert + optional `[validate]` extras (#693)
4. Shared PyPI trusted publishing + release-tag CI/CD
5. **msgspec over pydantic** for high-churn request/response validation (breaking OK);
   full Render 12–13 redeploy (E10-15)
6. **Production** IWXXM XSD/modelling codegen
7. ADR-026 amending ADR-016

Also: F11 layer cost matrix / benches as gate before deepening Rust paths.

### Intake decisions

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E10-1 | Decision | Session open | S014 feature → 16-evolve |
| E10-2 | Decision | Cycle shape | One EV-010: #703 first, then #698→#699→#693 |
| E10-3 | Decision | Deploy | PyPI + release-tag CI; skip Render unless API wiring |
| E10-4 | Decision | PyPI names | `tac-validate`, `iwxxm-validate`, `tac2iwxxm` |
| E10-5 | Decision | Converter scope | Convert + optional `tac2iwxxm[validate]` |
| E10-6 | Decision | Schema assets | Bundle pinned vendor schemas in iwxxm-validate wheel |
| E10-7 | Decision | Rust Schematron | Design full this cycle; implement if time |
| E10-8 | Decision | msgspec vs pydantic | Expand msgspec into backend internal paths (ADR-016 amend) |
| E10-9 | Decision | docs/domain | Aggressive encode mined rules into packages |
| E10-10 | Decision | IWXXM model import | Prototype codegen from XSD / iwxxm-modelling |
| E10-11 | Decision | Must vs stretch | **Everything must-ship** — Rust Schematron, all-product domain rules, production codegen |
| E10-12 | Decision | Fn allocation | F11 #703+msgspec+codegen; F12 #698; F13 #699; F14 #693+PyPI CI |
| E10-13 | Decision | Routing | 01–12 incl. 03/06; skip 13 Render; 12 = PyPI+tags |
| E10-14 | Decision | ADR-016 | New ADR-026 — msgspec internals; pydantic only where OpenAPI needs it |
| E10-15 | Decision | HTTP / Render | **Breaking OK** — move high-churn validation off pydantic to msgspec (faster); full Render 12–13 this cycle (amends E10-3/E10-13 skip-13) |
| E10-16 | Decision | 01 document manifest | Mandatory + all recommended (API, deps, config, deploy, ADRs, acceptance) |
| E10-17 | Decision | msgspec HTTP scope | High-churn convert/validate/lint/decode → msgspec; auth/admin stay pydantic |
| E10-18 | Decision | OpenAPI / FE | Keep pydantic for OpenAPI schema integrations (thin aliases / export); update FE types same cycle |
| E10-19 | Decision | PyPI versions | `0.1.0` each; tags `tac-validate-v0.1.0`, `iwxxm-validate-v0.1.0`, `tac2iwxxm-v0.1.0` |
| E10-20 | Decision | tac2iwxxm extras | `[validate]` → depends on `tac-validate` + `iwxxm-validate`; convert works without |
| E10-21 | Decision | Domain rules depth | All 7 products; METAR/SPECI/TAF full; SIGMET/AIRMET/VAA/TCA templates+gates; cite-only paywall |
| E10-22 | Decision | Rust Schematron | Native Rust Schematron/SVRL in crate; parity vs lxml isoschematron |
| E10-23 | Decision | Codegen source | Production codegen from published **XSD**; modelling UML provenance; CI regen on pin bumps |
| E10-24 | Decision | Perf CI gates | Soft benches in build; hard-fail at publish (lib path + msgspec HTTP + wheel smokes) |
| E10-25 | Decision | PyPI publisher | GitHub Actions OIDC trusted publishing; one workflow per package version tag |
| E10-26 | Decision | User journeys | UJ-022, UJ-023, UJ-DEV-005 |
| E10-27 | Decision | Write specs | Proceed — standing doc deltas in 01; detail in 04 |
| E10-28 | Decision | 02 S2.M1 | msgspec = responses + post-Form Structs; multipart Form intake unchanged |
| E10-29 | Decision | 02 S8.M1 | Back-add config-spec + deploy PyPI OIDC notes |
| E10-30 | Decision | 02 S1.M1 | Keep must-ship 11B; 04 kill-switch via AskQuestion only |
| E10-31 | Decision | 03 tooling | Option D — rules/hooks + pypi_release_guard + pypi-release-checklist |
| E10-32 | Decision | Phase A checkpoint | 34B — commit docs+tooling then 04 |
| E10-33 | Decision | 04 milestones | M1 benches → M2 tac-validate → M3 iwxxm-validate Rust → M4 tac2iwxxm+OIDC → M5 msgspec HTTP → M6 08–13 |
| E10-34 | Decision | 04 schema bundle | Runtime subset only (XSD+SCH+catalogs); exclude modelling/translation bulk |
| E10-35 | Decision | 04 hard benches | p95 ≤0.85× lxml baseline (lib path); msgspec HTTP p95 ≤1.0× pydantic map; wheel smokes |
| E10-36 | Decision | 04 Rust SCH | New `packages/iwxxm-validate/rust` via maturin; lxml parity until cutover |
| E10-37 | Decision | 04 PyPI workflows | One GHA workflow + package matrix (39B) |
| E10-38 | Decision | 04 msgspec HTTP encode | Thin helper Struct→msgspec.json.encode→Response; pydantic OpenAPI-only (41A) |
| E10-39 | Decision | 04 wheels/CLI | manylinux/macOS/win maturin; tac-validate CLI; optional iwxxm-validate CLI (42A) |
| E10-40 | Decision | 04 XSD codegen | **xsdata** (+ xsdata-pydantic) for full Python models; adapt to msgspec/Rust as follow-on in-cycle tasks |
| E10-41 | Decision | 04 execution plan | Approved M1–M6 (~36 tasks) — 43A |
| E10-42 | Decision | 05 S1.M1 | feature-list F11 → ADR-027 xsdata (44A) |
| E10-43 | Decision | 05 S2.M1 | deploy/config matrix workflow (45A) |
| E10-44 | Decision | 05 S3.M1 | Add T5.6 H0c CORS re-verify (46B) |
| E10-45 | Decision | 05 S4.L1 | Add T3.7a + T3.8a tests (47A) |
| E10-46 | Decision | T3.3 crate stack | **A — xmloxide 0.4.x** (D-S014-T33-crates); reject B quick-xml+xsd-schema, C libxml |
| E10-46 | Decision | 06 tooling | 49A — rust/maturin/xsdata rule, Makefile stubs, uv deps, hook |

### Stage log

| Stage | Completed | Notes |
|-------|-----------|-------|
| 00-context / Phase 0–1 | 2026-07-18 | E10-1..27 locked; F11–F14 + routing 01–13 |
| 01-requirements | 2026-07-18 | Feature-list F11–F14; ADR-026; spec/api/journeys/test/deps deltas |
| 02-verify-plan | 2026-07-18 | PASS — S2.M1/S8.M1/S1.M1 = A; multipart clarification + config/deploy notes |
| 03-plan-tooling | 2026-07-18 | D — PyPI/msgspec guardrails; commits 1711e75 + 0717f13 |
| 04-tech-plan | 2026-07-18 | M1–M6 plan approved (43A); ADR-027 xsdata |
| 05-verify-tech | 2026-07-18 | PASS — 12 auto + 44A–47A applied |
| 06-tech-tooling | 2026-07-18 | 49A — maturin/xsdata/Makefile/hook delta |

---

## Cycle EV-009 — Live decode translations + preview UX (S013)

**Session**: S013-live-decode-preview-ux
**Features**: F9 (value-aware live decode + plain-language summary), F10 (workbench preview
clarity)
**Started**: 2026-07-16

### Scope (approved Phase 0)

- **F9** — `decode_tac` parses actual token values for all 7 TAC products (METAR/SPECI/TAF
  rich; SIGMET/AIRMET/VAA/TCA best-effort): `24/18` → "Temperature 24 °C, dewpoint 18 °C",
  `18004KT` → "Wind from 180° at 4 kt", etc. Backend builds a deterministic natural-language
  `summary` string in the decode-tac response; frontend renders it live as a "Plain language"
  block at the top of the decode panel (existing 300 ms debounce path).
- **F10** — Dedicated side-by-side IWXXM preview pane in the workbench anchoring
  Soft-preview / Live IWXXM output; clearer `LAYER12_SOFT_FAIL` status copy;
  `MISSING_TERMINATOR` downgraded to info-level hint with reworded copy + one-click
  "Add `=`" quick fix in the editor.

**Out**: LLM/AI-generated summaries (deterministic template text only); changes to Layer 1–2
validation semantics or Schematron rules; F5 history surfaces.

### Intake decisions

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E9-1 | Decision | Resume paused S011 vs new session | New session S013 + EV-009 |
| E9-2 | Decision | Scope parts | All four: value decode, NL summary, preview UX, friendlier lint copy |
| E9-3 | Ambiguity | Products for value-aware decode | All 7 (SIGMET/AIRMET/VAA/TCA best-effort) |
| E9-4 | Decision | Summary placement | "Plain language" block atop decode panel |
| E9-5 | Decision | Preview destination UX | Side-by-side IWXXM preview pane in workbench |
| E9-6 | Decision | Summary engine | Backend deterministic `summary` in decode-tac response |
| E9-7 | Decision | MISSING_TERMINATOR UX | Info-level reword + one-click "Add `=`" quick fix |
| E9-8 | Decision | Deploy this cycle | Yes — full 12–13 with smokes |

### Stage log

| Stage | Completed | Notes |
|-------|-----------|-------|
| 16-evolve Phase 0–1 | 2026-07-16 | Fn allocation F9/F10 + routing approved |
| 01-requirements | 2026-07-16 | Delta specs: feature-list F9/F10; spec; UJ-020/021; TC-F9/F10; api-contract; ADR-025 |
| 02-verify-plan | 2026-07-16 | PASS — 12 auto + 4 user-approved (S3.1–S3.4); severity enum fixed to `warning` |
| 04-tech-plan | 2026-07-16 | execution-plan.md approved — M1–M4, 21 tasks, no new deps |
| 05-verify-tech | 2026-07-16 | PASS — A1–A10 repo-verified; T3.6 note (fixes[] through hook) |
| 07–08 | 2026-07-17 | M1–M3 built; 08-verify-build PASS |
| 09–10 | 2026-07-17 | QA PASS (QA-001/002 resolved); E2E UJ-020/021 PASS |
| 11 | 2026-07-17 | F9 + F10 user-approved; 8/8 acceptance criteria |
| 12–13 | 2026-07-17 | Checklist approved; PR #723 merged; live smokes PASS |
| Close | 2026-07-18 | User approved deploy results (option 1); session closed |

**Completed**: 2026-07-18 — PR [#723](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/723) merge `4660602`; F9/F10 Done in production.

---

## Cycle EV-008 — F7 multi-product operator UI (S011)

**Session**: S011-f7-operator-ui
**Features**: F7 (primary); F5/F6/M4 touchpoints
**Issues**: #694, #702, #665, #666, #697 (#5 parent)
**Started**: 2026-07-13

### Scope (approved Phase 0)

Workbench, decode, Failed-TAC/partial preview, unified `tac_work_sessions` (R2′), BYO + admin
removal. Out: teaching CMS, paste-keys UI, AMHS/SWIM, quiet F5 parallel store.

### Key decisions

| ID | Decision | ADR |
|----|----------|-----|
| R2′ | Unified `tac_work_sessions` + migrate F5 | ADR-020 |
| R6 / #697 | BYO; remove `/admin`; `E2E_USER_*` | ADR-021 |
| Preview | `preview=true` on `/convert` | ADR-022 |
| Convert params | Wire bulletin/issuing/stop_on_error/validate; console log filter; `.tac` accept | ADR-023 |
| Input modes | AHL bulletin UI; COLLECT 501 placeholder; `log_level` + `include_nil_reasons` | ADR-024 |
| 04 A | Expand-cutover; CM6 pkgs; 300ms debounce; live IWXXM off; keep work-sessions paths; reuse CORS | — |

### Execution plan

`docs/sessions/S011-f7-operator-ui/reports/execution-plan.md` — M1–M6 / T1–T6 (pending approval).

---

## Cycle EV-001 — Convert & Convert&Send UI (S001)

**GitHub**: [#656](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/656)
**Session**: S001-convert-send-buttons
**Feature**: F1 (conversion UI + database send)
**Approved**: 2026-06-22

### Scope

**In scope**

- **Convert** button — conversion only (already present; verify UX).
- **Convert&Send** button — convert then immediately upload with fixed defaults.
- Success/failure toast feedback for the send step.

**Out of scope**

- Auto-clear input panel (#555 sibling).
- In-app error log preview (#555 sibling).
- Backend API changes.

### Decisions

| ID | Category | Decision |
|----|----------|----------|
| R1 | Ambiguity | Convert&Send uses fixed defaults: `format: iwxxm`, `destination: primary`, `includeOriginal: false`; no upload dialog |
| R2 | Decision | Keep all three actions: Convert, Convert&Send, Upload to Database |
| R3 | Scope | #656 only — exclude #555 auto-clear and log preview |

### Artifacts updated

- `docs/feature-list.md` — F1 UI actions
- `docs/user-journeys.md` — UJ-001 steps
- `docs/test-plan.md` — E2E module for convert-and-send
- `apps/frontend/` — `FileConverter`, shared `databaseUpload` util
- `apps/e2e/tac-file-upload-database.e2e.spec.ts` — one-click path

## Cycle EV-002 — CI consolidation (M5)

**Session**: S002-ci-consolidation (pending open)
**Feature**: M5 (Workspace tooling)
**Approved**: 2026-06-22
**Cycle type**: general

### Scope

**In scope**

- Consolidate PR/push CI from 13+ jobs across multiple workflows to **≤3 jobs** in a single `ci-cd.yml`:
  1. **validate** — format, lint, typecheck, gitleaks, actionlint/yamllint, config-guard, frontend npm audit
  2. **test** — unit tests + coverage (matrix: backend, auth, gifts, frontend, shared), integration matrix, Codecov uploads (thresholds unchanged)
  3. **deploy** — build/push images + Render deploy hooks (main push only, unchanged behavior)
- Extend **pre-commit** with fast hooks mirroring validate checks (dual-run: local + CI).
- **Delete** standalone PR/push workflows after merge: `secret-scan.yml`, `github-yaml-lint.yml`; fold `frontend-audit.yml` into validate job.
- Fix monorepo paths in any remaining references (legacy `backend/`, `frontend/`).

**Out of scope**

- Scheduled workflows: `e2e-tests.yml`, `load-tests.yml`, `vendor-sync.yml`
- Legacy manual workflow `test-coverage-95.yml` (delete if still present; no behavior change)
- Broken `smoke-tests-deploy.yml` (fix trigger reference or delete — not in PR/push path)
- Path-filtered CI (P2) — deferred to future cycle
- Coverage threshold changes (98% pytest `--cov-fail-under`, Codecov 95% per-service)
- Product feature changes (F1–F4)

### Decisions

| ID | Category | Decision |
|----|----------|----------|
| R1 | Intent | Reduce CI cost/complexity without lowering quality bar |
| R2 | Jobs | Target ≤3 jobs on PR: validate → test → (deploy on main only) |
| R3 | Local hooks | Extend pre-commit only (no Husky); fast hooks = format/lint/typecheck/secrets/yaml |
| R4 | Dual-run | Pre-commit runs fast checks locally; CI still runs all checks on every PR |
| R5 | Test structure | Single test job with matrix strategy for per-package unit+coverage |
| R6 | Workflows | Single `ci-cd.yml` for PR/push; delete secret-scan + yaml-lint; merge frontend-audit |
| R7 | Coverage | Keep per-service pytest 98% gates and Codecov 95% uploads exactly as today |
| R8 | Security | **Accepted trade-off:** deleted `secret-scan.yml` scanned full git history (`fetch-depth: 0`); validate/pre-commit gitleaks scans the working tree only. Historical commits are not re-scanned on PR/push. Rationale: pre-commit gitleaks on every commit + CI validate dual-run catches new leaks; full-history scan cost duplicated validate job checkout depth. Revisit if org policy requires history scans. |

### Acceptance criteria

- [ ] PR to main/dev runs ≤3 jobs (validate, test; deploy skipped on PR)
- [ ] All checks that ran before EV-002 still execute in CI (no dropped gates)
- [ ] Pre-commit fast hooks match quality-gates + secrets + yaml lint
- [ ] `make ci` behavior unchanged (still the local full-suite entry point)
- [ ] CI green on evolve branch before merge

### Artifacts to update

- `docs/feature-list.md` — M5 CI/pre-commit detail
- `docs/test-plan.md` — CI/CD section
- `.pre-commit-config.yaml` — fast hook split
- `.github/workflows/ci-cd.yml` — consolidated jobs
- Delete: `.github/workflows/secret-scan.yml`, `.github/workflows/github-yaml-lint.yml`, `.github/workflows/frontend-audit.yml`

## Cycle EV-003 — Issue #594 COR + input traceability (S002)

**GitHub**: [#594](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/594)
**Session**: S002-issue-594-feedback
**Feature**: F1 (METAR → IWXXM conversion + UI traceability)
**Approved**: 2026-06-22
**Cycle type**: feature (delta on F1)

### Scope

**In scope**

- **COR-after-time** — GIFTs `metarDecoder` grammar accepts ICAO `METAR STID ddHHmmZ COR ...` pattern; regression tests for both COR placements.
- **Input traceability** — `ConversionResult.tac_input` on API; **Source TAC** panel in results UI; per-line manual input mapping.

**Out of scope**

- `=` terminator (reporter notes resolved — monitor only).
- #555 siblings: auto-clear input, in-app error log preview.
- TAF COR / `METAR AMD COR` unless reporter confirms.
- REQ-016 migration rewrites.

### Decisions

| ID | Category | Decision |
|----|----------|----------|
| R1 | Uncertainty | `=` terminator — no work unless repro reappears |
| R2 | Decision | COR fix in GIFTs grammar (`ITime Cor?`); no separate backend preprocessor needed |
| R3 | Decision | `tac_input` on API + Source TAC display in UI |
| R4 | Scope | #594 bundle only — exclude #555 deferred items |

### Artifacts updated

- `packages/gifts/gifts/metarDecoder.py` — COR-after-time grammar
- `apps/backend/src/schemas/conversion.py`, `apps/backend/src/api.py` — `tac_input` field
- `apps/frontend/src/app/components/FileConverter.tsx` — Source TAC panel
- `docs/guides/API.md`, `docs/api-contract.md`, `docs/test-plan.md` — TC-001b
- `tests/bugs/test_bug_2026_06_22_issue_594_cor_after_time.py`
- `apps/e2e/tac-file-conversion.e2e.spec.ts`

## Cycle EV-004 — #555 UX + F5 work history + S003 Supabase (S004)

**GitHub**: [#555](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/555)
**Session**: S004-issue-555-feedback
**Features**: F1 (converter UX), F5 (user METAR work history), S003 (Supabase keys/runtime config)
**Approved**: 2026-06-23
**Cycle type**: feature (multi-Fn delta)

### Scope

**In scope**

- **#555 remaining UX (F1)** — Replace (not append) result cards on each successful convert; in-app collapsible error log from API `errors` / `issues`; same active session row updated on re-convert.
- **F5 work history** — Supabase `metar_work_sessions` table + RLS; backend REST CRUD; Draft → WIP → Finished + Failed lifecycle; auto-save (~3s debounce); resume most recent non-Finished session on login; converter sidebar (5 recent) + My METARs page; admin read-only browse; 30-day Draft auto-purge + soft-delete trash.
- **S003 Supabase config** — Service-key leak fix and runtime config wiring required before F5 DB work (merged into this cycle, not a separate hotfix branch).

**Out of scope**

- Re-opening S001 Convert / Convert&Send / send feedback (already shipped).
- Admin mutate/delete other users' sessions in v1.
- Backfill F5 from existing KV uploads.
- REQ-016 migration rewrites unrelated to this scope.

### Decisions

| ID | Category | Decision |
|----|----------|----------|
| R1 | Scope | **Single cycle** — merge #555 UX + F5 + S003 (user confirmed 2026-06-23) |
| R2 | Status | Four statuses: Draft, WIP, Finished, Failed — as F5 spec |
| R3 | Auth | Persistence requires login; guests may convert without save (no history) |
| R4 | Granularity | One row = one converter batch (manual textarea + file queue) |
| R5 | Results | Replace UI results **and** overwrite active session `converted_results` on re-convert |
| R6 | Resume | Auto-resume most recent non-Finished, non-deleted session on login |
| R7 | Finished | Finished only after successful DB send; convert-only stays WIP |
| R8 | S003 | Include Supabase key/config fixes in EV-004 before F5 migration |
| R9 | Retention | Draft auto-purge 30d (pg_cron); soft-delete trash 30d restore |
| R10 | Admin | Read-only browse all users' sessions in v1 |
| R11 | UI | Sidebar (5 recent) + My METARs page with status/date filters in v1 |
| R12 | Routing | Full delta path: 01→02→04→07→11 (+ optional 12–13 deploy) |
| R13 | History model | Current state per session row — no audit trail table in v1 |
| R14 | Guest users | Convert without login; persistence requires auth |
| R15 | Send failure | Stay WIP — retry send |
| R16 | Finished view | Read-only when opened from history |
| R17 | New session | Explicit New METAR button |
| R18 | Sidebar switch | Load session into converter; WIP row unchanged |
| R19 | Multi-device | Last-write-wins on auto-save |
| R20 | Error log | In-app panel + persist on session row |
| R21 | Admin UI | Separate admin page (read-only) |
| R22 | Results (#555) | Replace result cards on successful convert only |

### Artifacts to update

- `docs/feature-list.md` — F1 UX + F5 delivery note
- `docs/spec.md` — F5 §Data (sidebar count)
- `docs/user-journeys.md` — UJ-001 (#555), UJ-004 (F5)
- `docs/test-plan.md` — TC-001 delta, TC-004, TC-LIVE-006
- `docs/api-contract.md` — work-sessions (verify against build)
- `supabase/migrations/` — `metar_work_sessions` + RLS + pg_cron
- `apps/backend/` — work-sessions router + S003 config
- `apps/frontend/` — FileConverter (#555 + F5), My METARs page
- `packages/shared/` — WorkSession types (TBD in 04-tech-plan)
- `apps/e2e/` — UJ-001 + UJ-004 deltas

## Cycle EV-005 — Custom output filename for manual METAR input (S006)

**GitHub**: [#664](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/664)
**Session**: S006-issue-664-output-filename
**Features**: F1 (manual-input custom output filename UX) + F5 touch (persist the name on the work session)
**Approved**: 2026-06-25
**Cycle type**: feature (delta on F1; light F5 persistence touch)

### Scope

**In scope**

- Optional **Output filename** text input near the manual TAC textarea; placeholder `manual_input`;
  helper text that `.xml` is appended automatically. Disabled/read-only consistent with Clear button
  and Finished (read-only) sessions.
- **Sanitize** the base name (strip directory separators + illegal filename chars, drop any
  user-supplied extension, trim whitespace); empty after sanitize ⇒ fall back to `manual_input`.
- Apply the custom base name to **manual-input results only** (file uploads keep their uploaded
  filename): single download, ZIP entry, and result-card label/aria-label.
- **Multi-line** manual input suffixes `_1`, `_2`, … on the custom base (mirrors `manual_input_N`).
- Rename the **batch ZIP archive** itself to `${base}.zip` when a custom name is set; otherwise keep
  `converted_files_<ts>.zip`.
- **Persist** the custom name across reload for both guest (sessionStorage snapshot) and logged-in
  users — carried inside the existing `conversion_params` JSONB blob (no schema/migration/API change).

**Out of scope**

- Dedicated `output_filename` DB column / typed API field (rejected in favor of `conversion_params`
  carriage — keeps the build frontend-only; no Supabase migration, no API contract change).
- Renaming **file-upload** outputs (only manual input).
- New top-level feature ID — extends F1, lightly touches F5.
- REQ-016 unrelated rewrites.

### Decisions

| ID | Category | Decision |
|----|----------|----------|
| R1 | Decision | **Frontend-only build** — name manual-derived downloads client-side; no backend/API contract change. |
| R2 | Decision | Blank input ⇒ `manual_input` default (and `manual_input_N` per line); non-blank ⇒ sanitized user base name. |
| R3 | Scope | Custom name applies to **manual input only**; file uploads keep their uploaded filename. |
| R4 | Ambiguity (confirmed) | Multi-line manual input with a custom base suffixes `_1`, `_2`, … (user-confirmed 2026-06-25). |
| R5 | Decision | Custom name **persists across reload** (guest + logged-in) — user-confirmed full persistence. |
| R6 | Decision | Persistence carried via existing `conversion_params` JSONB blob — **no migration, no API/schema change** (chosen over a dedicated typed column to keep routing lean / frontend-only). |
| R7 | Decision | Rename the batch **ZIP archive** to `${base}.zip` when a custom name is set; else `converted_files_<ts>.zip`. |
| R8 | Allocation | Extend **F1** + touch **F5** persistence; no new Fn. |

### Artifacts to update

- `docs/feature-list.md` — F1 UI actions (output filename input)
- `docs/user-journeys.md` — UJ-001 optional custom-name step
- `docs/test-plan.md` — sanitizer + naming + ZIP + persistence cases
- `apps/frontend/src/app/components/FileConverter.tsx` — input, manual-result naming, downloads, snapshot wiring
- `apps/frontend/src/utils/` — filename sanitizer helper + `ConverterSnapshot` field carriage in `conversion_params`
- `apps/frontend/src/**/*.test.tsx` — unit coverage
- `apps/e2e/tac-file-conversion.e2e.spec.ts` — custom-name download assertion

## Cycle EV-006 — S008 F6 / validate packages / F8

**Session**: S008-general-tac-iwxxm-converter
**Features**: F6, F2→`iwxxm-validate`, F8
**Approved build**: 2026-07-12 (B→C)

### Decisions (build)

| ID | Category | Decision |
|----|----------|----------|
| D-S008-T21-sch | Ambiguity | `iwxxm-validate` mirrors current F2: lxml XSD best-effort + catalogs; Schematron via lxml when possible, else `SCHEMATRON_SKIPPED` (non-blocking) for xslt2; optional Docker/Saxon via env. TC-F6-032 unit suite asserts API + malformed fail + skip path + vendor pins; full M-sch Docker is a soft/separate gate. |

## Cycle EV-007 — Issue #655 TAC traceability UX (S010)

**GitHub**: [#655](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/655)
**Session**: S010-issue-655-tac-traceability
**Feature**: F6 (general converter UI — input traceability delta)
**Approved**: 2026-07-12
**Cycle type**: feature (UI-only delta on F6)

### Scope

**In scope**

- **Results traceability UX** — always show original TAC per conversion result in `FileConverter`:
  header snippet, TAC-derived card label where helpful, prominent Source TAC panel, multi-line
  index mapping; client-side fallback when API omits `tac_input`.
- **Tests** — extend TC-001b (Vitest + Playwright).
- **Deploy** — production frontend redeploy (12/13).

**Out of scope**

- API/schema changes (`tac_input` already on prod `/api/v1/convert`).
- ZIP sidecar, bulletin UI, convert-bulletin operator surface.

### Decisions

| ID | Category | Decision |
|----|----------|----------|
| R1 | Decision | F6 delta; UI-only |
| R2 | Decision | Full UX bundle: header snippet + derived label + prominent Source TAC + multi-line mapping |
| R3 | Decision | Frontend redeploy required |
| R4 | Scope | Lean routing — skip 02/03/05/06 |
