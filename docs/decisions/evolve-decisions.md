# Evolve Decisions

> Standing log of approved evolve-cycle scope and product decisions.
> Cycle metadata also recorded in `workflow-state.yaml` §`evolve_cycles`.

## Cycle EV-014 — Dissemination epic (#729 / #2 / #6) (S019)

**Session**: S019-dissemination-upload  
**Features**: TBD — **no F16+ until Phase 0 fully approved**  
**Issues**: [#729](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/729), [#2](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/2), [#6](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/6)  
**Started**: 2026-07-20  
**Branch**: `cursor/dissemination-upload-e25c`  
**Status**: Phase 0 intake **PARTIAL** — Batch 1+2 locked; Batch 3 **partial** (clarifications still needed)

### Intake (Batch 1 Assumed — AskQuestion waived / cloud written interview) — still locked

| ID | Decision |
|----|----------|
| Creds | One-shot session credentials (paste in UI); never persist / never saved profiles |
| UI | Drawer for send/upload destination + preflight |
| Schema | Require existing table matching versioned writer contract (no create-if-missing) |
| Q1=A | Convert-in-app then send IWXXM to user's Postgres |
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

### Intake (Batch 3 Assumed — AskQuestion waived / cloud written interview) — PARTIAL 2026-07-20

| ID | Status | Decision / note |
|----|--------|-----------------|
| Q10 | Recorded as stated; **[Ambiguity] unresolved** | User verbatim: *"we're dropping supabase support just user has to provide byo credentials"*. Open interpretations — **do not invent resolution**: **(1)** drop Supabase Auth+DB entirely → user-pasted credentials for auth AND data; **(2)** drop hosted Supabase for app auth in favor of another IdP; **(3)** only dissemination destinations are BYO-paste; app auth changes separately. |
| Q11 | **Not locked** | User asked for recommendation — pending agent recommendation + user confirm |
| Q12=B | Locked Assumed | Staging wis2box stood up in this project's infra |
| Q13=A | Locked Assumed | Real SMTP/submission to NWS Telecommunications Gateway (RTH Washington) |
| Q14=B | Locked Assumed + **[Ambiguity]** | Only B selected (saved/encrypted connection profiles out of scope). Confirm: only B out, or multi-select misunderstanding (A/C/D/E not selected)? |
| Q15=A | Locked Assumed | Keep Q8=C — block cycle close until Postgres + WIS2 + EDIS all green on real targets |

### Unresolved ambiguities (block Phase 0 full approval)

- **I-S019-EV014-Q10-supabase-byo** — Q10 meaning (1)/(2)/(3)
- **I-S019-EV014-Q11-pending-rec** — agent rec + user confirm before lock
- **I-S019-EV014-Q14-multiselect** — only-B-out vs multi-select misunderstanding

### Corpus contradictions noted (unresolved — for 01-requirements / ADR amend)

| Corpus | Tension |
|--------|---------|
| ADR-021 BYO deploy-env Supabase (no paste-keys UI) | vs Q5/Q10 in-app paste BYO + “dropping supabase support” |
| F5 work history on Supabase | vs Q10 drop-supabase reading |
| Non-goals: push sinks; paste-keys | vs Q8=C / Q12–Q13 live WIS2+EDIS + paste credentials |
| Batch 1 require-existing table | DDL/create-if-missing out (unless later reversed) |
| Batch 1 Q1=A convert-then-send | drag-drop external IWXXM maybe out |

### Notes

- Prior: S018/EV-013 closed 2026-07-20 (Q0=A waive leftover 08/09/11/12); #750 remarks live
- Do **not** invent feature ids F16+ in `feature-list.md` until Phase 0 fully approved
- **Batch 3 partial** — resolve Q10/Q11/Q14 ambiguities before routing lock / Phase 0 full approval
- **Close gate (Q15=A + Q8=C):** block cycle close until Postgres + WIS2 + EDIS green on real targets (staging wis2box in-project; EDIS → RTH Washington)

---

## Cycle EV-013 — Handle METAR remarks (#667) (S018)

**Session**: S018-metar-remarks-667  
**Features**: F6 (deepen)  
**Issues**: [#667](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/667)  
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
**Issues**: [#730](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/730)  
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
**Issues**: [#732](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/732)  
**Started**: 2026-07-19  
**Branch**: `evolve/EV-011-metar-lint-quality`  
**Completed**: 2026-07-20 (D-S015-EV011-phase4-close-1)  
**Merge**: PR [#742](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/742) → `b405a96`; deploy-smoke PR [#743](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/743)

### Close

| ID | Decision |
|----|----------|
| D-S015-EV011-phase4-close-1 | Close EV-011/S015; F15 **Done**; defer PyPI `tac-validate-v0.1.1`; close #732 |

### Scope (Phase 0–1 locked 2026-07-19)

1. Maintainable METAR lint **issue registry** (`info` / `warning` / `error`), additive and documented
2. Full [#732](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/732) METAR quality bar — lint, convert, IWXXM validate, API/UI path
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

**Completed**: 2026-07-18 — PR [#723](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/723) merge `4660602`; F9/F10 Done in production.

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

**GitHub**: [#656](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/656)  
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

**GitHub**: [#594](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/594)  
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

**GitHub**: [#555](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/555)  
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

**GitHub**: [#664](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/664)  
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

**GitHub**: [#655](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/655)  
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
