# Evolve Decisions

## Cycle EV-922-synthesis — Epic #922 close-out

**Opened:** 2026-09-03 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-922-epic-synthesis`  
**Issues:** [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)

| ID | Outcome |
|----|---------|
| D-EV922SYN-accept | **Epic investigation band complete** — all six spikes have Accepted ADRs |
| D-EV922SYN-matrix | Consolidated gap matrix: contract (ADR) vs runtime gap |
| D-EV922SYN-sequence | **Final** milestone sequence approved (Core → … → UIs) |
| D-EV922SYN-merge | PR stack #1125→#1130 merge order documented |
| D-EV922SYN-close | Close #923–#931 + epic #922 when PRs land on `stage` |
| D-EV922SYN-ui | Platform UIs #933–#938 unblocked after ADR merge (runtime deps noted) |
| D-EV922SYN-next | Priority runtime: `packages/workflows` (ADR-042) |
| D-EV922SYN-writeup | Session `reports/922-epic-synthesis.md` + [Context: epic-922-synthesis](../context/epic-922-synthesis.md) |

[Corpus: system-spec] §Platform logical layers [Corpus: product §F6] [Corpus: adr] ADR-037–042 [Corpus: decisions §EV-922-synthesis]

---


## Cycle EV-931 — Workflow definitions (#931)

**Opened:** 2026-09-03 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-931-spike-workflow-definitions-execute-message-workf`  
**Issues:** [#931](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/931), [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)

| ID | Outcome |
|----|---------|
| D-EV931-dsl | **Accept** declarative YAML WorkflowDefinition — reject BPMN/Temporal/Celery |
| D-EV931-execute | **Accept** `execute(message, workflow) -> WorkflowResult` contract (ADR-042) |
| D-EV931-package | **New** `packages/workflows` executor — apps remain thin callers |
| D-EV931-files | v1 workflows in git `workflows/*.yaml`; DB-managed deferred (#934) |
| D-EV931-secrets | No credentials in YAML — `${ENV:…}` / `secretRef:` only (ADR-021) |
| D-EV931-convert | HTTP `/convert` stays library primitive — not replaced by execute |
| D-EV931-mvp | Runtime MVP: tac→convert→xsd/sch → quarantine/archive only; gateways deferred |
| D-EV931-plan | DisseminationPlan runtime remains #936 — workflow documents hooks only |
| D-EV931-e2e | Skip e2e (no UI) |
| D-EV931-writeup | Session `reports/931-workflow-definitions.md` |

[Corpus: product §F6] [Corpus: product §F8] [Corpus: adr] ADR-037–042 [Corpus: decisions §EV-931]

---


## Cycle EV-927 — DisseminationGateway (#927)

**Opened:** 2026-09-03 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-927-dissemination-gateway`  
**Issues:** [#927](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/927), [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)

| ID | Outcome |
|----|---------|
| D-EV927-package | **Extend dissemination** — no packages/afs or gateways |
| D-EV927-gateway | **Accept** DisseminationGateway contract (ADR-041) over SinkAdapter |
| D-EV927-plan | DisseminationPlan + DeliveryReceipt documented; runtime deferred |
| D-EV927-edis | IWXXM not AFTN-safe raw; EDIS = AHL + ASCII TAC (#928) |
| D-EV927-wis2 | BYOC + DMZ via backend egress (#929) |
| D-EV927-writeup | Session `reports/927-dissemination-gateway.md` |

[Corpus: product §F16–F19] [Corpus: adr] ADR-030, ADR-041 [Corpus: decisions §EV-927]

---


## Cycle EV-926 — SQL adapters + mapping (#926)

**Opened:** 2026-09-03 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-926-sql-adapters-mapping`  
**Issues:** [#926](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/926), [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)

| ID | Outcome |
|----|---------|
| D-EV926-package | **Extend dissemination** — no new adapters package |
| D-EV926-mapping | **Accept** MappingConfig contract (ADR-040) |
| D-EV926-source | SourceAdapter protocol documented; runtime deferred |
| D-EV926-oracle | **Defer** Oracle v1 |
| D-EV926-896 | Hybrid URI connector + mapping (#896) |
| D-EV926-writeup | Session `reports/926-sql-adapters-mapping.md` |

[Corpus: product §F16] [Corpus: adr] ADR-030, ADR-040 [Corpus: decisions §EV-926]

---


## Cycle EV-925 — Canonical MET + staged validation (#925)

**Opened:** 2026-09-03 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-925-canonical-met-staged-validation`  
**Issues:** [#925](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/925), [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)

| ID | Outcome |
|----|---------|
| D-EV925-ir | **Keep-in-place** — `ConvertResult.ir` dict in tac2iwxxm; no core package extract |
| D-EV925-pipeline | **Accept** ADR-039 PipelineResult contract |
| D-EV925-stages | Map ADR-036 stages; `ca_eccc` StageResult = reference |
| D-EV925-canonical | Confirm one ICAO path + national overlays |
| D-EV925-writeup | Session `reports/925-canonical-met-staged-validation.md` |

[Corpus: product §F6] [Corpus: adr] ADR-036, ADR-039 [Corpus: decisions §EV-925]

---


## Cycle EV-924 — ConversionProfile contract (#924)

**Opened:** 2026-09-03 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-924-conversion-profile-contract`  
**Preset:** Standard · **Documenting→Implementing gate:** **closed** · **Issues:** [#924](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/924), [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)

| ID | Outcome |
|----|---------|
| D-EV924-fn | No new Fn — contract spike under F6 |
| D-EV924-contract | **Accept** normative ConversionProfile contract (ADR-038) |
| D-EV924-loader | Defer runtime loader — code plugins + registries remain SoT |
| D-EV924-overlays | Defer custom/operator packs to #933; v1 first-party catalog only |
| D-EV924-e2e | Skip e2e |
| D-EV924-writeup | Session `reports/924-conversion-profile-contract.md` |

### Corpus

[Corpus: product §F6] [Corpus: adr] ADR-013, ADR-036, ADR-038 [Corpus: api] [Corpus: decisions §EV-924]

---


## Cycle EV-922 — Platform package layout (#922 / #923)

**Opened:** 2026-09-03 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-922-epic-modular-conversion-validation-integration-d`  
**Preset:** Standard · **Documenting→Implementing gate:** **closed** · **Issues:** [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922), [#923](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/923)

| ID | Outcome |
|----|---------|
| D-EV922-fn | No new Fn — under F6 + F16–F19 architecture |
| D-EV922-slice | Slice A = #923 only (layout + gap matrix + milestone) |
| D-EV922-option | **Option C accepted** — logical layers only; defer Option B until #924–#927 (ADR-037) |
| D-EV922-milestone | Draft Core→Profiles→Validation→Adapters→Dissemination; revise after #924–#927 |
| D-EV922-issues | No migrate-now children until Option B/A approved |
| D-EV922-e2e | Skip e2e |
| D-EV922-writeup | Session `reports/923-platform-package-layout.md` |

### Corpus

[Corpus: product §F6] [Corpus: product §F16] [Corpus: system-spec] [Corpus: adr] ADR-013, ADR-030, ADR-036, ADR-037 [Corpus: decisions §EV-922]

---


## Cycle EV-099 — F9 SWXA/VONA structured decode (#1119)

**Opened:** 2026-09-03 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-099-f9-swxa-vona-structured-decode`  
**Preset:** Standard · **Documenting→Implementing gate:** **open** · **Issue:** [#1119](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1119)

| ID | Outcome |
|----|---------|
| D-EV099-fn | Deepen **F9** (+ F28/F32 quality surfaces) — no new top-level Fn |
| D-EV099-peers | Unlock peers: `vona_a7_1`, `swxa_a7_3`, `swxa_a7_4`, `swxa_a7_5` |
| D-EV099-residuals | Meaningful explicit residuals OK; **no** whole-TAC / `allow_any` body dump |
| D-EV099-convert | Convert annex3 peer XML must remain **bit-identical** |
| D-EV099-pattern | Mirror VAA/TCA structured `LABEL:` decode (EV-030 / #820) |
| D-EV099-e2e | Skip Playwright e2e this cycle — unit/integration + staging health |
| D-EV099-pr | PR into `stage` |

### Corpus

[Corpus: product §F9] [Corpus: product §F28] [Corpus: product §F32] [Corpus: decisions §EV-099] [Corpus: adr] ADR-025

---

## Cycle EV-097 — Deep-research domain handoff (skill + rule)

**Opened:** 2026-09-02 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-097-deep-research-domain-handoff`  
**Preset:** Standard · **Documenting→Implementing gate:** **open** · **Issue:** — (process/meta)

| ID | Outcome |
|----|---------|
| D-EV097-skill | Project skill `deep-research-domain-handoff` — evolve-invokable handoff prompts |
| D-EV097-rule | Optional `deep-research-domain-handoff.mdc` — AskQuestion gates; no silent promote |
| D-EV097-promote | Promote/conflict via existing `mine-domain-sources` |
| D-EV097-corpus | No new minimal CORPUS member; decisions + domain hub |
| D-EV097-wire | protocol-card + skill-routing only (no pack evolve rewrite) |
| D-EV097-pr | PR into `stage` |
| D-EV097-scope | No mining pass / no product code this cycle |

### Corpus

[Corpus: decisions §EV-097] [Corpus: product] (process — no Fn)

Detail: [ev-097-deep-research-domain-handoff.md](ev-097-deep-research-domain-handoff.md)

---

## Cycle EV-981 — Optional propagate decode residuals into remarks / HRT (#981)

**Opened:** 2026-08-31 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-981-feature-optional-propagate-decode-residuals-into`  
**Preset:** Standard · **Documenting→Implementing gate:** **closed** · **Issue:** [#981](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/981)  
**Context:** [propagate-residuals-to-remarks](../context/propagate-residuals-to-remarks.md)

| ID | Outcome |
|----|---------|
| D-EV981-fn | Deepen **F6** / **F9** / **F7.q** — no new top-level Fn |
| D-EV981-flag | `propagate_residuals_to_remarks` on convert (+ convert-bulletin) |
| D-EV981-default | Default off; omitted → profile default |
| D-EV981-annex3 | annex3 / ICAO_2025 default **off** (must not silently retain residuals) |
| D-EV981-profile-wire | Profile-default hook shipped; **no** other profile defaults enabled this cycle |
| D-EV981-issue | When folded: info ConvertIssue e.g. `RESIDUALS_PROPAGATED_TO_REMARKS` + provenance |
| D-EV981-uj | UJ-026 unchanged when off; **UJ-070** when on |
| D-EV981-qm | Detail `residuals_propagated_to_remarks` + residuals-panel indicator (fixtures stay precomputed) |
| D-EV981-adr | No ADR unless tech-plan forces standing policy |
| D-EV981-pr | PR into `stage` |
| D-EV981-ux | Plain-language operator copy; no internal doc refs |
| D-EV981-feasible | Feasibility **FEASIBLE**; proceed tech-plan (2026-08-31) |
| D-EV981-emit-target | Fold into XML only where profile already emits remarks/HRT; **annex3:** no invented free-text; flag-on + residuals → info `RESIDUALS_PROPAGATED_TO_REMARKS` message documents **no XML target**; QM fold bool stays false |
| D-EV981-dedup | Append only residuals not already covered by remarks-retain / RMK→HRT |
| D-EV981-zip | `/convert-zip` inherits same Form field + resolve semantics |
| D-EV981-resolve | Omitted → profile default (annex3/`ICAO_2025` off); explicit override wins; no other profile defaults this cycle |

### Corpus

[Corpus: product §F6/F9/F7.q] [Corpus: api] [Corpus: journeys] [Corpus: tests] [Corpus: decisions §EV-981]

---


## Cycle EV-096 — Harden Cursor rules/skills from CI footguns (#1096)

**Opened:** 2026-08-31 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-096-ci-rules-skills-harden`  
**Preset:** Standard · **Documenting→Implementing gate:** **open** · **Issue:** [#1096](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1096)

| ID | Outcome |
|----|---------|
| D-EV096-scope | Process/DX only — no product Fn |
| D-EV096-docs | test-plan delta + `ev-096-ci-rules-skills-harden.md`; skip Feature/Spec/Journeys/ADR |
| D-EV096-top3 | FE 100% coverage · E2E Full on promote · Mutation pnpm pin |
| D-EV096-mutation | Document + fix packageManager dual-spec this cycle |
| D-EV096-vendor | Document only; no hand-edit `vendor/schemas` |
| D-EV096-1095 | Verify-only existing home-path CI guard |
| D-EV096-pr | PR into `stage` |
| D-EV096-ux | No user-facing internal doc refs |

### Corpus

[Corpus: tests] [Corpus: decisions] [Corpus: deploy]

---

## Cycle EV-094 — Thin/compat national deepen (#1098)

**Opened:** 2026-08-31 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-094-thin-compat-national-deepen`  
**Preset:** Standard · **Documenting→Implementing gate:** **open** · **Issue:** [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098)  
**Prior:** #920 closed (EV-089 / PR #1087) — do not reopen  
**Build:** M1–M7 complete on stacked PRs (#1099–#1106 tip); catalog six packs `implemented`

| ID | Outcome |
|----|---------|
| D-EV094-products | Keep EV-089 allowlists (do not drop IN SIGMET or HK SIGMET/VAA) |
| D-EV094-speci-expand | Add SPECI to `KR_KMA` and `JP_JMA` convert allowlists + fixtures |
| D-EV094-in-taf | `IN_IMD` / `in_imd` **lint profile overlay**: TAF omit TX/TN → registered info awareness code; convert stays core IWXXM |
| D-EV094-jp-airmet | Keep AIRMET out of JP allowlist |
| D-EV094-uk-mil | Civil-only; military colour OOS |
| D-EV094-fixtures | Official preferred; aggregator TAC OK with URL + UTC attribution |
| D-EV094-order | UK → BR → KR → JP → IN → HK; one PR per pack; Spec all six then Build continuum |
| D-EV094-gamet | Reaffirm parse-only |
| D-EV094-china | Omit |
| D-EV094-xsd | No national XSD invent |
| D-EV094-exchange | #921 OOS |
| D-EV094-issue | Tracking [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098) |
| D-EV094-ui | N/A |
| D-EV094-req | R0:2 · R1:1 · R2 overlay · R3:1 locked 2026-08-31 |

### Corpus

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: adr/ADR-036] [Corpus: tests] [Corpus: decisions]

---

## Cycle EV-093 — Light semantic + exchange profile picker deepen (#1024)

**Opened:** 2026-08-31 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-093-light-profile-picker-deepen`  
**Preset:** Standard · **Documenting→Implementing gate:** **open** · **Issue:** [#1024](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1024)  
**Prior:** EV-090 exchange picker · EV-091 drawer overlay

| ID | Outcome |
|----|---------|
| D-EV093-intake | Option 2 deepen — G1–G5 after EV-090/091 partial ship |
| D-EV093-g2 | **A1** — all registered canonicals in Profile select + legacy `annex3` / `iwxxm_us` |
| D-EV093-wire | **B1** — Form `semantic_profile` + uppercase OpenAPI ids (`ICAO_2025`, …) |
| D-EV093-req | R1 recommended — FR-01..08; AC 1–6; TC-EV093-001..006 |
| D-EV093-ui-preview | **Yes** — local non-deployed preview before merge (not H4–H5 proof) |
| D-EV093-trust | Profile help: not destinations/credentials; not editable overlays (#924 / #933) |
| D-EV093-trust-layout | **A+B+C** — help icons/tooltips + one-line summary under bar + collapsed “What’s this?” details; controls-only `product-profile-bar` (no inline wrap) |
| D-EV093-hygiene | After Build: close #1024; update #912 checklist |
| D-EV093-scale | standard |
| D-EV093-kg | Fail-open — peer retrieve skip; keep-local EV-090/091; adopt alias-window + verify gates |
| D-EV093-gate | **Open Build** — implement M1–M5 on `evolve/EV-093-light-profile-picker-deepen` → PR `stage` |

### Corpus

[Corpus: product §F7] [Corpus: product §F35] [Corpus: product §F36] [Corpus: adr/ADR-036] [Corpus: api] [Corpus: journeys] [Corpus: tests] [Corpus: domain-profiles]

---

## Cycle EV-091 — Dissemination drawer restore (#898 / #1089)

**Opened:** 2026-08-30 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-091-dissemination-drawer-restore`  
**Preset:** Standard · **Documenting→Implementing gate:** open · **Issues:** [#898](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/898), [#1089](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1089)

| ID | Outcome |
|----|---------|
| D-EV091-intake | Full #898 restore (Convert&Send + Disseminate + Upload to Database) + #1089 drawer exchange overlay |
| D-EV091-db | URI-BYOC for F16 DBs; do **not** wait on #896 connector spike |
| D-EV091-qol | Connection-first / per-sink schema checks retained (former #795) |
| D-EV091-overlay | Drawer Exchange profile select; default `GLOBAL_AFS`; convert-before-send wires `exchange_profile` |
| D-EV091-security | ADR-021/029/030 unchanged |
| D-EV091-uj053 | Invert UJ-053 / TC-EV042-001 to destinations **visible** (TC-EV091-001); restore UJ-027–030 operator UI |
| D-EV091-scale | standard |
| D-EV091-gate | **open** (Build 2026-08-30) — implement T1–T7 |
| D-EV091-build | Commits `c1f5321f` / `cefc123d` / `e4eb50a6` on `evolve/EV-091-dissemination-drawer-restore` |
| D-EV091-inline-doc | Full-tree **WAIVE** — delta `VERIFY_DOC_PATHS` PASS (DisseminationDrawer / FileConverter / operatorDisseminationUi); remaining ~107 → [#1090](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1090). Bar: `docs/decisions/inline-documentation-verify.md` |
| D-EV091-tech-debt | [#1090](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1090) — pack checker harden + remaining inline-doc fill; does not block #898/#1089 PR |

### Corpus

[Corpus: product §F16–F19] [Corpus: product §F36] [Corpus: adr/ADR-021] [Corpus: adr/ADR-029] [Corpus: adr/ADR-030] [Corpus: adr/ADR-036] [Corpus: journeys] [Corpus: tests] [Corpus: api] [Corpus: verifier]

---

## Cycle EV-090 — Exchange overlay deepen + light picker (#921 / #913 / #1024)

**Opened:** 2026-08-30 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-090-exchange-overlay-deepen`  
**Preset:** Standard · **Documenting→Implementing gate:** closed · **Issues:** [#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921), [#913](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/913), [#1024](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1024)

| ID | Outcome |
|----|---------|
| D-EV090-intake | Option 3 — mining deepen + light picker; drawer #898 out |
| D-EV090-routing | Standard band + e2e for picker; gate closed until documenting verify |
| D-EV090-req | R1 recommended: 1a no local UI preview; 2a promote existing mining notes; 3a workbench Exchange select (default `GLOBAL_AFS`, all registered ids, ignored on convert-only); 4b close #921 when mining+picker land and spawn child for drawer |
| D-EV090-packaging | No new packaging rules this cycle — COLLECT baseline retained; gaps documented only |
| D-EV090-ui | Light Exchange control beside semantic Profile (`profile-type-select` pattern); plain-language copy; no destinations/credentials |
| D-EV090-tests | TC-EV090-* (catalog/provenance + FE unit + H4–H5 e2e); preserve TC-EV063/065/086 |
| D-EV090-adr | ADR-036 cite-only (no amend unless Build finds boundary gap) |
| D-EV090-kg | Cross-project Neo4j checkpoint (F107): session-open retrieve sparse — **adopt** verification-gate discipline; **keep-local** prior #921 / EV-065 / EV-086 product history; no Pattern to waive |
| D-EV090-gate | **open** (Build 2026-08-30) |
| D-EV090-build | Commit `38161462` on `evolve/EV-090-exchange-overlay-deepen` |

### Corpus

[Corpus: product §F36] [Corpus: product §F7] [Corpus: domain-profiles] [Corpus: domain] [Corpus: adr/ADR-036] [Corpus: tests] [Corpus: api] [Corpus: journeys]

---

## Cycle EV-089 — Thin/compat national packs (#920)

**Opened:** 2026-08-29 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-089-thin-compat-national-packs`  
**Preset:** Standard · **Documenting→Implementing gate:** closed · **Issue:** [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920)

| ID | Outcome |
|----|---------|
| D-EV089-order | UK → BR → KR → JP → IN → HK; one profile per PR |
| D-EV089-china | Omit China |
| D-EV089-gamet | Parse-only; BR fixtures only; no IWXXM emit; no convert enum |
| D-EV089-jp-va | JP VAA yes; AIRMET no |
| D-EV089-hk | HK SIGMET + VAA fixtures |
| D-EV089-xsd | No invented national XSD |
| D-EV089-path | Thin path C/N ±D (EV-088 playbook) |
| D-EV089-exchange | SAM note on BR only; #921 packaging OOS |
| D-EV089-ui | N/A — no FE picker |
| D-EV089-child-issues | Spec does not open GH children |
| D-EV089-req | R0–R4 recommended approved 2026-08-29 |
| D-EV089-gate | **open** (Build 2026-08-29) |
| D-EV089-build | Registry + fixtures + TC-EV089 on `evolve/EV-089-thin-compat-national-packs` @ `519d319e` |

### Corpus

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: adr/ADR-036] [Corpus: tests] [Corpus: api]

---

## Cycle EV-088 — Profile engineering enablement (#1044)

**Opened:** 2026-08-29 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-088-profile-eng-enablement`  
**Preset:** Standard · **Documenting→Implementing gate:** open · **Issue:** [#1044](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1044)

| ID | Outcome |
|----|---------|
| D-EV088-req | Recommended AC — playbook, templates, scaffold, TC-EV088; waive full CA issue-body rewrite |
| D-EV088-gate | **open** (Build 2026-08-29) |
| D-EV088-ui | N/A — no FE |
| D-EV088-pr | [PR #1086](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1086) → `stage`; CI green |
| D-EV088-inline-doc | Full-tree WAIVE (brownfield); scaffold script documented; bar in `inline-documentation-verify.md` |

### Corpus

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: adr/ADR-036] [Corpus: tests]

---

## Cycle EV-087 — AU_BOM + NZ_CAA_MET semantic P1 kickoff

**Opened:** 2026-08-28 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-087-au-nz-semantic-profiles`  
**Preset:** Standard · **Documenting→Implementing gate:** closed · **Issues:** [#917](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/917), [#918](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/918), [#913](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/913), [#1044](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1044)

### Locked requirements

| ID | Outcome |
|----|---------|
| D-EV087-inter-emit | Parse INTER distinctly; emit `TEMPORARY_FLUCTUATIONS` + preserve INTER in remarks/diagnostics; never invent IWXXM enum |
| D-EV087-taf3 | `product=TAF`; RMK `TAF3` / `TAF3 VALID TL` → flag `AU.TAF.TAF3` |
| D-EV087-nz-domestic | Parse domestic extras to IR; core IWXXM only if attested; else remarks + diagnostics |
| D-EV087-catalog | `AU_BOM` + `NZ_CAA_MET` → P1 / in_progress |
| D-EV087-depth | Registry + stubs + mining + goldens + parse/lint; convert where clear; SIGMET ICAO base |
| D-EV087-ui | N/A — no FE picker |
| D-EV087-xsd | No AU/NZ national extension pin (none published) |
| D-EV087-arch | ADR-036 overlay model confirmed |
| D-EV087-feasibility | **FEASIBLE** — library-first kickoff; INTER emit policy locked |
| D-EV087-tech-plan | M1–M5 registry→AU parse→INTER emit→NZ→docs promote |
| D-EV087-draft-docs | catalog P1, stubs, mining, F36, test-plan TC-EV087, api-contract ids |
| D-EV087-gate | **open** (`open_build` 2026-08-28) |
| D-EV087-build | M1–M5 implemented on `evolve/EV-087-au-nz-semantic-profiles`; TC-EV087-001..006 green |
| D-EV087-pr | [PR #1085](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1085) → `stage`; tip `aa1f3e90`; CI green |
| D-EV087-verify-build | 08 PASS — `reports/verification-report.md` |
| D-EV087-qa | 09 PASS — `reports/qa-report.md` (no UI; H4–H5 N/A) |
| D-EV087-verify-tests | Pack `tests` FAIL from FE Vitest load timeouts — harden FileConverter + add `make test-fast` for pack-run fallback |
| D-EV087-inline-doc | Full-tree inline-doc WAIVE (brownfield); delta VERIFY_DOC_PATHS PASS; bar in `docs/decisions/inline-documentation-verify.md` |
| D-EV087-adv-swxa | Quality sticky SWXA Fail:1 pre-existing annex3 residual — not EV-087; pack job PASS |
| D-EV087-adv-h4h5 | H4–H5 N/A waived (D-EV087-ui); staging smoke after merge if needed |
| D-EV087-adv-e2e | E2E Full skipped on PR→stage; E2E Smoke PASS |

### Corpus

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: adr/ADR-036] [Corpus: tests] [Corpus: api]

---

## Cycle EV-080 — Universal 100% unit coverage (EV-080-unit-coverage-100)

**Opened:** 2026-08-27 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-080-unit-coverage-100`  
**Preset:** Full · **Documenting→Implementing gate:** closed · **Issue:** [#1077](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1077)

### Locked intake / requirements

| ID | Outcome |
|----|---------|
| D-EV080-goal | 100% line+branch unit coverage; CI fail under 100 |
| D-EV080-out | vendor; generated xsd/codegen; Playwright as unit surface |
| D-EV080-scripts-py | All `scripts/**/*.py` cov ≥100% |
| D-EV080-scripts-sh | bats-core test for **every** `scripts/**/*.sh` |
| D-EV080-bats | **bats-core** in CI (not shunit2) |
| D-EV080-fe-excludes | Remove executable FE Vitest coverage excludes |
| D-EV080-init-omit | Remove `**/__init__.py` coverage omit |
| D-EV080-manifest | Delta docs approved; skip config/api/deploy |
| D-EV080-issue | #1077 |
| D-EV080-gate | **open** (2026-08-27 Spec→Build) |
| D-EV080-docs | draft-docs applied: ADR-007, typing-policy, test-plan TC-EV080-*, feature-list, dependency-inventory, spec component row, inventory YAML seed |
| D-EV080-feasibility | **FEASIBLE** multi-PR; fill-before-flip; see session reports/feasibility.md |
| D-TP080-1..7 | **approved** inventory path, bats tree, scripts cov make target, fill-before-flip, new TC-EV080 guards, sticky 100, base stage |
| D-TP080-m2-split | **yes** M2a packages / M2b tac2iwxxm+backend+flip |
| D-TP080-approved | tech-plan approved 2026-08-27 |
| D-VT080-pass | verify-tech **PASS**; product↔tech PASS; connectivity N/A |
| D-VT080-med-low | **Approve all** V-M1..V-M5, V-L1..V-L2 |
| D-TT080-delta | tech-tooling: make targets + bats/scripts READMEs + rule floors + CI stub `if: false` |
| D-TT080-hook | **coverage-advisory.sh** afterFileEdit |
| D-EV080-doc-verify | documenting `bin/verify` **12/12 PASS** |
| D-EV080-build-open | Gate open; branch `evolve/EV-080-unit-coverage-100`; M1 started |
| D-EV080-m1 | **completed** inventory SoT + TC-EV080-001 (10 pass) + m1-gap-ranked |
| D-EV080-m1-pr | [#1078](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1078) `[M1] EV-080 coverage inventory @ 100 floor` → stage @ `ba41b804` |
| D-EV080-m2a | **completed** packages→100%: worker/shared/dissemination/iwxxm-validate/tac-validate/auth — [#1079](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1079) merged @ `cba32156` |
| D-EV080-m2b | **completed** tac2iwxxm + backend fills + Python fail_under/CI flipped to 100 |
| D-EV080-m2b-t22 | **completed** tac2iwxxm 100% line+branch (`test_coverage_gaps_ev080.py` + small testability/pragmas) |
| D-EV080-m2b-t23 | **completed** backend 100% line+branch (`test_ev080_m2b_coverage_gaps.py` + unit extensions) |
| D-EV080-m2b-t24 | **completed** fail_under / CI `--cov-fail-under` / per-file default → 100; `__init__.py` omit removed |
| D-EV080-m2b-t25 | **completed** TC-EV080-002/003 + legacy gate asserts updated to 100 |
| D-EV080-m2b-pr | [#1080](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1080) `[M2b] EV-080 tac2iwxxm+backend → 100% + flip gates` → stage @ `693d7739` **merged** |
| D-EV080-m3 | **completed** Vitest FE + shared → 100% (exclude purge + fills + thresholds) |
| D-EV080-m3-t31 | **completed** executable FE coverage.exclude purged (fixtures/generated kept) |
| D-EV080-m3-fills | **completed** FE unit fills to 100% stmts/branches/funcs/lines (3817/3817, 2837/2837) |
| D-EV080-m3-flip | **completed** Vitest thresholds FE+shared → 100; TC-EV080-004/005 |
| D-EV080-m3-pr | [#1081](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1081) `[M3] EV-080 Vitest 100% + exclude purge` → stage **merged** |
| D-EV080-m4 | **completed** scripts Python cov 100% + bats for all 56 `.sh` + CI `scripts-coverage` enabled |
| D-EV080-m4-t41 | **completed** `tests/scripts/` harness + `make test-coverage-scripts` fail_under 100 |
| D-EV080-m4-t43 | **completed** `tests/bats/` mirrors `scripts/**/*.sh` + helpers stubs (NFR-006) |
| D-EV080-m4-guards | **completed** TC-EV080-006..008 |
| D-EV080-m4-pr | [#1082](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1082) `[M4] EV-080 scripts py cov 100% + bats-core` → stage |
| D-EV080-m5 | **completed** TC-EV080-009 docs guard; sticky coverage comment cites 100% gate; TC-EV080-010 via inventory |

### Delivered

| Milestone | Scope | PR |
|-----------|--------|-----|
| M1 | Inventory @ floor 100 + TC-EV080-001 | [#1078](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1078) |
| M2a | Packages → 100% | [#1079](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1079) |
| M2b | tac2iwxxm + backend + flip gates | [#1080](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1080) |
| M3 | Vitest FE + shared → 100% | [#1081](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1081) |
| M4 | Scripts py cov + bats-core | [#1082](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1082) |
| M5 | Docs/ADR audit + sticky 100 + closeout | (same #1082) |

**Issue:** [#1077](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1077) — close after #1082 merges to `stage`.

### Milestones (planned)

M1 inventory → M2 Python 100% → M3 TS 100% → M4 scripts (py+bats) → M5 ADR/docs/CI closeout

**Tests:** TC-EV080-001..010 · **Requirements:** session `requirements.md`

[Corpus: adr/ADR-007] [Corpus: tests] [Corpus: tech-spec]

---

## Cycle EV-085 — US_FAA_NWS #919 closeout (EV-085-us-919-closeout)

**Opened:** 2026-08-26 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-085-us-919-closeout`  
**Preset:** Standard · **Documenting→Implementing gate:** open · **Issue:** [#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919)  
**Parent:** #912 · **Prior:** EV-084 merged to `stage` @ `a0b85366` ([#1072](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1072))

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV085-goal | Close #919 acceptance + F36 Build item 1 |
| D-EV085-in | M20 audit; M21 if mined fixtures; M22 SWXA/TCA thin rules; docs; TC-EV085-* |
| D-EV085-out | M14 / #1025 alias cutover (Oct 2026); #921; stage→main promote |
| D-EV085-accept | Close #919 with waivers for M14 + §12.7.2 additive RMK |
| D-EV085-gate | **open** |

### Delivered

| Milestone | Scope |
|-----------|--------|
| M20 | Manifest audit + `negative_cases`; catalog + stub sync; TC-EV085-001..005 |
| M21 | No additional §12.7 rows — documented residual (no mined fixtures) |
| M22 | `US_SWXA_SATCOM_NOT_ISSUED`, `US_TCA_OBSERVED_CB_NOT_PROVIDED` + profile negatives |

**Branch:** `evolve/EV-085-us-919-closeout`

[Corpus: product §F36] [Corpus: domain-profiles §US_FAA_NWS] [Corpus: tests]

---

## Cycle EV-084 — US_FAA_NWS M19 (#919) (EV-084-us-waus-multisection)

**Opened:** 2026-08-25 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-084-us-waus-multisection`  
**Preset:** Standard · **Documenting→Implementing gate:** open · **Issue:** [#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919)  
**Parent:** #912 · **Prior:** EV-083 merged to `stage` @ `0e3e3919` · **Merged:** [#1072](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1072) @ `a0b85366`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV084-goal | M19 — full WAUS multi-section bulletin (ICE + OTLK + FRZLVL + VOR FROM) |
| D-EV084-in | `FROM … TO …` VOR chains; FRZLVL after OTLK; multisection fixture/golden |
| D-EV084-out | M14 / #1025 alias cutover (Oct 2026) |
| D-EV084-gate | **open** — operator chose M19-only |

### Delivered (local)

| Milestone | Scope |
|-----------|--------|
| M19 | WAUS bulletin: CONUS ICE + polygon geometry + inline FRZLVL + outlook + `FreezingLevelForecast` |

**Branch:** `evolve/EV-084-us-waus-multisection` (local, uncommitted)

---

## Cycle EV-083 — US_FAA_NWS M17–M18 (#919) (EV-083-us-airmet-updt-frzlvl)

**Opened:** 2026-08-25 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-083-us-airmet-updt-frzlvl`  
**Preset:** Standard · **Documenting→Implementing gate:** open · **Issue:** [#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919)  
**Parent:** #912 · **Prior:** EV-082 merged to `stage` @ `9e7e125c` · **Merged:** [#1071](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1071) @ `0e3e3919`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV083-goal | M17–M18 — CONUS `UPDT` header + FRZLVL-only subsection / `FreezingLevelForecast` |
| D-EV083-in | CONUS/Hawaii product line parse; `BTN FRZLVL`; standalone FRZLVL section emit |
| D-EV083-out | Promote; #1025 M14; full WAUS bulletin stack |
| D-EV083-gate | **open** — operator chose M17+M18 after EV-082 closeout |

### Delivered

| Milestone | Scope |
|-----------|--------|
| M17 | `AIRMET <series> UPDT` header + FAA `ZONE WA` issue time + inline FRZLVL vertical |
| M18 | `FRZLVL...` subsection → `iwxxm-us:FreezingLevelForecast` |

**Tests:** TC-EV083-001..005 · **1037 passed** · **97.25%** cov · per-file gate OK  
**Merged:** [#1071](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1071) → `stage` @ `0e3e3919` · **Staging smoke:** green ([CI run](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32914128391))

---

## Cycle EV-082 — US_FAA_NWS M15–M16 (#919) (EV-082-us-airmet-outlook)

**Opened:** 2026-08-25 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-082-us-airmet-outlook`  
**Preset:** Standard · **Documenting→Implementing gate:** open · **Issue:** [#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919)  
**Parent:** #912 · **Prior:** EV-081 merged to `stage` @ `386a9676` · **Merged:** [#1070](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1070) @ `9e7e125c`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV082-goal | M15–M16 — AIRMET outlook (`OTLK VALID`) + multi-area sub-periods |
| D-EV082-in | Outlook parse/emit; `validTimeSubPeriod`; multi-member collections; fixtures |
| D-EV082-out | Promote; #1025; CONUS `UPDT` header; FRZLVL-only sections |
| D-EV082-gate | **open** — operator chose outlook slice after EV-081 closeout |

### Delivered

| Milestone | Scope |
|-----------|--------|
| M15 | `OTLK VALID` outlook → forecast analysis + `AIRMETEvolvingConditionExtension` |
| M16 | AND-joined multi-area bodies → multiple evolving members |

**Tests:** TC-EV082-001..003 · **1032 passed** · **97.39%** cov · per-file gate OK  
**Branch:** `evolve/EV-082-us-airmet-outlook` · **PR:** [#1070](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1070) → `stage`

---

## Cycle EV-081 — US_FAA_NWS M10–M13 (#919) (EV-081-us-m10-m13)

**Opened:** 2026-08-25 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-081-us-m10-m13`  
**Preset:** Standard · **Documenting→Implementing gate:** catchup_verify (code landed; verify after spec catch-up) · **Issue:** [#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919)  
**Parent:** #912 · **Prior:** EV-080 merged to `stage` @ `079339e6` · **Merged:** [#1069](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1069) @ `386a9676`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV081-goal | M10–M13 — weather hazards, convective SIGMET (WST), structured VIS verify, US TAF lint |
| D-EV081-in | `iwxxm_us.py` hazard emit; WST parse/emit + fixture; M7 VIS assert; TAF lint codes |
| D-EV081-out | Promote; M14 / #1025; outlook AIRMET; FE; CA_ECCC |
| D-EV081-scale | Standard evolve angles |
| D-EV081-gate | Operator chose **catchup_verify** (2026-08-25) — no commit/PR until asked |

### Delivered

| Milestone | Scope |
|-----------|--------|
| M10 | `AIRMETWeatherHazards` / `SIGMETWeatherHazards` emit in `iwxxm_us.py` |
| M11 | `CONVECTIVE SIGMET` parse + `emit_convective_sigmet_annex3` + WST fixture |
| M12 | Structured VIS — verified via existing M7 sector/tower/var goldens (TC-EV081-005) |
| M13 | `US_TAF_BECMG_FORBIDDEN` + `US_TAF_TEMPO_MAX_4H` lint under `iwxxm_us` |

**Tests:** TC-EV081-001..005 · **Branch:** `evolve/EV-081-us-m10-m13`

---

## Cycle EV-080 — US_FAA_NWS VOR reference geometry (#919 M9) (EV-080-us-vor-geometry)

**Opened:** 2026-08-24 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-080-us-vor-geometry`  
**Preset:** Full · **Documenting→Implementing gate:** open · **Issue:** [#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919)  
**Parent:** #912 · **Prior:** EV-079 merged to `stage` @ `d2749cd5`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV080-goal | M9 — `ReferencePointGeometryParser` for US SIGMET VOR/airport reference geometry |
| D-EV080-in | `geometry/reference_point.py`; VOR table; SIGMET fixtures; TC-EV080 |
| D-EV080-out | Promote; CA_ECCC; M10–M14; FE |
| D-EV080-vor-table | Bundled `vor_reference_points.json` (EED, BZA, TRM); `UnknownVOR` on missing id |
| D-EV080-gate | **open** — parser + fixtures + regression gate |

### Delivered (M9 slice)

| Area | Change |
|------|--------|
| Parser | `ReferencePointGeometryParser` + `parse_vor_reference_geometry` wired in `sigmet_airmet.py` |
| Data | `vor_reference_points.json` (FAA-published CONUS VORTAC coords) |
| Fixtures | +2 valid SIGMET VOR cases + 1 invalid unknown VOR |
| Tests | TC-EV080-001..005 (`test_tc_ev080_us_vor_geometry.py`) |

### Corpus

[Corpus: product §F36] [Corpus: domain-profiles §US_FAA_NWS] [Corpus: tests]

---

## Cycle EV-079 — US_FAA_NWS SIGMET/AIRMET national layer (#919 M8) (EV-079-us-sigmet-airmet)

**Opened:** 2026-08-24 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-079-us-sigmet-airmet`  
**Preset:** Standard · **Documenting→Implementing gate:** open · **Issue:** [#919](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/919)  
**Parent:** #912 · **Prior:** EV-078 merged to `stage` @ `e77b7ecb`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV079-goal | #919 M8 — US SIGMET/AIRMET national layer fixture pack + US AIRMET phenomenon tokens |
| D-EV079-in | `sigmet_airmet.py` parser tokens; `fixtures/profiles/US_FAA_NWS/{SIGMET,AIRMET}/`; manifest; TC-EV079 |
| D-EV079-out | VOR ReferencePointGeometryParser; iwxxm-us SIGMETWeatherHazards emit; promote; CA_ECCC |
| D-EV079-ifr | US TAC `IFR` shorthand → WMO `AirWxPhenomena/SFC_VIS` (documented mapping) |
| D-EV079-fn | Deepen **F36** / **F6.d** / **tests** — no new top-level Fn |
| D-EV079-scale | Standard verify angles |
| D-EV079-gate | **open** — parser + fixture pack + regression gate |

### Delivered (M8 slice)

| Area | Change |
|------|--------|
| Parser | `IFR`, `MOD ICE/TURB`, `MT OBSC`, `TSGR` variants in `_AIR_PHENOMENA` |
| Fixtures | +2 SIGMET, +3 AIRMET under `profiles/US_FAA_NWS/` with `rule_id` |
| Tests | TC-EV079-001..004 (`test_tc_ev079_us_sigmet_airmet.py`) |

### Corpus

[Corpus: product §F36] [Corpus: domain-profiles §US_FAA_NWS] [Corpus: tests]

---

## Cycle EV-078 — CA_ECCC #916 closeout audit (EV-078-ca-eccc-916-closeout)

**Opened:** 2026-08-24 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-078-ca-eccc-916-closeout`  
**Preset:** Standard (doc-only) · **Documenting→Implementing gate:** closed · **Issues:** [#916](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/916) (verify close)  
**Parent:** #912 · **Prior:** EV-077 merged to `stage` @ `844f681a`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV078-goal | Audit standing docs vs `stage`; confirm #916 P1 AC met or waived; align corpus post EV-076/077 |
| D-EV078-in | `catalog.yaml`, `COVERAGE_MATRIX.md`, `CA_ECCC.md`, `feature-list.md`, `test-plan.md`; TC-EV071..074, TC-EV1061, TC-EV078 pytest |
| D-EV078-out | Promote; VAA exchange emit; TAC convert VAA; live datamart re-harvest |
| D-EV078-916 | **Close verified** — CA_ECCC P1 build AC met on `stage`; residual VAA exchange emit waived |
| D-EV078-vaa-emit | **Waived** — datamart `vaa/` HTTP 404 at probe 2026-08-24; inherits D-EV074-vaa-follow |
| D-EV078-vaa-count | **1 of ≥2** — VAAC 31-day index still single FVCN bulletin; TC-EV074-003 objective met |
| D-EV078-fn | Deepen **F36** / **tests** — no new top-level Fn |
| D-EV078-scale | Standard verify angles; doc-only implementing |
| D-EV078-gate | **closed** — doc deltas + regression gate only |

### Probe result (2026-08-24)

| Product | Datamart | VAAC TAC (31-day index) |
|---------|----------|-------------------------|
| VAA IWXXM | HTTP 404 | N/A |
| VAA TAC | N/A | 1 live (FVCN01-0001 EDZIZA) — unchanged since EV-077 |

### Audit result (2026-08-24)

| Area | Verdict | Evidence |
|------|---------|----------|
| SIGMET exchange emit (#1061) | Met | EV-076 / TC-EV1061-* |
| VAA validate-first TAC | Met | EV-077 / TC-EV074-005, TC-EV074-011 |
| AIRMET ops deepen (+2) | Met | EV-077 / TC-EV072-007..010 |
| VAA exchange emit | Waived | D-EV074-vaa-follow; datamart absent |
| #916 P1 build AC | Met | EV-064..077 on `stage` |

### Corpus

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests]

---

## Cycle EV-077 — CA_ECCC ops corpus deepen + VAA VAAC TAC waiver (2026-08-24)

**Opened:** 2026-08-24 · **Merged:** 2026-08-24 · **PR:** [#1064](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1064) → `stage` @ `844f681a`  
**Parent:** #916 · **Prior:** EV-076 merged to `stage`

**Opened:** 2026-08-24 · **Parent:** #916 · **Prior:** EV-076 merged to `stage`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV077-goal | Deepen CA_ECCC ops corpus (AIRMET czwg + GFA SFC_VIS); VAA validate-first via Montreal VAAC TAC |
| D-EV077-ops | +2 AIRMET datamart fixtures (`czwg`, `SFC_VIS_and_BKN_CLD`); manifest pin 2026-08-24 |
| D-EV074-vaa-waiver-tac | **Waived** datamart `vaa/` gate — Montreal VAAC TAC from weather.gc.ca/eer/vaac as validate-first ops source; no exchange emit |
| D-EV074-vaa-count | **1 of ≥2** live FVCN bulletins in VAAC 31-day index at pin 2026-08-24 (EDZIZA); re-harvest when second publishes |
| D-EV077-out | Promote; VAA exchange emit; TAC convert VAA |

### Probe result (2026-08-20..24)

| Product | Datamart | VAAC TAC |
|---------|----------|----------|
| VAA IWXXM | HTTP 404 all days | N/A |
| VAA TAC | N/A | 1 live (FVCN01-0001 EDZIZA 2026-08-18) |
| AIRMET | 5–24 files/day | — |
| SIGMET | 10–105 files/day (all LSCN weather) | — |

### Corpus

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests §TC-EV074]

---

## Cycle EV-076 — CA_ECCC SIGMET exchange output emit (#1061) (EV-076-ca-eccc-sigmet-exchange-emit)

**Opened:** 2026-08-24 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-076-ca-eccc-sigmet-exchange-emit`  
**Preset:** Standard · **Issues:** [#1061](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1061)  
**Parent:** #916 · **Prior:** EV-075 merged to `stage`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV076-goal | SIGMET MSC exchange-output emit + layer-6 ops packaging; catalog `ev076_slice` |
| D-EV076-in | `exchange_output.py`, `ca_exchange_validate`, layered validate exchange stage, ops fixtures, API bare `output_spec` |
| D-EV076-out | VAA emit (deferred D-EV074-vaa-follow); TAC convert SIGMET; promote |
| D-EV076-vaa | **Deferred** — no MSC VAA datamart tree; VAA stays `ev074_validate_first` |
| D-EV076-fn | Deepen **F36** / **F23** — no new top-level Fn |

### Corpus

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests]

---

## Cycle EV-075 — CA_ECCC #1032 closeout audit (EV-075-ca-eccc-1032-closeout)

**Opened:** 2026-08-24 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-075-ca-eccc-1032-closeout`  
**Preset:** Standard (Full verify) · **Documenting→Implementing gate:** closed (doc-only) · **Issues:** [#1032](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1032) (verify close), follow-on SIGMET/VAA exchange emit  
**Parent:** #916 · **Prior:** EV-074 merged to `stage` @ `cd19f80a`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV075-goal | Audit standing docs vs `stage`; confirm #1032 umbrella AC met or waived; align corpus |
| D-EV075-in | `catalog.yaml`, `COVERAGE_MATRIX.md`, `CA_ECCC.md`, `test-plan.md`; TC-EV071..074 pytest |
| D-EV075-out | Promote; new product surface; TAC convert SIGMET/VAA; live datamart re-harvest |
| D-EV075-1032 | **Close verified correct** — aerodrome exchange + COLLECT + ops delivered EV-071..073; issue already closed on GitHub |
| D-EV075-sigmet-vaa-emit | **Waived** — SIGMET/VAA exchange *emit* remains validate-first; split to [#1061](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1061) |
| D-EV075-vaa-harvest | **Waived** — inherits D-EV074-vaa-follow (no MSC VAA datamart tree at pin) |
| D-EV075-fn | Deepen **F36** / **tests** — no new top-level Fn |
| D-EV075-scale | Full verify angles; doc-only implementing |
| D-EV075-gate | **closed** — doc deltas only |

### Audit result (2026-08-24)

| Area | Verdict | Evidence |
|------|---------|----------|
| Exchange output METAR/SPECI/TAF/AIRMET | Met | TC-EV071-005..009, TC-EV072-001..006 — 68 passed |
| COLLECT envelope | Met | TC-EV073-001..005 |
| Ops corpus (#1036) | Met | TC-EV072-007..010 |
| SIGMET validate-first (#1043) | Met | TC-EV074-001..010 |
| VAA ops harvest | Waived | D-EV074-vaa-follow; TC-EV074-003 skipped objective |
| SIGMET/VAA exchange emit | Waived | `catalog.yaml` `ev074_validate_first`; follow-on issue |

### Corpus

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: tests]

---

## Cycle EV-074 — CA_ECCC SIGMET + VAA datamart validate-first (#1043) (EV-074-ca-eccc-sigmet-vaa)

**Opened:** 2026-08-24 · **Merged:** 2026-08-24 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-074-ca-eccc-sigmet-vaa`  
**Preset:** Full · **Documenting→Implementing gate:** closed · **Issues:** [#1043](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1043) **closed**  
**Parent:** #916 · **Prior:** EV-073 merged to `stage` · **PR:** #1060 → `stage` @ `cd19f80a`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV074-path | EV-074 on #1043 now (not #1032 closeout-first) |
| D-EV074-goal | Validate-first SIGMET/VAA ops fixtures + catalog/coverage; reusable harvest/validate pattern |
| D-EV074-in | ≥2 SIGMET IWXXM (VAA harvest deferred — D-EV074-vaa-follow); WMO 3.0.0 XSD+SCH under CA profile; skip `ca_xsd` N/A; catalog products; coverage matrix |
| D-EV074-out | TAC convert; full F23/F26 bar; live datamart CI; promote; UI; COLLECT/exchange emit for SIGMET/VAA; shipping `code-ca` SIGMET rules |
| D-EV074-counts | ≥2 SIGMET (ship now); ≥2 VAA **deferred** (D-EV074-vaa-follow) |
| D-EV074-kinds | Any operational SIGMET mix; record kinds in manifest |
| D-EV074-ca-xsd | Skip `ca_xsd` as not-applicable (not `CA_PRODUCT_XSD_NOT_FOUND`) |
| D-EV074-1033 | Note-only |
| D-EV074-fn | Deepen **F23** / **F26** / **F36** — no new top-level Fn |
| D-EV074-scale | Full; all default evolve verifying angles |
| D-EV074-success | #1043 AC + documenting/implementing verify PASS; PR → `stage`; no promote |
| D-EV074-deps | EV-073 on `stage` |
| D-EV074-gate | **closed** — merged PR #1060 |
| D-EV074-vaa-follow | MSC datamart 2026-08-24 has no `aviation/iwxxm/vaa` tree; ship SIGMET ops now; do **not** silent-fill encoder VAA; follow-on when MSC publishes VAA |

### Corpus

[Corpus: product §F23] [Corpus: product §F26] [Corpus: product §F36] [Corpus: tests] [Corpus: api] [Corpus: domain-profiles §CA_ECCC]

---

## Cycle EV-073 — CA_ECCC COLLECT envelope + profile wiring (#1042) (EV-073-ca-eccc-collect-envelope)

**Opened:** 2026-08-24 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-073-ca-eccc-collect-envelope`  
**Preset:** Full · **Documenting→Implementing gate:** closed · **Issues:** [#1042](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1042) (+ #1032 COLLECT residual)  
**Parent:** #916 · **Prior:** EV-072 merged to `stage` @ `83c99d6f`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV073-goal | M1: full COLLECT envelope on CA_ECCC convert; M2: #1042 extension token + profile metadata wiring |
| D-EV073-in | METAR/SPECI/TAF/AIRMET COLLECT wrap; MSC bulletinIdentifier; ops shell parity; FE `IWXXM_CA` auto-wire; fail-closed vendor pin |
| D-EV073-out | SIGMET/VAA ops (#1043); live datamart CI; ConversionProfile editor (#933) |
| D-EV073-deps | EV-072 on `stage` @ `83c99d6f` |
| D-EV073-scale | Full; all default evolve verifying angles |
| D-EV073-fn | Deepen **F36** / **F6** / **F7** / **tests** — no new top-level Fn |
| D-EV073-gate | **open** — M1+M2 **complete**; implementing verify in progress |
| D-EV073-m1 | COLLECT envelope: TC-EV073-001..005 — **complete** |
| D-EV073-m2 | Profile wiring (#1042): TC-EV073-006..009 — **complete** |

### Corpus

[Corpus: product §F36] [Corpus: product §F6] [Corpus: product §F7] [Corpus: api] [Corpus: tests] [Corpus: domain-profiles §CA_ECCC]

---

## Cycle EV-072 — CA_ECCC exchange aerodrome products + ops corpus (#1036) (EV-072-ca-eccc-exchange-ops)

**Opened:** 2026-08-24 · **Merged:** 2026-08-24 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-072-ca-eccc-exchange-ops`  
**Preset:** Full · **Documenting→Implementing gate:** open · **Issues:** [#1036](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1036) (+ #1032 residual exchange products)  
**Parent:** #916 · **Prior:** EV-071 merged to `stage` @ `2d934ef2` · **PR:** [#1057](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1057) → `stage` @ `83c99d6f`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV072-goal | M1: SPECI/TAF/AIRMET exchange output (EV-071 deferred); M2: datamart ops conformance corpus (#1036) |
| D-EV072-in | Per-product output_spec, layer-6 goldens, catalog/doc delta; harvest script + ops fixtures (≥5 METAR, ≥2 each other) |
| D-EV072-out | Full COLLECT envelope; UI picker (#1042); SIGMET/VAA ops (#1043); live CI datamart fetch |
| D-EV072-deps | EV-071 on `stage` @ `2d934ef2` |
| D-EV072-scale | Full; all default evolve verifying angles |
| D-EV072-fn | Deepen **F36** / **F6** / **tests** — no new top-level Fn |
| D-EV072-gate | **open** — documenting 11/11 PASS; M1+M2 **complete**; implementing verify **11/11 PASS**; merged #1057 |
| D-EV072-m1 | Exchange SPECI/TAF/AIRMET: TC-EV072-001..006 — **complete** |
| D-EV072-m2 | Ops corpus: harvest + fixtures; TC-EV072-007..010 — **complete** |

### Corpus

[Corpus: product §F36] [Corpus: product §F6] [Corpus: tests] [Corpus: domain-profiles §CA_ECCC] [Corpus: api]

---

## Cycle EV-071 — CA_ECCC lint pack + exchange output (#1038 / #1032 / #1040) (EV-071-ca-eccc-lint-exchange)

**Opened:** 2026-08-24 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-071-ca-eccc-lint-exchange`  
**Preset:** Full · **Documenting→Implementing gate:** closed · **Issues:** [#1038](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1038), [#1032](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1032), [#1040](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1040)  
**Parent:** #916 · **Prior:** EV-070 merged to `stage` @ `c45b3ddc`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV071-goal | Phased: M1 #1038 tac-validate CA rule pack; M2 #1032 METAR exchange output + #1040 translation metadata |
| D-EV071-in | P0+P1 METAR/SPECI + TAF NCLWS + AIRMET GFA lint; MSC filename + WMO header; catalog exchange contract; writer/validate hooks |
| D-EV071-out | Full MANOBS book in one PR; AMQP/dissemination (F16–F19); full COLLECT unless METAR slice requires minimal wrapper |
| D-EV071-deps | EV-070 on `stage`; EV-069 exchange validate layer (partial #1032); include #1040 in scope |
| D-EV071-scale | Full; all default evolve verifying angles |
| D-EV071-fn | Deepen **F15** / **F6** / **F36** — no new top-level Fn |
| D-EV071-gate | **open** — documenting 11/11 PASS; M1+M2 **complete**; verify implementing pending |
| D-EV071-m1 | CA lint pack: 12 rules, fixtures, API pre-convert lint, quality matrix (TC-EV071-001..004) |
| D-EV071-m2 | Exchange METAR output: MSC filename, WMO header, translation metadata, API output_spec (TC-EV071-005..009) |

### Corpus

[Corpus: product §F15] [Corpus: product §F6] [Corpus: product §F36] [Corpus: api] [Corpus: domain-profiles §CA_ECCC] [Corpus: adr/ADR-036] [Corpus: adr/ADR-028]

---

## Cycle EV-070 — CA_ECCC TAF + AIRMET convert deepen (#1041) (EV-070-ca-eccc-taf-airmet-convert)

**Opened:** 2026-08-23 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-070-ca-eccc-taf-airmet-convert`  
**Preset:** Standard · **Documenting→Implementing gate:** closed · **Issue:** [#1041](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1041)  
**Parent:** #916 · **Prior:** EV-069 merged to `stage` @ `ec782625`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV070-goal | #1041 convert deepen — TAF `present_and_forecast_weather` + MANAIR amendment slice; AIRMET GFA structured fields |
| D-EV070-in | `tac2iwxxm` parse/emit; CA_ECCC goldens; TC-EV070-*; layered `ca_eccc` validate round-trip |
| D-EV070-out | `#1032` full exchange output; `#1050` reportVariant; datamart live fetch; promote |
| D-EV070-deps | EV-069 on `stage`; #1033 code-ca closed |
| D-EV070-scale | Standard; all default evolve verifying angles |
| D-EV070-fn | Deepen **F6** / **F20** / **F36** — no new top-level Fn |
| D-EV070-gate | **open** — documenting 11/11 PASS; implementing 11/11 PASS |

### Build (complete)

| ID | Outcome |
|----|---------|
| D-EV070-m1 | TAF `present_and_forecast_weather/IC` + `taf_amd` AMENDMENT golden |
| D-EV070-m2 | AIRMET GFA `surfaceVisibility` / `cloudBase` / `surfaceWindSpeed` for SFC_VIS_and_BKN_CLD |
| D-EV070-m3 | TC-EV070-001..007; `ca_xsd` AIRMET extension probe fix in `iwxxm-validate` |
| D-EV070-verify | Local `make test` PASS; scoped EV-070/064/069 tests 79 passed; implementing verify 11/11 PASS |

### Closeout (2026-08-24)

| ID | Outcome |
|----|---------|
| D-EV070-build | TAF `present_and_forecast_weather/IC` + MANAIR amendment golden; AIRMET GFA structured fields; TC-EV070-001..007 |
| D-EV070-verify-impl | Local implementing verify 11/11 PASS; remote CI all green on #1055 |
| D-EV070-pr | [#1055](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1055) → `stage` **merged** @ `c45b3ddc` |
| D-EV070-issues | [#1041](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1041) **closed** |
| D-EV070-fn-status | **F6** / **F20** / **F36** — CA_ECCC TAF + AIRMET convert deepen on `stage` |

**Closed:** 2026-08-24 · **Session status:** closed · **PR merged to `stage`** · **Promote `stage`→`main`:** held

### Corpus

[Corpus: product §F6] [Corpus: product §F20] [Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: adr/ADR-036]

---

## Cycle EV-067 — CA_ECCC metar-speci-ca extensions (#1039) (EV-067-ca-metar-speci-ca)

**Opened:** 2026-08-22 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-067-ca-metar-speci-ca`  
**Preset:** Standard · **Documenting→Implementing gate:** open · **Issue:** [#1039](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1039)  
**Parent:** #916 / EV-064 · **Prior:** EV-066

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV067-goal | P1 #1039 — LWIS + SAWR IWXXM roots, Addendum deepen (densityAltitude, icing), MANOBS TAC leads |
| D-EV067-in | tac2iwxxm parse/emit; CA_ECCC fixtures; API LWIS/SAWR auto-detect → METAR product |
| D-EV067-out | P2 AerodromeVariableRVR/ObservedLightning; full #1027/#1035 validation stack |
| D-EV067-deps | Proceed on EV-064/066 foundation; waive #1027/#1035 gaps for this slice |
| D-EV067-scale | Standard; all default evolve verifying angles |
| D-EV067-fn | Deepen **F36** / **F1** |
| D-EV067-gate | **open** (`open_build` 2026-08-22) |

### Closeout (2026-08-23)

| ID | Outcome |
|----|---------|
| D-EV067-build | P1 complete: LWIS/SAWR roots, Addendum deepen, API auto-detect, goldens + TC-EV067-001..003 |
| D-EV067-pr | [#1049](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1049) → `stage` **merged** @ `615f156a` (2026-08-23) |
| D-EV067-verify | Remote CI all required checks SUCCESS; local scoped tests 23 passed |
| D-EV067-fn-status | **F36** / **F1** deepen — LWIS/SAWR + Addendum P1 slice; P2 residuals on backlog |
| D-EV067-follow-on | #1035 XSD stack; P2 variable RVR/lightning; optional lint; [#1050](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1050) umbrella |

**Closed:** 2026-08-23 · **Session status:** closed · **PR merged to `stage`** · **Issue #1039:** open (close manually if desired)

### Corpus

[Corpus: product §F36] [Corpus: product §F1] [Corpus: domain-profiles §CA_ECCC] [Corpus: adr/ADR-036]

---

## Cycle EV-068 — CA_ECCC validation stack (#1035 + #1027) (EV-068-ca-eccc-validation-stack)

**Opened:** 2026-08-23 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-068-ca-eccc-validation-stack`  
**Preset:** Standard · **Documenting→Implementing gate:** closed · **Issues:** [#1035](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1035), [#1027](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1027)  
**Parent:** #916 / EV-067 · **Prior:** EV-067 merged [#1049](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1049) @ `615f156a`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV068-goal | Layered `ca_eccc` validation: profile-pinned IWXXM 3.0.0 bundle (#1027) + staged pipeline (#1035) |
| D-EV068-in | `iwxxm-validate` layers; vendor manifest; API/CLI CA_ECCC + IWXXM_CA; EV-067 golden XSD gate |
| D-EV068-out | Global 2025-2 default migration; #1050 reportVariant; P2 #1039 residuals; SIGMET 3.0.0 |
| D-EV068-deps | EV-067 on `stage`; bundle #1027 remainder with #1035 in one cycle |
| D-EV068-scale | Standard; all default evolve verifying angles |
| D-EV068-fn | Deepen **F2** / **F4** / **F13** / **F36** |
| D-EV068-gate | **open** (`open_build` 2026-08-23) |

### Documenting band (2026-08-23)

| ID | Outcome |
|----|---------|
| D-EV068-context | Inventory complete — EV-064 M2 scaffold; layers 4–5 missing; GML/catalog risk on layer 2 |
| D-EV068-docs | Deltas: `IWXXM_VALIDATION.md` §CA stages, `VERSION_SUPPORT_POLICY.md` profile lines, `CA_ECCC.md`, `catalog.yaml` validation_stages, `COVERAGE_MATRIX.md`, `api-contract.md`, `test-plan.md` TC-EV068-* |
| D-EV068-feasibility | **FEASIBLE** — see session `feasibility.md` |
| D-EV068-verify-doc | Documenting twins **11/11 PASS** (2026-08-23) |

### Closeout (2026-08-23)

| ID | Outcome |
|----|---------|
| D-EV068-build | M1–M7 complete: layered `ca_eccc` validate, vendor 3.0.0 bundle, `extensions=IWXXM_CA` API wire, TC-EV068-001..004, docs |
| D-EV068-verify-impl | Implementing twins **11/11 PASS**; scoped tests 34 passed |
| D-EV068-pr | [#1052](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1052) → `stage` **merged** @ `1828d9dc` |
| D-EV068-hotfix | [#1053](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1053) — quality-pack native build for CA_ECCC XSD (GML catalog) |
| D-EV068-staging-smoke | Local `scripts/deploy/staging_smoke.sh` **PASS** (pre-deploy image; await CI Deploy + Staging smoke on tip) |
| D-EV068-fn-status | **F2** / **F4** / **F13** / **F36** deepen — CA_ECCC layered validation on `stage` |
| D-EV068-follow-on | TAF `taf-ca.xsd` product gate gaps (TC-EV068-002 backlog); global 2025-2 default migration held |

**Closed:** 2026-08-23 · **Session status:** closed · **PR merged to `stage`** · **Promote `stage`→`main`:** held (separate gate)

### Corpus

[Corpus: product §F2] [Corpus: product §F4] [Corpus: product §F13] [Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC]

---

## Cycle EV-069 — CA_ECCC validation deepen (#1035 follow-on) (EV-069-ca-eccc-validation-deepen)

**Opened:** 2026-08-23 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-069-ca-eccc-validation-deepen`  
**Preset:** Standard · **Issues:** [#1035](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1035) (remainder), [#1033](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1033), [#1032](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1032)  
**Parent:** EV-068 merged to `stage` @ `71d400a3`

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV069-goal | Complete #1035 remainder: code-ca layer, exchange layer, TAF `taf-ca.xsd` product gate |
| D-EV069-in | `iwxxm-validate` layers 5–6; TAF NCLWS probe fix; TC-EV069-*; standing docs |
| D-EV069-out | AIRMET convert (M5); datamart live fixture fetch; global 2025-2 migration |
| D-EV069-deps | EV-068 on `stage` |
| D-EV069-scale | Standard; all default evolve verifying angles |
| D-EV069-fn | Deepen **F2** / **F13** / **F36** |

### Closeout (2026-08-23)

| ID | Outcome |
|----|---------|
| D-EV069-build | Layers 5 (`code_ca`) + 6 (`exchange`); TAF NCLWS `taf-ca.xsd` gate; TC-EV069-001..007; docs |
| D-EV069-verify-impl | `iwxxm-validate` tests **156 passed**, 1 skipped; per-file coverage ≥95% |
| D-EV069-pr | [#1054](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1054) → `stage` **merged** @ `ec782625` |
| D-EV069-issues | [#1035](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1035) **closed**; [#1033](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1033) **closed**; [#1032](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1032) **closed** (EV-075 umbrella audit; aerodrome emit EV-071..073; SIGMET/VAA emit → #1061) |
| D-EV069-fn-status | **F2** / **F13** / **F36** — CA_ECCC validation stack complete on `stage` (layers 1–6) |

**Closed:** 2026-08-23 · **Session status:** closed · **PR merged to `stage`** · **Promote `stage`→`main`:** held

### Corpus

[Corpus: product §F2] [Corpus: product §F13] [Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC]

---

## Cycle EV-066 — CA_ECCC RMK + altimeter deepen (#916) (EV-066-ca-eccc-rmk-deepen)

**Opened:** 2026-08-22 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-066-ca-eccc-rmk-deepen`  
**Preset:** Standard · **Documenting→Implementing gate:** open · **Issue:** [#916](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/916)  
**Parent:** EV-063 / F36 / [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912)

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV066-goal | #916 deepen P1 — Canadian RMK grammar + `A####` altimeter edge cases with goldens |
| D-EV066-in | tac2iwxxm parse/emit; tac-validate ca_eccc lint; CA_ECCC fixtures; standing docs |
| D-EV066-out | LWIS/SAWR; MANAIR TAF amendments; exchange overlays (#921); SIGMET national |
| D-EV066-slice | PRESRR; A//// not-observable; SLP+T combo; extended RMK lint codes |
| D-EV066-scale | Standard; all default evolve verifying angles |
| D-EV066-fn | Deepen **F36** only |
| D-EV066-feasibility | **FEASIBLE** — EV-064 foundation; parser/emitter hooks exist |
| D-EV066-gate | **open** (`open_build` 2026-08-22) |

### Corpus

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: adr/ADR-036]
[Corpus: api] [Corpus: system-spec] [Corpus: tests]

---

## Cycle EV-086 — EUR_RODEX + AFI + CAR_SAM stubs (#921) (EV-086-regional-exchange-overlays)

**Opened:** 2026-08-28 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-086-regional-exchange-overlays`  
**Preset:** Standard · **Documenting→Implementing gate:** closed · **Issue:** [#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921)  
**Parent:** EV-065 / F36 / [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912)

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV086-goal | Land `EUR_RODEX` + `AFI` + `CAR_SAM` exchange stubs (registry + COLLECT packaging + tests + catalog docs) |
| D-EV086-in | `packages/dissemination` registry/packaging; standing docs; TC-EV086; API known-ids note |
| D-EV086-out | Drawer UI (#898); ROBEX/RODEX handbook mining deepen (#913); semantic TAC decode; sink protocols |
| D-EV086-overlay | All three P0 stubs = GLOBAL_AFS COLLECT baseline (same as APAC_ROBEX EV-065) |
| D-EV086-scale | Standard; evolve default verifying angles; e2e skipped (no UI) |
| D-EV086-fn | Deepen **F36** only |
| D-EV086-sources | EUR handbook URL remains access:gap; AFI/CAR_SAM sources TBD via #913 — stubs still ship |
| D-EV086-feasibility | **FEASIBLE** — EV-065 stub pattern; additive registry + COLLECT |
| D-EV086-gate | **open** (`open_build` 2026-08-28) |

### Corpus

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: adr/ADR-036]
[Corpus: api] [Corpus: tests] [Corpus: journeys §UJ-069]

---

## Cycle EV-065 — GLOBAL_AFS + APAC_ROBEX (#921) (EV-065-global-afs)

**Opened:** 2026-08-22 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-065-global-afs`  
**Preset:** Standard · **Documenting→Implementing gate:** open (pre-filled) · **Issue:** [#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921)  
**Parent:** EV-063 / F36 / [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912)

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV065-goal | Close #921 P0 — GLOBAL_AFS docs/fixtures + APAC_ROBEX regional stub with tests |
| D-EV065-in | dissemination exchange registry/packaging; convert-bulletin wire; standing docs |
| D-EV065-out | Dissemination drawer UI (#898); EUR_RODEX/AFI/CAR_SAM; semantic/TAC changes |
| D-EV065-overlay | APAC_ROBEX P0 = GLOBAL_AFS COLLECT baseline; ROBEX deepen on backlog |
| D-EV065-scale | Standard; all default evolve verifying angles |
| D-EV065-fn | Deepen **F36** only |
| D-EV065-feasibility | **FEASIBLE** — EV-063 foundation; stub overlay pattern |
| D-EV065-gate | **open** (`open_build` 2026-08-22, pre-filled) |

### Corpus

[Corpus: product §F36] [Corpus: domain-profiles §GLOBAL_AFS] [Corpus: adr/ADR-036]
[Corpus: api] [Corpus: system-spec] [Corpus: tests] [Corpus: journeys §UJ-069]

---

## Cycle EV-064 — CA_ECCC profile (#916) (EV-064-ca-eccc-profile)

**Opened:** 2026-08-22 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-064-ca-eccc-profile`  
**Preset:** Standard · **Documenting→Implementing gate:** closed · **Issue:** [#916](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/916)  
**Parent:** EV-063 / F36 / [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912)

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV064-goal | Full #916 scope — METAR/SPECI/TAF/AIRMET + validate + fixtures + API + FE picker slice |
| D-EV064-mining | Parallel MANOBS/MANAIR section mining → `manobs-manair-ca-mining-notes.md` |
| D-EV064-iwxxm | IWXXM **3.0.0** core + `iwxxm-ca` extensions (MSC operational line) |
| D-EV064-surface | API + tac2iwxxm + iwxxm-validate + FE #1024 slice |
| D-EV064-scale | Standard; all default evolve verifying angles |
| D-EV064-fn | Deepen **F36** only |
| D-EV064-out | US RMK reuse as-is; exchange overlays; SIGMET national deepen |
| D-EV064-feasibility | **FEASIBLE** — schedule risk on full roll-up; IWXXM 3.0.0 core pin required |
| D-EV064-gate | **open** (`open_build` 2026-08-22) |

### Closeout (2026-08-22)

| ID | Outcome |
|----|---------|
| D-EV064-m1-m6 | M1–M6 complete: vendor pin, validate, METAR/TAF/AIRMET convert, API wire, FE picker |
| D-EV064-verify | TC-EV064-001..006 green; implementing verify pending PR |
| D-EV064-fn-status | **F36** CA_ECCC P1 slice implemented; deepen continues on backlog |

**Closed:** pending PR · **Session status:** implementing (M7 docs)

---

### Corpus

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: adr/ADR-036]
[Corpus: api] [Corpus: system-spec] [Corpus: tests] [Corpus: journeys]

### Standing doc deltas (draft-docs)

- `docs/domain/profiles/semantic/CA_ECCC.md` — in progress status + IWXXM 3.0 line
- `docs/domain/mining/manobs-manair-ca-mining-notes.md` — new parallel mining backlog
- `docs/test-plan.md` §EV-064 TC rows
- `docs/feature-list.md` F36 #916 deepen
- `docs/api-contract.md` — `CA_ECCC` canonical semantic id + `IWXXM_CA` extension token
- `docs/domain/profiles/catalog.yaml` — mining_notes link + gaps refresh

---

## Cycle EV-063 — Multi-national semantic profiles (#912) (EV-063-multinational-profiles)

**Opened:** 2026-08-22 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-063-multinational-profiles`  
**Preset:** Standard · **Documenting→Implementing gate:** closed · **Epic:** [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912)

### Locked intake (EV0–EV9 + requirements)

| ID | Outcome |
|----|---------|
| D-EV063-goal | Drive #912 toward M1; stretch full roll-up; **Spec close** = ADR + #913 catalog + ≥1 P1 In Progress with fixtures |
| D-EV063-scope | In = unblocked #912 children; out = epic non-goals + defer #908/#920/#1024 by default |
| D-EV063-breaking | ADR + deprecation window; alias removal **2026-10-31** → [#1025](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1025) |
| D-EV063-fn | **F35** (semantic vs exchange arch/IDs/wire) + **F36** (national + exchange content) |
| D-EV063-spine | #913 → #914 → #919 US → #916 CA first P1 → #921 exchange as capacity |
| D-EV063-wire | Nested `conversion.semanticProfile` + `exchange.profile`; hard 4xx unknown ids |
| D-EV063-journey | Operator + library; convert → exchange package; fence annex3/iwxxm_us + F16–F19 |
| D-EV063-ui | Light picker [#1024](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1024); preview later if Build includes FE |
| D-EV063-corpus | New ADR-036 (Proposed); new CORPUS row **domain-profiles** |
| D-EV063-build | 07–13 blocked; touch tac2iwxxm/validate/dissemination/backend; deploy at gate |
| D-EV063-04-plan | **1a** — execution plan approved 2026-08-22 |
| D-EV063-gate | **open** (`open_build` 2026-08-22) — 07-build M1–M2 in progress |
| D-EV063-feasibility | **FEASIBLE** — Spec close by M1 (~2026-09-19) if gate opens ~2026-08-25; full M1 roll-up not feasible (#970/UI/nationals out) |
| D-EV063-914 | Spike unblock = ADR-036 Accept + stable ID list; runtime F35 follows gate |
| D-EV063-verify-doc | Documenting twins **11/11 PASS** (2026-08-22) |

### Corpus

[Corpus: product §F35] [Corpus: product §F36] [Corpus: adr/ADR-036] [Corpus: domain-profiles]
[Corpus: api] [Corpus: system-spec] [Corpus: tests] [Corpus: journeys] [Corpus: tech-spec]

### Standing doc deltas (draft-docs)

- `docs/adr/ADR-036-semantic-vs-exchange-profiles.md` (Proposed)
- `docs/domain/profiles/README.md` + CORPUS `domain-profiles` row
- `docs/feature-list.md` F35/F36
- `docs/api-contract.md` EV-063 proposed wire section
- `docs/spec.md`, `docs/env-contract.md`, `docs/test-plan.md`, `docs/user-journeys.md` (UJ-069)

### Closeout (2026-08-22)

| ID | Outcome |
|----|---------|
| D-EV063-merged | PR [#1026](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1026) → `stage` (M1–M9) |
| D-EV063-verify-impl | Implementing twins **11/11 PASS**; `08-verify-build` PASS |
| D-EV063-spec-close | Met: ADR-036 Accepted; #913 catalog; #916 fixtures started; UJ-069 API |
| D-EV063-fn-status | **F35** → Implemented; **F36** → In progress (national deepen continues) |
| D-EV063-follow-on | Epic #912 umbrella open; #1025 alias cutover 2026-10-31; #1024 FE deferred |

**Closed:** 2026-08-22 · **Session status:** complete

---

## Cycle EV-062 — Validation Issues Catalog (#1017) (EV-062-validation-issues-catalog)

**Opened:** 2026-08-20 · **Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-062-validation-issues-catalog` · **Branch:** `evolve/EV-062-validation-issues-catalog` @ `origin/stage`  
**Preset:** Standard · **Documenting→Implementing gate:** closed · **Promote:** not in scope (EV-061 promote remains held)

### Locked intake

| ID | Outcome |
|----|---------|
| D-EV062-scope | Full [#1017](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1017) A+B **plus** rename to **Validation Issues Catalog**, operator **issue_type**, richer natural-language descriptions with section locators (or explicit unavailable) |
| D-EV062-996 | **Out** — keep [#996](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/996) click-detail distinct |
| D-EV062-scale | Standard; evolve default angles |
| D-EV062-session | One session Documenting → Implementing |
| D-EV062-fn | Deepen **F7.v** / **F15** only — **no new Fn** |
| D-EV062-api | Additive fields on existing `GET /lint-issue-catalog` — no new route |
| D-EV062-issue-type | Closed vocab: `presence` \| `structure` \| `content` \| `consistency` \| `iwxxm_schema` \| `other` |
| D-EV062-copy | Descriptions must explain what + why + severity; natural-language section cite or “Source section unavailable”; ban thin research-only stubs as sole copy |
| D-EV062-sources | Prefer public primary hrefs; paywall labeled; `source_locator` + `source_access`; re-crawl; no engine changes for link polish alone |
| D-EV062-gate | **open** — Documenting twins PASS 11/11; intake locked one-session Implementing (`D-EV062-session`); proceed Build |

### Corpus

[Corpus: product §F15] [Corpus: product §F7] [Corpus: api §lint-issue-catalog] [Corpus: adr/ADR-028]
[Corpus: journeys] [Corpus: tests] [Corpus: decisions §EV-062]

---

## Cycle EV-061 — Pre-promote UX + catalog + AHL + stage→main gate (#1009) (S071)

**Opened:** 2026-08-18 · **Session:** S071-pre-promote-ux-catalog · **Branch:** `evolve/EV-061-pre-promote-ux-catalog` @ `stage@a1650b01`  
**Preset:** Standard · **Spec→Build gate:** **open** (`D-S071-spec-build=1a`) · **Promote:** held until #1015

### Locked intake (EV0–EV9)

| ID | Outcome |
|----|---------|
| D-S071-e0 | Goal = validate UX + AHL + Product/Profile UI + catalog; in = all listed + stage→main gate; API breaking OK if documented |
| D-S071-e1 | Pre-promote cleanup; `cycle_type: feature`; M0 epic #1009 + #1010–#1015 |
| D-S071-e2 | Public/guest ops + CI reviewers; must-not-break F21/F7/F10; UI preview at 11 |
| D-S071-e3 | Readable item-by-item IWXXM validate decode; fix AHL decode+convert; new catalog tab; full stage→main checks |
| D-S071-e4 | Docs: product/api/journeys/tests/tech; Spec 01→02→04 + uat/verify-qa Spec; AHL brief shown |
| D-S071-e5 | FE/BE/tac-validate(+AHL)/CI; full H4–H5+UAT; stage then hold promote |
| D-S071-e6 | OOS: M1+ profiles, dissemination spikes, #996, #837 |
| D-S071-e7 | New FE tab; no new secrets; H4–H5 |
| D-S071-e8 | Standard Spec/Build bands; Build blocked until gate |
| D-S071-e9 | Open S071; deepen F7/F2/F6/F9/F10/F15/F34 (no new Fn); Spec-only |
| D-S071-ahl | AHL context brief acknowledged — golden SAUS31 multi-METAR; #1011 harness vs #1012 product |
| D-S071-links | Crawl catalog URLs in Spec; **block Build** on broken links until user searches; normalize official copies OK |
| D-S071-links-resolve | User research 2026-08-18 — **3-tier source model**; treat `49-2`/`nil` as semantic IDs; operator hrefs → verified landings; IWXXM-US → NWS schemas + vendor pin; **unblock #1014** Spec/Build; mining note `docs/domain/mining/ev061-catalog-source-replacements-2026-08-18.md` |

### 02-verify-plan Gate A — PASS (`D-S071-gateA=1a`)

| ID | Verdict |
|----|---------|
| D-S071-02-c1 | Modify — journeys header/changelog: links resolved / #1014 unblocked |
| D-S071-02-m1 | Modify — UJ-067 tier includes H4–H5 |
| D-S071-02-m2 | Approve — TC-EV061-* detail deferred to 04 |
| D-S071-02-m3 | Approve — api-contract delta deferred to 04 |
| D-S071-02-m4 | Approve — Spec UI minimum; richer catalog schema in 04/Build |
| D-S071-gateA | **PASS** → 04-tech-plan; Spec→Build stays closed |

Report: `docs/sessions/S071-pre-promote-ux-catalog/reports/02-verify-plan.md`

### 04-tech-plan (drafted — pending `D-S071-04-plan`)

| ID | Outcome |
|----|---------|
| D-S071-m-order | M1 #1011 → M2 #1012 → M3 #1010 → M4 #1013 → M5 #1014 → M6 #1015 |
| D-S071-deps | No new npm/PyPI deps |
| D-S071-adr | No new ADR |
| D-S071-api | Additive: `INVALID_AHL`; validate `segments`/`summary`; catalog fields on existing GET. No new catalog endpoint |
| D-S071-cors | No new origins; H4–H5 in 12/13 |
| D-S071-ci | Restore lint/typecheck CI + full E2E as required on `stage`→`main` (plus unit + Staging gate) |
| D-S071-ahl-code | Prefer `INVALID_AHL` for malformed convert-bulletin heading; keep `bulletin_split_failed` as `detail.alias` (additive, not a rename) |

Artifacts: `reports/04-tech-plan.md`, `reports/execution-plan.md`, `build-plan-card.md`  
**Approved:** `D-S071-04-plan=1a` (2026-08-18)

### Dual Spec

- verify-qa Spec: `reports/verify-qa-spec.md` — **completed**
- uat Spec: `uat-script.md` — **completed** (Build sign-off pending)

### Spec→Build gate — OPEN (`D-S071-spec-build=1a`)

| ID | Outcome |
|----|---------|
| D-S071-spec-build | **1a** — Open Spec→Build; start 07-build M1 (#1011 live bulletin `file` → `files`); promote held until #1015 |

### Prior session closeout

- S070/EV-060 closed; PRs #1007 (product), #1008 (S070 docs), #999 (S069 docs) merged to `stage`
- Tickets: epic [#1009](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1009); children #1010–#1015 on milestone M0

### Corpus

[Corpus: product §F2] [Corpus: product §F6] [Corpus: product §F7] [Corpus: product §F9] [Corpus: product §F10] [Corpus: product §F15] [Corpus: product §F34] [Corpus: api] [Corpus: journeys] [Corpus: tests] [Corpus: tech-spec]

---

> Standing log of approved evolve-cycle scope and product decisions.
> Cycle metadata also recorded in `workflow-state.yaml` §`evolve_cycles`.

## Cycle EV-060 — Converter operator bugs + IWXXM pass-through (#1000) (S070)

**Session**: S070-converter-operator-bugs  
**Features**: deepen **F7.t** (IWXXM product) + F6/F2/F10/F29/F31; no new top-level Fn  
**Started**: 2026-08-17  
**Status**: **in_progress** — 09-qa PASS (advisories); 10-e2e UJ-059..063 PASS; Auth logout T2 FAIL  
**Branch**: `evolve/EV-060-converter-operator-bugs` (base `stage@8755ae87`)  
**Issues**: epic [#1000](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1000) · [#1001](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1001) · [#1002](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1002) · [#1003](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1003) · [#1004](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1004) · [#1005](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1005) · [#1006](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1006)  
**Milestone**: GitHub **M0 — Stabilize + operator trust + narrative**  
**Later (not this cycle)**: profile view/create [#933](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/933) / [#924](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/924)  
**Corpus**: [Corpus: product §F7] [Corpus: product §F6] [Corpus: product §F2] [Corpus: product §F10]
[Corpus: product §F29] [Corpus: product §F31] [Corpus: api] [Corpus: journeys] [Corpus: tests]
[Corpus: decisions §EV-060]

### Scope (Phase 0 — locked 2026-08-17)

| ID | Decision |
|----|----------|
| D-S070-e0 | Tickets + Spec first; M0 pack; in/out as written |
| D-S070-e1 | Deepen F7.t (no F35); file tickets at EV9; six success observables |
| D-S070-e2 | Operator + API/CLI; FileConverter/accumulate/QM honor; UI preview at 11 |
| D-S070-e3a | AHL split then lint reports; product=IWXXM pass-through; F7.s stays |
| D-S070-e3b | Profile at converter top; editable Bulletin ID + Issuing Center; wire log_level; a11y must |
| D-S070-e3c | Auth UAT + Playwright; API same fields |
| D-S070-e4 | Standing docs delta; existing CORPUS (no waiver); uat+verify-qa Spec; Standard 01→02→04 |
| D-S070-e5 | Four Build PRs; 09+10+11+uat; staging smoke; promote held |
| D-S070-e6 | OOS: #933/#924/#912/F16–F19/#898/F8 auto-push/promote/new auth; additive API; no JWT in DEBUG |
| D-S070-e7 | No new secrets; existing CORS; H0c + H4–H5; no new observability contract |
| D-S070-e8 | Spec 00→16→01→02→04; Build 07–13 blocked; skip 03/05/06 |
| D-S070-e9 | Open session; Spec-development only; Spec→Build **closed** |
| D-S070-spec-build | Open Build; 07+ as routed; M1 #1001 first |
| D-S070-board | Epic #1000 Backlog; children Ready until 07 |
| D-S070-08-vaa | AHL lint keep-whole remainder when no `=` (VAA/TCA/SWXA/VONA); heading-only still INVALID_AHL |
| D-S070-resume-m4 | Continue recommended: T4.2 facilitated UAT-003 now on local :18000 |
| D-S070-uat003 | **all-pass** — UAT-003 ACCEPTED 2026-08-18 local :18000 (product owner) |
| D-S070-phase-d | **1a** — 09-qa + 10-e2e in parallel |
| D-S070-09-depth | **2a** — delta QA + blocking H0c |
| D-S070-10-journeys | **3a** — UJ-059..063 + TC-EV060-1006 on local :18000 |
| D-S070-local-dev | **4a** — restart make-dev `:18000`/`:18001` |

### Intake decisions

| ID | Category | Question | Decision | ADR |
|----|----------|----------|----------|-----|
| E60-1 | decision | cycle_type | feature deepen F7.t | — |
| E60-2 | decision | GitHub pack | epic #1000 + #1001–#1006 on M0; no duplicate #933 | — |
| E60-3 | decision | F7.s | keep Validate-only alongside F7.t | — |
| E60-4 | decision | log_level | wire logger verbosity (not client echo only) | ADR-023 deepen |

### Corpus cites / waivers

| Ref | Kind | Target | Notes |
|-----|------|--------|-------|
| `[Corpus: product §F7]` | cite | F7.t + picker/bulletin | |
| `[Corpus: product §F6]` | cite | AHL / convert-bulletin | |
| `[Corpus: product §F2]` | cite | IWXXM validate pass-through | |
| `[Corpus: api]` | cite | `product=iwxxm`, log_level, bulletin fields | |
| `[Corpus: journeys]` | cite | UJ-059..063; UJ-003/046 | |
| `[Corpus: tests]` | cite | TC-EV060-* | |
| — | waiver | none | existing CORPUS rows |

### Stage log

| Stage | Completed | Notes |
|-------|-----------|-------|
| 00-context | 2026-08-17 | S070 opened; EV0–EV9 recommended |
| 16-evolve | — | orchestrating; Spec→Build **open** |
| 02-verify-plan | 2026-08-17 | Gate A PASS (`D-S070-gateA=1a`) |
| 04-tech-plan | 2026-08-17 | EP approved `D-S070-04-plan=1a` |
| uat Spec / verify-qa Spec | 2026-08-17 | checklists written |
| Spec→Build | 2026-08-17 | **open** (`D-S070-spec-build=1a`) |
| 07-build | 2026-08-18 | M1–M4 complete; 08 M4 PASS |
| 08-verify-build | 2026-08-18 | M4 PASS; report `reports/verification-report.md` |
| uat Build | 2026-08-18 | T4.2 UAT-003 ACCEPTED local :18000 |
| 09-qa | 2026-08-18 | PASS (advisories); `reports/qa-report.md`; H0c 6/6 |
| 10-e2e | 2026-08-18 | UJ-059..063 PASS; TC-EV060-1006-003 FAIL (`POST /auth/logout` 404); `reports/e2e-report.md` |
| D-S070-logout | 2026-08-18 | **1a** — restore `POST /auth/logout` (GoTrue proxy + scope); 1006-003 re-run **PASS**; then 11 |
| 11-verify-impl | 2026-08-18 | All 5 Fn + UJ-059..063 **Approve**; UI preview accepted `:18000`; T3 → 12/13 (`D-S070-11-t3`); `reports/verify-impl.md` |
| push | 2026-08-18 | `7762b88b` (09/10) pushed to PR #1007; promote held |
| 12-verify-deploy | 2026-08-18 | CI tip HARD STOP `c57eeef1` run 32169922030 (auth cov + OpenAPI drift) |
| D-S070-12-ci-fix | 2026-08-18 | **fix in place** — auth-job tests for `sign_out` + logout errors; `make openapi-refresh`; CI **success** 32171946188 @ `4d29ee0c` |
| D-S070-12-risks | 2026-08-18 | **approve** image/CD, CORS/Auth XHR, accidental promote, Playwright install hang |
| D-S070-12-rollback | 2026-08-18 | **approve** prior GHCR / `stage-latest`; no DB migrations |
| D-S070-12-close | 2026-08-18 | **checklist only** — keep no-merge #1007; hold 13 until a later merge |

### Out of scope

- #933/#924 profile editor; #912 national packs; F16–F19/#898; F8 auto-push;
  stage→main promote; new auth providers; live log panel; new CLI product

---

## Cycle EV-059 — CI Schemathesis + mutation quality gates (#841 / #727 / #874) (S069)

**Session**: S069-ci-schemathesis-mutation  
**Features**: **F34** — contract + mutation quality gates (**Done**)  
**Started**: 2026-08-17  
**Closed**: 2026-08-17  
**Branch**: `evolve/EV-059-ci-schemathesis-mutation` (base `stage@c458669e`)  
**Status**: **completed** — `D-S069-close=1`; on `stage` @ `8755ae87`; promote held  
**Issues**: [#841](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/841) · [#727](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/727) · [#874](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/874) — all **CLOSED** / Done  
**PRs**: [#997](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/997) (M1) @ `c08bc30f` · [#998](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/998) (M2) @ `8755ae87`  
**Tip CI**: [32054972352](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32054972352) SUCCESS  
**Reports**: [evolve-report-EV-059.md](../evolve-report-EV-059.md) · [evolve-summary.md](../sessions/S069-ci-schemathesis-mutation/reports/evolve-summary.md) · [07-build-m1](../sessions/S069-ci-schemathesis-mutation/reports/07-build-m1.md) · [07-build-m2](../sessions/S069-ci-schemathesis-mutation/reports/07-build-m2.md) · [verification-report](../sessions/S069-ci-schemathesis-mutation/reports/verification-report.md)  
**Artifacts**: [session-brief](../sessions/S069-ci-schemathesis-mutation/session-brief.md) · [routing-plan](../sessions/S069-ci-schemathesis-mutation/routing-plan.md) · [evolve-plan-card](../sessions/S069-ci-schemathesis-mutation/evolve-plan-card.md) · [02-verify-plan](../sessions/S069-ci-schemathesis-mutation/reports/02-verify-plan.md)  
**Corpus**: [Corpus: product §F34] [Corpus: tests] [Corpus: tech-spec] [Corpus: api]
[Corpus: decisions §EV-059]

### Scope (Phase 0 — locked 2026-08-17)

| ID | Decision |
|----|----------|
| D-S069-e0 | Close #841 via #727+#874; minimal CI cost; two PRs; fix findings |
| D-S069-ci | Schemathesis path-filtered **required** (tight budget); mutation **nightly/manual only** |
| D-S069-tool | **pytest-gremlins** (Python) + **Stryker** (TS) |
| D-S069-fn | Allocate **F34** |
| D-S069-e4 | Broad Python+TS mutation coverage via nightly matrix (not one-package PoC) |
| D-S069-e5 | Breaking OpenAPI cleanup **allowed** when Schemathesis proves export wrong |
| D-S069-route | Lean Spec `00→16→01→02`; Build `07→08`; skip 03–06, 09–13 |
| D-S069-e8 | Open session; Spec-development only — **superseded** by Spec→Build open |
| D-S069-01-ac | **2b** — AC1–AC7 (budgets in Spec) |
| D-S069-01-uj | **1a** — no new UJ |
| D-S069-01-tc | **2a** — TC-F34-001..007 |
| D-S069-01-deps | **3a** — schemathesis, pytest-gremlins, @stryker-mutator/core |
| D-S069-gateA | **1a** — PASS (2026-08-17) |
| D-S069-spec-build | **2a** — Open Build 07→08; Schemathesis (#727) before mutation (#874) |
| D-S069-m1-merge | **1a** — merge PR #997 → `stage`; start M2 mutation (#874) |
| D-S069-m2-pins | **pytest-gremlins==1.9.0**; **@stryker-mutator/*@10.0.0** |
| D-S069-m2-survivors | Waive 3 equivalent Stryker survivors on `packages/shared` `parseCommaSeparatedOrigins` outer trim/empty short-circuit (see `reports/07-build-m2.md`) |
| D-S069-m2-pr | **1** — open PR #998 → `stage` for #874 (after GitHub 503 recovery) |
| D-S069-ci-comment-waiver | **2** — waive Quality PR comment + Coverage PR comment failures on CI run `32049951760` (GitHub 503 sticky comments); all substantive test jobs green on PR #998 |
| D-S069-github-outage-bypass | Bypass GitHub API mutations (rerun, board sync, sticky comments) until user says otherwise — long-running Partial System Outage; prefer local verification |
| D-S069-sticky-softfail | Soft-fail Coverage/Quality sticky PR comment posts on GitHub API 429/500/502/503 (warn + continue); marker validation still hard-fails |
| D-S069-m2-merge | **1** — merge PR [#998](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/998) → `stage` @ `8755ae87` after sticky soft-fail CI green (`32054972352`) |
| D-S069-close | **1** — Close EV-059/S069 on stage; F34 Done; #841/#727/#874 CLOSED; `active_session=null`; promote held |

### Acceptance (approved `D-S069-01-ac=2b`)

1. Schemathesis ASGI + auth on protected routes (**TC-F34-001**).
2. `make test-schemathesis` + path-filtered required CI (**TC-F34-002**).
3. pytest-gremlins + Stryker + `make` + nightly matrix across Python packages/services + TS
   (**TC-F34-003..005**).
4. Inventory + test-plan notes (**TC-F34-006**).
5. Findings fixed or waived; two PRs; #841 closable (**TC-F34-006**).
6. (AC6 in feature-list) epic close path via children Done.
7. Documented max-examples ≤ 25 and Schemathesis job timeout ≤ 10 min (**TC-F34-007**).

### Out of scope

- Mutation required on every PR; Rust mutation; live staging/prod Schemathesis merge gate;
  product UI; weaken ≥95% coverage; promote `stage`→`main`; replace hand-written UJ/pytest

---

## Cycle EV-058 — Quality metrics side-by-side vs inline XML diff (#983) (S068)

**Session**: S068-quality-metrics-diff-layout  
**Features**: deepen **F7.q** only  
**Started**: 2026-08-17  
**Closed**: 2026-08-17  
**Branch**: `evolve/EV-058-quality-metrics-diff-layout` (base `stage@c2ca9a3f`)  
**Status**: **completed** — `D-S068-13=1` / `D-S068-close=1`; on `stage` @ `2c320c45`; promote held  
**Issue**: [#983](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/983) — **CLOSED** · board **Done**  
**PR**: [#994](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/994) → `stage` @ `2c320c45`  
**Staging CD**: [32038222032](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32038222032)  
**Reports**: [evolve-report-EV-058.md](../evolve-report-EV-058.md) · [evolve-summary.md](../sessions/S068-quality-metrics-diff-layout/reports/evolve-summary.md)  
**Predecessor**: S066 / EV-056 / #988 (unified + collapsible on stage)  
**Corpus**: [Corpus: product §F7.q] [Corpus: journeys §UJ-056] [Corpus: tests §UJ-056]
[Corpus: decisions §EV-058] [Corpus: deploy] [Corpus: adr/ADR-034]

### Scope (Phase 0 — locked 2026-08-17)

| ID | Decision |
|----|----------|
| D-S068-e0 | **1a/2b/3a/4a/5a** — evolve #983; persist + synced-scroll AC; stage; proceed |
| D-S068-route | **1a/2a/3a** — Lean `00→16→01→02→10→13`; Spec→Build closed |
| D-S068-ui-preview | **1** — http://127.0.0.1:18000/ |
| D-S068-board | **1** — #983 → In progress |
| D-S068-ev-confirm | **1a** — EV0–EV9 carry-forward |
| D-S068-01-ac | **2b** — AC1–AC5; synced scroll **best-effort** (not blocking) |
| D-S068-01-control | **3a** — segmented Inline \| Side-by-side |
| D-S068-01-uj | **4a** — deepen UJ-056 + TC-EV058-001..005 |
| D-S068-merge | **1** — Merge #994 → stage; run 13 |
| D-S068-13 | **1** — Approve 13; close on stage (no promote) |
| D-S068-close | **1** — Close EV-058/S068; #983 Done; `active_session=null` |

### Acceptance (approved `D-S068-01-ac=2b`)

1. Switch Inline ↔ Side-by-side without reload.
2. Default remains unified.
3. Side-by-side via existing line-diff util; no new npm `diff`.
4. Preference in localStorage.
5. TAC/diagnostics/collapse kept; Vitest + Playwright both modes; H4–H5 via 13.
   Synced scroll is best-effort polish only.

### Out of scope

- API/backend; new npm `diff`; C14N/`match_status`; #982 whitespace; promote to main;
  non–Quality-metrics UI

---

## Cycle EV-057 — M0 Ready: apex redirect + accumulate ZIP + validate IWXXM (#948 / #903 / #838) (S067)

**Session**: S067-m0-ready-apex-accumulate-validate  
**Features**: deepen **F7**; **F1**/**F6** (#903); **F2**/**F4** (#838); deploy hosts (#948)  
**Started**: 2026-08-15  
**Branch**: `evolve/EV-057-m0-ready-apex-accumulate-validate` (base `stage@b796882e`)  
**Status**: **completed** — `D-S067-13=1a` / `D-S067-close=1a`; on `stage`; promote deferred (`D-S067-promote=2b`)  
**Issues**: [#948](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/948), [#903](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/903), [#838](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/838) — board **Done**  
**PRs**: [#991](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/991) @ `d7022f1f`; follow-up [#992](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/992) @ `3af364fb`  
**Reports**: [evolve-report-EV-057.md](../evolve-report-EV-057.md) · [evolve-summary.md](../sessions/S067-m0-ready-apex-accumulate-validate/reports/evolve-summary.md)
**Parent**: M0 Ready queue after S066 / EV-056  
**Corpus**: [Corpus: product §F7] [Corpus: product §F1] [Corpus: product §F6]
[Corpus: product §F2] [Corpus: product §F4] [Corpus: tech-spec] [Corpus: deploy]
[Corpus: journeys] [Corpus: decisions §EV-057]

### Scope (Phase 0 — locked 2026-08-15)

| ID | Decision |
|----|----------|
| D-S067-first | **1a** — Open on #948 first within the pack |
| D-S067-pack | **2c** — One evolve cycle for all three Ready issues |
| D-S067-success | **3c** — Ship to `stage` + promote path available |
| D-S067-oos | **1a** — Exclude #841/#727/#874; S056 ruleset-admin leftover; drive-bys |
| D-S067-promote | **2b** — Land all three on `stage` first; promote only after re-approve |
| D-S067-blockers | **3a** — None known; surface as found |
| D-S067-preset | **4a** — Standard (`00→16→01→02→04→07→08→09→10→11→12→13`) |
| D-S067-type | **1a** — `feature` session → 16-evolve |
| D-S067-order | **2a** — #948 → #903 → #838 |
| D-S067-ui-preview | **3a** — Remind at 11-verify-impl (non-deployed) |
| D-S067-proceed | **4a** — Open S067 + EV-057; write brief/routing/plan card |
| D-S067-board | **1** — #948 → In progress (WIP 1); #903/#838 stay Ready until started |
| D-S067-903-cap | **1c** — Soft accumulate cap **≤200** |
| D-S067-948-ingress | **2a** — Extend prod FE Ingress apex/www → app `$request_uri` |
| D-S067-948-redirect | **1a** — Tiny nginx redirect Deployment (webhook blocks `$` on `permanent-redirect`; snippets off) |
| D-S067-948-apply | **1a** — Apply sibling apex Ingress on prod after public Dig green (2026-08-16) |
| D-S067-gateA | **1** — PASS Gate A → 04-tech-plan |
| D-S067-04-plan | **1** — EP approved (sibling apex Ingress; M1→M2→M3) |
| D-S067-04-next | **1a** — skip 05/06 → 07-build M1 |
| D-S067-12-resume | **1a** — finish checklist tip `d05c23b7` / #991 |
| D-S067-12-scope | **1a** — no delta; promote held |
| D-S067-12-risks | **1a** — approve standard stage mitigations |
| D-S067-12-merge | **1a** — merge #991 → stage → 13 |
| D-S067-13-start | **1a** — smoke staging H1–H5 + UJ-057/058 |
| D-S067-13-scope | **1a** — staging only; promote later |
| D-S067-13-depth | **1a** — CI smoke + verify_connectivity + quick UJ |
| D-S067-13-uj058 | **1a** — fix TacEditor aria-label + #992 → stage |
| D-S067-13 | **1a** — approve 13 complete; promote deferred |
| D-S067-close | **1a** — close cycle on stage; promote later on request |

### Acceptance (`D-S067-01-ac=1`)

**#948 / F30**
1. `https://tac-to-iwxxm.com` → `https://app.tac-to-iwxxm.com` (301 or equivalent).
2. Path + query preserved.
3. `www` if DNS/cert covers; HTTP ends on HTTPS app URL.
4. TLS covers apex (and `www` if enabled).
5. Document **prod FE Ingress** + **`metar-apex-redirect`** in deploy docs (`D-S067-948-ingress=2a`, `D-S067-948-redirect=1a`).

**#903 / F7.r / UJ-057**
1. N≥2 sequential successes remain visible.
2. Download all → one ZIP of accumulated IWXXM.
3. Empty custom name → `{stem}_{yyyyMMddHHmmss}.zip` (≈8 sanitized TAC chars of first success).
4. Custom basename → `{base}.zip` (#664).
5. Explicit clear/reset.
6. Failed convert leaves prior successes.
7. Soft accumulate cap **≤200**; clear error when over (`D-S067-903-cap=1c`).
8. UJ-057 / TC-EV057-903-* + H4–H5.

**#838 / F7.s / UJ-058**
1. Paste IWXXM → validate without TAC convert.
2. Upload one `.xml` → F2 results.
3. Invalid/non-IWXXM → structured fail.
4. F4 version/profile parity.
5. Guest-usable (no Supabase).
6. UJ-058 / TC-EV057-838-* + H4–H5.

### Out of scope

- Epic [#841](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/841) and children #727 / #874 (M4/M5)
- S056 converter-perf ruleset apply (repo admin; not a ticket)
- Batch disseminate of accumulated conversions; F33 as substitute for #903
- Reverse-engineering TAC from IWXXM
- Auto-promote to `main` without re-approve after full pack on `stage`

---

## Cycle EV-056 — Quality metrics detail page + collapsible diffs (#988) (S066)

**Session**: S066-quality-metrics-diff-page  
**Features**: deepen **F7.q** only  
**Started**: 2026-08-11  
**Branch**: `evolve/EV-056-quality-metrics-diff-page` (base `stage@340b3cf6`)  
**Status**: **completed** — closed on stage (`D-S066-13=1` / `D-S066-close=1`; #989 @ `b4a63ab8`)  
**Issues**: [#988](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/988)  
**Parent**: S065 / #987 pretty-print hotfix; EV-054 / EV-055 Quality metrics  
**Corpus**: [Corpus: product §F7.q] [Corpus: journeys §UJ-056] [Corpus: tests]
[Corpus: decisions §EV-056]

### Scope (Phase 0 — locked 2026-08-11)

| ID | Decision |
|----|----------|
| D-S066-route | **1** — Lean (`00→16→01→02→10→13`); PR → stage |
| D-S066-ui-preview | **1** — non-deployed http://127.0.0.1:18000/ |
| D-S066-route-shape | **1** — `/quality/:stem` + back-to-list |
| D-S066-context-n | **1** — default 3 context lines |
| D-S066-list | **1** — navigate to detail; list via back |
| D-S066-board | **1** — #988 In progress |
| D-S066-pr | **1** — Push + PR → stage → CI → 13 |
| D-S066-13 | **1** — Approve 13; H0c–H5 PASS on staging |
| D-S066-close | **1** — Close EV-056 / S066 on stage; #988 Done; promote deferred |

### Acceptance (`D-S066-01-ac=1`)

1. List row opens dedicated `/quality/:stem` (shareable) with back-to-list.
2. Official/Converted/TAC panes remain; normalized = pretty C14N.
3. Diff shows collapsible equal-context hunks (default 3; expand hunk / expand all).
4. Unequal SIGMET stems remain navigable and readable on staging.
5. UJ-056 / TC-EV056; FE unit + Playwright; H4–H5 via 13.

### Out of scope

- `match_status` / C14N equality / fixture generator changes
- New npm diff library unless AskQuestion
- Promote to `main` unless asked
- API contract change unless routing requires it

---

## Cycle EV-055 — Quality metrics 2025-2 follow-ups (#982 / #980 / #979) (S064)

**Session**: S064-quality-metrics-2025-2-followups  
**Features**: deepen **F7.q**; deepen **F2** / **F13** as needed for 2025-2 validate; **F4** only if messaging requires  
**Started**: 2026-08-11  
**Branch**: `evolve/EV-055-quality-metrics-2025-2-followups` (base `stage@4fd51e39`)  
**Status**: **completed** — closed on stage (`D-S064-13=1` / `D-S064-close=1`; #985 @ `4b48c8d8`)
**Issues**: [#982](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/982), [#980](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/980), [#979](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/979)  
**Parent**: EV-054 / S063 / [#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836) (closed)  
**Corpus**: [Corpus: product §F7] [Corpus: product §F2] [Corpus: product §F13]
[Corpus: product §F4] [Corpus: api] [Corpus: tests] [Corpus: system-spec]
[Corpus: adr/ADR-035] [Corpus: decisions §EV-055]

### Scope (Phase 0–1 — locked 2026-08-11)

| ID | Decision |
|----|----------|
| D-S064-intent | **1** — Investigate and fix/ship all three when disposition is clear |
| D-S064-parked | **1** — Leave EV-043 / EV-044 parked; open S064 / EV-055 |
| D-S064-success | **1** — Quieter diffs + clear disposition for both 2025-2 warnings |
| D-S064-normalize | **1** — Normalize both official and converted XML; `match_status` = normalized equality |
| D-S064-spike-pref | **3** — Prefer enable Schematron for 2025-2 if native can evaluate xslt2; XSD fix optional |
| D-S064-surface | **1** — Operator surface = Quality metrics tab (F7.q) |
| D-S064-engine | **1** — Allow F2/F13 (`iwxxm-validate`) changes for #980/#979 |
| D-S064-oos | **1** — Accept OOS: no vendor hand-edits; no #836 redo; no DOKS; no encode parity |
| D-S064-route | **1** — Standard; PR → `stage` |
| D-S064-branch | **1** — Branch from `stage@4fd51e39` |
| D-S064-board | **1** — #982/#980/#979 → In progress (WIP 3 > ≤2; user override) |
| D-S064-01-manifest | **1** — feature-list + journeys + test-plan + api-contract + decisions; skip spec/config/deploy |
| D-S064-ui-preview | **2** — No non-deployed UI preview at 01; docs/repo only |
| D-S064-uj | **1** — Deepen UJ-056 only (no UJ-057) |
| D-S064-01-ac | **1** — Lock AC1–AC7 as drafted |
| D-S064-regen | **1** — Regenerate corpus_metrics for normalized match_status |
| D-S064-gateA-M1 | **1** — Shared C14N helper: generator + FE |
| D-S064-gateA-M2 | **override** — Panes default normalized; override → un-normalized |
| D-S064-sch-hard | **1** — #980 Schematron enable hard (overrides `D-S064-spike-pref=3`) |
| D-S064-c14n | **1** — Always W3C C14N (`D-S064-gateA-M4=2`) |
| D-S064-xsd-hard | **1** — #979 SCHEMA_IMPORT fix required (H3=2) |
| D-S064-gateA | **1** — PASS Gate A; → 04-tech-plan |
| D-S064-04-plan | **1** — Approve EP as drafted: 17 tasks M1–M5; engine→C14N→regen→FE→E2E; lxml+TS C14N; ADR vs ADR-032; no new deps/CORS |
| D-S064-c14n-host | **1** — Python C14N in `packages/iwxxm-validate` (not shared); FE TS helper |
| D-S064-05 | **1** — Gate B PASS; C1 resolved; → 07 M1 |
| D-S064-c14n-volatile | **1** — C14N **after** volatile-attr strip (`gml:id` / UUID / codes.wmo.int hrefs per ADR-032 rules); not pure C14N; not C14N-of-ADR-032-repr — ADR-035 amend 2026-08-11 |
| D-S064-m5 | **1** — M5 local Playwright deepen done; tip push for CI; board stays **In progress** until implementing PR opens (`D-S064-board=1`) |
| D-S064-gateC | **1** — PASS Gate C; push tip + continue 09-qa |
| D-S064-09-10-continue | **1** — continue → 11-verify-impl |
| D-S064-ui-preview-11 | **1** — Non-deployed preview at http://127.0.0.1:18000/ |
| D-S064-uj056 | **1** — Approve UJ-056; waive live T3 until 12/13 |
| D-S064-11 | **1** — Approve F7.q + F2/F13 deepen; proceed toward 12 |
| D-S064-12-start | **1** — continue → 12-verify-deploy; open PR→stage |
| D-S064-12 | **1** — Approve checklist + merge #985 → `stage`, then continue 13 |
| D-S064-13 | **1** — Approve 13; close EV-055 / S064 on stage (no promote) |
| D-S064-close | **1** — Cycle + session closed on stage |

### Deploy smoke (13 — COMPLETE `D-S064-13=1`)

| Item | Result |
|------|--------|
| Merge #985 | `4b48c8d8` on `stage` |
| Staging CD | [31534191417](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31534191417) Deploy + Staging smoke **success** |
| H1–H5 | PASS on `api\|app.staging.tac-to-iwxxm.com` |
| Board | #982/#980/#979 **Done** |
| Docs follow-up | PR [#986](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/986) |
| Sign-off | `D-S064-13=1` / `D-S064-close=1` |

### Build closeout (07 — M1–M5)

| M | Tip note |
|---|----------|
| M1 | Native Schematron/XSD for quality metrics |
| M2 | `c14n_xml` + FE `c14nXml.ts` + ADR-035 |
| M3 | Generator `c14n_equal` + corpus regen (`D-S064-c14n-volatile=1`) |
| M4 | C14N panes + raw override + validate chips |
| M5 | UJ-056 / TC-EV055-007 Playwright deepen; E2E badge 83 |

### Tech plan (04 — `D-S064-04-plan=1`)

| Artifact | Path |
|----------|------|
| Execution plan | `docs/sessions/S064-quality-metrics-2025-2-followups/reports/execution-plan.md` |
| Build Plan Card | `docs/sessions/S064-quality-metrics-2025-2-followups/build-plan-card.md` |

| M | Goal |
|---|------|
| M1 | Engine #980/#979 hard |
| M2 | C14N helpers Py+FE + ADR |
| M3 | Generator + corpus_metrics regen |
| M4 | FE panes + diff + validate chips |
| M5 | Playwright + docs/CI |

### Approved scope (verbatim)

Whitespace-normalize via **W3C C14N** for official and converted XML so Quality metrics
`match_status` and unified diffs reflect semantic differences (#982). Shared helper in
generator + FE; panes default to normalized XML with override to raw. **Hard** this cycle:
enable Schematron for IWXXM 2025-2 xslt2 (#980) and fix `SCHEMA_IMPORT_WARNING` (#979).
Operator-facing consumer remains the Quality metrics tab; engine changes allowed in
`packages/iwxxm-validate`.

### Out of scope

- Hand-editing `vendor/schemas/*`
- Reopening / redoing closed #836 Quality metrics shell
- DOKS / F30 (EV-043 / EV-044 remain parked)
- New product families / encode parity
- `stage`→`main` unless explicitly approved later

### Preset

**Standard** — `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`
(skip `03`, `06`).

### Corpus cites / waivers

| Ref | Kind | Target | Notes |
|-----|------|--------|-------|
| `[Corpus: product §F7]` | cite | F7.q deepen — diffs + validate UX | |
| `[Corpus: product §F2]` | cite | validate engine / SCHEMA_* / SCHEMATRON_* | |
| `[Corpus: product §F13]` | cite | native Rust Schematron path | |
| `[Corpus: product §F4]` | cite | version-line skip messaging if needed | |
| `[Corpus: api]` | cite | quality-metrics match_status semantics | |
| `[Corpus: tests]` | cite | TC-EV055 + UJ-056 | |
| `[Corpus: journeys]` | cite | UJ-056 deepen | |
| — | waiver | none | |

### Acceptance criteria (01 — `D-S064-01-ac=1`)

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | Formatting-only diffs no longer dominate; semantic remain (C14N) | TC-EV055-001 |
| AC2 | `match_status` = C14N equality both sides; no internal doc ids | TC-EV055-002 |
| AC3 | C14N helper tests + golden; vendor read-only; shared generator+FE | TC-EV055-003 |
| AC4 | #980 Schematron **enabled** for 2025-2 (hard) | TC-EV055-004 |
| AC5 | #979 SCHEMA_IMPORT **fixed** (hard) | TC-EV055-005 |
| AC6 | Validate chips + normalized panes w/ override | TC-EV055-004..005 / 007 |
| AC7 | corpus_metrics regen + UJ-056 smoke | TC-EV055-006..007 |

---

## Cycle EV-054 — Quality metrics tab / official IWXXM corpus (#836) (S063)

**Session**: S063-quality-metrics-tab  
**Features**: deepen **F7** (note **F7.q** in feature-list; no new top-level Fn)  
**Started**: 2026-08-10  
**Completed**: 2026-08-11  
**Branch**: `evolve/EV-054-quality-metrics-tab` (base `stage@f2926ac8`)  
**Status**: **completed** (`D-S063-13=1` / `D-S063-close=1`) — [#977](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/977) → `stage` @ `4fd51e39`; [#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836) closed; **no stage→main** (stay on stage)  
**Issue**: [#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836) (closed)  
**Follow-ups**: [#979](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/979)–[#983](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/983)  
**Corpus**: [Corpus: product §F7] [Corpus: product §F25] [Corpus: journeys]
[Corpus: tests] [Corpus: adr/ADR-032] [Corpus: adr/ADR-025] [Corpus: api]
[Corpus: system-spec] [Corpus: decisions §EV-054]

### Closeout (2026-08-11)

| ID | Decision |
|----|----------|
| D-S063-13 | **1** — Approve staging smoke; close EV-054 / S063; stay on stage (no promote) |
| D-S063-close | **1** — Close #836; clear `active_session`; file follow-ups #979–#983 |

Evidence: CI/CD [31453072506](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31453072506) SUCCESS; H0c/H1/H3/H4/H5 + live UJ-056 PASS; `reports/deploy-smoke.md` / `reports/evolve-summary.md`.

### Scope (Phase 0–1 — locked 2026-08-10)

| ID | Decision |
|----|----------|
| D-S063-route | **1** — Standard: `00→16→01→02→04→05→07→08→09→10→11→12→13`; skip `03,06` (05 re-enabled Gate A) |
| D-S063-ui-preview | **2** — No non-deployed UI preview at open; docs/repo only |
| D-S063-scope | **1** — Full #836 scope (not METAR/SPECI-only shell); iterative ship OK in build |
| D-S063-fn | **1** — Deepen **F7** only; document **F7.q** as sub-id note (no F34) |
| D-S063-compute | **1** — Prefer **precomputed** fixture/CI metrics JSON for default view; on-demand refresh optional later |
| D-S063-01-manifest | **1** — feature-list + journeys (UJ-056) + test-plan + decisions; skip API/config unless 04 needs them |
| D-S063-01-ac | **1** — Lock AC1–AC7 |
| D-S063-diff | **2** — Unified XML diff in v1 (plus inspectable raw panes) |
| D-S063-shell-tab | **1** — **Separate primary app-shell tab** (peer to Convert / History), not a FileConverter panel |
| D-S063-gateA | **2** — PASS Gate A; **require public metrics HTTP API in v1** (re-open api-contract; override FE-only bundle M1) |
| D-S063-04-plan | **1** — Approve 04 execution plan as drafted (single corpus blob; no npm `diff`) |
| D-S063-05 | **1** — Gate B PASS; C1=15 tasks; C2 keep Impl→Test (milestone-exit green); C3–C7 hygiene applied |

### Approved scope (verbatim)

Add an operator **Quality metrics** primary shell tab (F7.q / F7 deepen — **not** a panel
inside the convert workbench) that imports the official WMO IWXXM example corpus
(vendor pin + mirrored TAC peers) and lets operators explore conversion quality **by
file / product type**: corpus browser, official match / comparison with **unified XML
diff**, residuals, lint issues, validation issues, and drill-down. Default view offline /
bundled (precomputed metrics JSON). UI complements CI matrices (#815 / #831); does not
replace them.

### Out of scope

- Replacing CI residual / encode / lint matrices
- Promoting `wmoReference` → `wmoPass` encode equality
- Live re-download of upstream WMO trees on every page load
- New products beyond catalog / F6 (+ deferred) inventory
- Mutation testing (#874), Schemathesis (#727)
- Workbench epic (#840) unless tiny deep-link
- `stage`→`main` unless explicitly approved later

### Preset

**Standard** — `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`.

### Corpus cites / waivers

| Ref | Kind | Target | Notes |
|-----|------|--------|-------|
| `[Corpus: product §F7]` | cite | Fn deepen + F7.q note | |
| `[Corpus: product §F25]` / F7.g | cite | catalog inventory | |
| `[Corpus: journeys]` | cite | new UJ + UJ-039 deepen | |
| `[Corpus: tests]` | cite | H4–H5 / Playwright smoke | |
| `[Corpus: adr/ADR-032]` | cite | wmoPass / wmoReference tiers | |
| `[Corpus: adr/ADR-025]` | cite | decode residuals | |
| — | waiver | none | |

### Acceptance (locked `D-S063-01-ac=1`)

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | Separate primary Quality metrics tab; corpus by product / file type | TC-EV054-001..002 |
| AC2 | File select → official + our XML/TAC + match + **unified XML diff** | TC-EV054-003 |
| AC3 | Residuals / lint / validate panels (empty when clean) | TC-EV054-004 |
| AC4 | Product summary counts match precomputed fixture via `GET /quality-metrics` | TC-EV054-005 / 008 |
| AC5 | Gap / deferred stems labeled; no silent omissions | TC-EV054-002 |
| AC6 | H4–H5 or Playwright: open → filter → passer → expected diagnostics | TC-EV054-007 |
| AC7 | No Supabase / no live WMO fetch; metrics from public API + precomputed fixtures | TC-EV054-006 / 008 |

Journey: **UJ-056**. API: [Corpus: api] `GET /api/v1/quality-metrics*`.

### Stage log

| Stage | Completed | Notes |
|-------|-----------|-------|
| 00-context | 2026-08-10 | D-S063-route=1; ui-preview=2; board #836 In progress |
| 16-evolve Phase 0–1 | 2026-08-10 | scope/fn/compute locked |
| 01-requirements | 2026-08-10 | D-S063-01-ac=1; diff=2; shell-tab=1; UJ-056 + TC-EV054 |
| 02-verify-plan | 2026-08-10 | Gate A PASS (`D-S063-gateA=2`); api-contract reopened; **05 re-enabled** |
| 04-tech-plan | 2026-08-10 | `D-S063-04-plan=1` — M1→M5 / 15 tasks; client-side line diff; single corpus blob |
| 05-verify-tech | 2026-08-10 | `D-S063-05=1` — Gate B PASS; C1–C7 resolved; handoff 07 M1 |
| 07-build M1–M4 | 2026-08-10 | Generator + API + shell/list + detail/diff; tip through `6a385f79` |
| 07-build M5 | 2026-08-10 | T5.1 Playwright UJ-056 / TC-EV054-007 green; T5.2 `make generate-quality-metrics`; T5.3 docs + tip push |
| 08-verify-build | 2026-08-10 | Gate C local PASS — lint/format/typecheck/units/H0c/UJ-056; `reports/verification-report.md`; CI via PR→stage |

### Build M5 notes (2026-08-10)

| Item | Evidence |
|------|----------|
| Playwright | `apps/e2e/uj056-quality-metrics.e2e.spec.ts` — open tab → METAR filter → `metar-A3-1` detail + deferred `metar-NIL-collect`; asserts list/detail API calls |
| Diff pane | Semantic `match_status=equal` may still show line hunks (gml:id / whitespace); assert `unified-diff` + empty\|body |
| Regen | `make generate-quality-metrics` → `scripts/ci/generate_quality_metrics.py`; artifact README notes CI does not auto-regen |
| E2E badge | README `E2E_tests-82` |
| H4–H5 live | Deferred to stages **12/13** after staging deploy (C7) |

---

## Cycle EV-053 — Vitest branches ≥95 FileConverter follow-up (S062)

**Session**: S062-vitest-branches-95  
**Features**: deepen **F29**, **M5** (no new Fn)  
**Started**: 2026-08-10  
**Branch**: `evolve/EV-053-vitest-branches-95` (base `stage@6f25c0b1`)  
**Status**: **completed** (`D-S062-merge=1` / `D-S062-close=1`) — [#973](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/973) → `stage` @ `ef68ac67`; [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968) closed; no stage→main  
**Corpus**: [Corpus: product §F29] [Corpus: product §M5] [Corpus: tests]
[Corpus: adr/ADR-007] [Corpus: decisions §EV-052] [Corpus: decisions §EV-053]

### Build closeout notes (2026-08-10)

| Item | Evidence |
|------|----------|
| Aggregate Vitest branches | **96.39%** @ `b3416505` (suite green) |
| FileConverter branches (AC5) | **95.95%** (521/543) — `reports/m3-ac5-coverage-proof.md` |
| Inventory `branch_waiver` | **resolved** — S061 `coverage-surface-inventory.yaml` |
| Parent waiver | `D-S061-cov-branches=3` closed by EV-053 / #968 |
| Merge | [#973](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/973) → `stage` @ `ef68ac67` (`D-S062-merge=1`) |
| Issue | [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968) **CLOSED** (`D-S062-close=1`) |

### Close decisions (2026-08-10)

| ID | Decision |
|----|----------|
| D-S062-merge | **1** — Merge [#973](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/973) → `stage` |
| D-S062-close | **1** — Close #968; complete EV-053 / S062; no stage→main this cycle |

### Scope (Phase 0–1 — locked 2026-08-10)

| ID | Decision |
|----|----------|
| D-S062-route | **1** — Standard: `00→16→01→02→04→07→08→09→11`; skip `03,05,06,10,12,13` |
| D-S062-ui-preview | **2** — No non-deployed UI preview; Vitest/docs only |
| D-S062-dirty | **2** — S061 closeout already on `stage` via [#972](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/972); open clean from `stage` |
| D-S062-fc-strategy | **1** — Re-include `FileConverter.tsx` in Vitest coverage; fill tests until aggregate ≥95 |
| D-S062-01-manifest | **1** — Delta: feature-list + test-plan + decisions (+ inventory in 07) |
| D-S062-01-ac | **1** — Lock AC1–AC5 (AC5 = FileConverter ≥95% branches when included) |
| D-S062-gateA | **1** — PASS Gate A + M1 approve (AC5 via coverage JSON/html + session verify; optional CI if cheap) |
| D-S062-m1 | **1** — Same as Gate A M1 verdict |
| D-S062-04-plan | **1** — Approve execution plan as drafted; skip 05; start 07 M1 |

### Acceptance (locked `D-S062-01-ac=1`)

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | Vitest `branches` threshold ≥95 in `apps/frontend/vitest.config.ts` (lines/stmts/funcs remain ≥95) | TC-EV053-001 |
| AC2 | FE coverage suite green with FileConverter in the coverage set | TC-EV053-002 |
| AC3 | Coverage inventory `branch_waiver` resolved; excludes justified (no silent soft gate) | TC-EV053-003 |
| AC4 | Standing docs cite closeout; #968 closable after merge | TC-EV053-004 |
| AC5 | With FileConverter included, **that file’s** branch coverage ≥95% | TC-EV053-005 |

### Out of scope

- Lowering lines/stmts/funcs below 95
- #874 mutation / #727 Schemathesis / #836 UI metrics
- stage→main this cycle
- Operator UI redesign
- Keeping FileConverter excluded while only raising aggregate branches

### Preset

**Standard** — `00 → 16 → 01 → 02 → 04 → 07 → 08 → 09 → 11`.

### Parent waiver

`D-S061-cov-branches=3` — EV-052 enforced lines/stmts/funcs ≥95; branches floor 84 +
explicit child #968 (not silent). This cycle **closes** that waiver.

---

## Cycle EV-052 — CI polish + quality PR stats + free Sentry/Redis/Orval (S061)

**Session**: S061-ci-polish-quality-pr-stats  
**Features**: deepen **F29**, **F6**, **F21**, **F30**, **M5** (no new Fn)  
**Started**: 2026-08-09  
**Branch**: `evolve/EV-052-ci-polish-quality-pr-stats` (base `stage@80197a58`)  
**Status**: **completed** (`D-S061-close=1`) — [#969](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/969) → `stage` @ `fd84c00a`; docs [#971](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/971) → `stage` @ `3e019b57`; no stage→main  
**Corpus**: [Corpus: product §F29] [Corpus: product §F6] [Corpus: product §F21]
[Corpus: product §F30] [Corpus: product §M5] [Corpus: tests] [Corpus: adr/ADR-007]
[Corpus: adr/ADR-006] [Corpus: adr/ADR-031] [Corpus: tech-spec] [Corpus: deploy]

### Scope (Phase 0–1 — locked 2026-08-09)

| ID | Decision |
|----|----------|
| D-S061-intake | **1** — Open S061 / EV-052 for quality PR comment + #950 + #900 (implement 2–4) |
| D-S061-quality | **1** — Quality-matrix + annex3/`iwxxm_us` golden outcome stats by product × profile |
| D-S061-comment | **1** — Second sticky PR comment (separate from EV-036 coverage) |
| D-S061-900 | **2–4** — Implement free Sentry + Redis rate limits + Orval/openapi-typescript |
| D-S061-redis | **1** — Upstash Redis free (no new DOKS Redis Deployment) |
| D-S061-route | **1** — Standard: `00→16→01→02→04→05→07→08→09→11`; skip `03,06,10,12,13` |
| D-S061-01-ac | **1** — Accept AC1–AC12 (continue after Redis lock) |
| D-S061-ui-preview | **3** — N/A at intake (no operator UI product work) |
| D-S061-gateA | **1** — PASS Gate A → 04 |
| D-S061-04-plan | **1** — Approve execution plan as drafted; **openapi-typescript** (not Orval) |
| D-S061-gateB | **1** — PASS Gate B → 07-build M1 |
| D-S061-cov-branches | **3** — Enforce Vitest lines/stmts/funcs ≥95; **branches** floor 84 + child [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968) (FileConverter excluded from Vitest collection; not silent) |
| D-S061-ui-preview-11 | **1** — Non-deployed local preview accepted at 11 (`:18000` / `:18001`) |
| D-S061-11 | **1** — Approve AC1–AC12 / Fn deepen; 11 complete; Phase 4 close / merge-path next |
| D-S061-merge | **1** — Commit session verify artifacts + push tip, then merge [#969](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/969) → `stage` (no stage→main this cycle; 12/13 waived per routing) |
| D-S061-close | **1** — Merge [#971](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/971) → `stage`, close EV-052 / S061; leave [#968](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/968) open |

### Acceptance

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | Coverage surface inventory vs ≥95% | TC-EV052-001 |
| AC2 | Every surface enforces ≥95% in CI; soft/deferred gates removed | TC-EV052-002 |
| AC3 | Suite green with gates; excludes justified | TC-EV052-003 |
| AC4 | Second sticky PR comment: match/soft-diff/fail/skip by product × profile | TC-EV052-004 |
| AC5 | Comment formatter tested + sticky update idempotent | TC-EV052-005 |
| AC6 | Sentry on API+FE+worker when DSN set; free Developer documented | TC-EV052-006 |
| AC7 | slowapi → Upstash when configured; in-memory fallback when unset | TC-EV052-007 |
| AC8 | Shared-store rate-limit behavior unit/integration covered | TC-EV052-008 |
| AC9 | OpenAPI → typed FE client; CI/commit policy | TC-EV052-009 |
| AC10 | Standing docs + ADR notes accurate | TC-EV052-010 |
| AC11 | Free-tier + no new DOKS Redis service documented | TC-EV052-011 |
| AC12 | PR CI green with new jobs/tests | TC-EV052-012 |

### Out of scope

- Paid Sentry Team / DO Managed Valkey unless free path fails
- #874 mutation / #727 Schemathesis / #836 UI metrics tab
- AMS #958; stage→main promote this cycle
- New in-cluster Redis Deployment

### Preset

**Standard** — `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`.

### Infra note

See `docs/sessions/S061-ci-polish-quality-pr-stats/reports/infra-free-tier.md`.

---

## Cycle EV-051 — Tag-driven prod deploy + full CI Deploy needs (S060)

**Session**: S060-tag-driven-prod-deploy  
**Features**: deepen **F30** (no new Fn)  
**Started**: 2026-08-09  
**Branch**: `evolve/EV-051-tag-driven-prod-deploy` (merged → `stage` @ `8882856b`)  
**Status**: **completed** 2026-08-09 (`D-S060-merge=1` / `D-S060-close=1`; PR [#966](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/966) → `stage` @ `8882856b`)  
**Corpus**: [Corpus: product §F30] [Corpus: deploy] [Corpus: adr/ADR-034] [Corpus: tests]

### Scope (Phase 0–1 — locked 2026-08-09)

| ID | Decision |
|----|----------|
| D-S060-open | **1** — Open S060 / EV-051; EV-043/044 remain parked |
| D-S060-scope | **1** — Design 2+3+4: widen Deploy `needs` (+ `e2e-smoke`); no auto Deploy on `main` push; prod via `vYYYY.MM.DD-deploy` tag + optional `workflow_dispatch`; staging stays auto after full CI |
| D-S060-route | **1** — Lean+: `00→16→01→02→03→07→08→09→11`; skip `04,05,06,10,12,13` |
| D-S060-gateA | **1** — Gate A PASS; handoff 07/08/09/11 |
| D-S060-11-next | **1** — Approve AC1–AC6; push + PR → `stage` (12/13 skipped) |
| D-S060-merge | **1** — Merge #966 when CI green (user continue) |
| D-S060-close | **1** — Close EV-051 / S060; clear `active_session` |

### Acceptance

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | Deploy `needs` includes prior set **plus** `e2e-smoke` (frontend remains inside `test` matrix) | TC-EV051-001 |
| AC2 | Push/merge to `stage` still auto-Deploys **staging** after those needs pass | TC-F30-010 (amended) / TC-EV051-002 |
| AC3 | Push/merge to `main` runs full CI but **does not** Deploy prod | TC-EV051-003 |
| AC4 | Push tag matching `vYYYY.MM.DD-deploy` (pattern `v*-*-deploy`) on a commit runs prod Deploy after full CI | TC-EV051-004 / TC-F30-014 |
| AC5 | `workflow_dispatch` can trigger prod Deploy (escape hatch) after full CI | TC-EV051-005 |
| AC6 | ADR-034, `docs/deploy.md`, `doks-promote-from-stage.mdc`, feature-list F30 / TC-F30-010 amended; solo-dev approval = tag (or dispatch), not Environment reviewers | TC-EV051-006 |

### Out of scope

- GitHub Environment required reviewers
- Quality-pack workflows as Deploy `needs`
- Chat/Slack approve
- PyPI publish path changes
- Resume EV-043 / EV-044
- Promote `stage`→`main` / first prod tag cutover in this cycle (docs+workflow only → `stage`)

### Preset

**Lean+** — `00 → 16 → 01 → 02 → 03 → 07 → 08 → 09 → 11`.

---

## Cycle EV-050 — codes.wmo.int Validated: harvest + tac-validate membership (#959) (S059)

**Session**: S059-codes-wmo-validated  
**Features**: deepen **F6 / F12 / F15 / F20 / F23 / F24 / F28** (no new Fn; F6 for
`annex3` vs `iwxxm_us` profile compare; fixtures may touch encode packs)  
**Started**: 2026-08-09  
**Branch**: `evolve/EV-050-codes-wmo-validated` (merged → `stage` @ `2815ffbe`)  
**Status**: **completed** 2026-08-09 (`D-S059-merge=1` / `D-S059-close=1`; PR [#964](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/964))  
**Issues**: [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959) (closed);
parent [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889) (already CLOSED —
Validated satisfied; residual Present/Cited depth defer+cite in session reports);
epic [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846);
compose [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859),
[#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882)  

**Corpus**: [Corpus: product §F6/F12/F15/F20/F23/F24/F28], [Corpus: tests],
[Corpus: tech-spec], [Corpus: decisions] · domain opt-in
`docs/domain/rules/*`, `docs/domain/mining/*`, `docs/domain/TAC_VALIDATION.md`

### M2 close (T2.4 — 2026-08-09)

AC4 / TC-EV050-004: aggressive `RE*` / AIRMET `_` / SpaceWx composed / TCU packs landed;
coverage delta + residual **defer+cite** (no new GitHub children) in
`docs/sessions/S059-codes-wmo-validated/reports/fixture-coverage-delta-t2.4.md`.
Exhaustive 402 weather + remaining register depth stay under #959/#889 per OOS.

### M3 close (T3.1–T3.4 — 2026-08-09)

AC7 / TC-EV050-007: dual-profile harness + disposition
(`reports/dual-profile-disposition.md`) — N/A for VAA/TCA/SWXA/VONA.
AC8 / TC-EV050-008: true-error fix — `REMARK_US_EXTENSION` gated to `iwxxm_us` only;
`INVALID_REMARK` remains under both. Tip after M3: `271efa49`.

### M4 / AC5 — #889 Validated satisfied (T4.2 — 2026-08-09)

**Decision `D-S059-validated=1`:** Parent [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889)
**Validated** triad element is **satisfied** by S059 / EV-050 (not re-scoped). Lean waiver
`D-S055-validated=1` is superseded for this element.

| Criterion | Evidence |
|-----------|----------|
| Offline harvest → CI membership sets | AC1 / TC-EV050-001 — `wmo_membership.json` + `make membership-regen` |
| Happy + unknown/sad per v1 families | AC2 / TC-EV050-002 — membership matrix |
| Cadence vs `iwxxm-codelists` pin | AC3 / TC-EV050-003 — tech-spec + TAC_VALIDATION + RULE_SOURCE_URLS |
| Fixture gaps closed or defer+cite | AC4 / TC-EV050-004 — `fixture-coverage-delta-t2.4.md` |
| Dual-profile disposition + true-error fix | AC7–AC8 — disposition + `REMARK_US_EXTENSION` gating |
| #882 notify job | **Not** required for Validated — AC6 design-only (`D-S059-882=3a`) |

**Still open (compose, not Validated blockers):** [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859)
URI drift; [#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882) notification pipeline;
exhaustive 402 weather / residual register depth under #959/#889 **defer+cite**.

**Issue comments:** criteria above posted on #889 and #959 at T4.2.
**Close:** #959 closed on merge; #889 was already CLOSED (Validated-only) — residuals stay
defer+cite in `fixture-coverage-delta-t2.4.md` / this section (no reopen).

### Close (2026-08-09)

| ID | Decision |
|----|----------|
| D-S059-merge | **1** — Merge [#964](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/964) → `stage` @ `2815ffbe` |
| D-S059-close | **1** — Close EV-050 / S059; clear `active_session` |

Summary: `docs/sessions/S059-codes-wmo-validated/reports/evolve-summary.md` ·
report: `docs/evolve-report-EV-050.md`.

### Scope (Phase 0–1 — locked 2026-08-09; profile amend 2026-08-09)

| ID | Decision |
|----|----------|
| D-S058-park | **1a** — Park S058 / #958; keep handwritten AMS constraint |
| D-S059-ticket | **2a** — Open S059 / EV-050 for #959 |
| D-S059-route | **1** — Standard: `00→16→01→02→04→05→07→08→09→11`; skip `03,06,10,12,13` |
| D-S059-families | **1a** — v1 membership: weather (306/4678 + present/forecast) + recent + cloud amount/type + SIGMET/AIRMET phenomena + nilReason URI checks where lint already touches them |
| D-S059-fixtures | **2c** — **Aggressive** fixture expansion this cycle: `RE*`, AIRMET `_` phenomena, SpaceWxPhenomena, TCU (plus packs needed for membership happy/sad) |
| D-S059-882 | **3a** — Design-only compose note with #882; no scheduled live refresh job this cycle |
| D-S059-01-ac | **4a** — Lock AC1–AC6 as drafted (with 1a/2c/3a amendments) |
| D-S059-profiles | **1b** — Expand: compare **`annex3` vs `iwxxm_us`** across **all F6 products** (`iwxxm_us` **N/A** where no US profile); fix **true errors** (AC7–AC8) |
| D-S059-gateA | **1** — Gate A **PASS**; handoff **04-tech-plan** (advisories M1–M3 accepted: AC8 defer+cite OK; N/A ≠ fail; 04 may split milestones) |
| D-S059-04-milestones | **1** — Four milestones: M1 harvest · M2 membership+fixtures · M3 profiles · M4 closeout docs |
| D-S059-04-harvest | **1** — L3 SoT = vendor CSV `notation`; pin RDF for nil / dual paths |
| D-S059-04-wire | **1** — Generated membership under `packages/tac-validate` data + pytest + `make` regen |
| D-S059-04-adr | **1** — No new ADR; path/cadence in tech-spec / domain + execution plan |
| D-S059-04-plan | **1** — Approve execution plan + Build Plan Card → **05-verify-tech** |
| D-S059-gateB | **1** — Gate B **PASS**; handoff **07-build** M1 / T1.1 (L1–L3 advisory accepted) |
| D-S059-validated | **1** — #889 Validated **satisfied** (AC5); supersedes Lean `D-S055-validated=1` for this triad element |
| D-S059-11-next | **1** — Approve AC1–AC8; push branch + open PR → `stage` (12/13 stay skipped) |
| D-S059-merge | **1** — Merge #964 → `stage` @ `2815ffbe`; close #959 |
| D-S059-close | **1** — Close EV-050 / S059; `active_session` cleared |

### Gate A (02) — PASS 2026-08-09

Report: `docs/sessions/S059-codes-wmo-validated/reports/02-verify-plan.md`. Corpus cites for scope: [Corpus: product] [Corpus: tests] [Corpus: tech-spec] [Corpus: decisions].

### 04-tech-plan — APPROVED 2026-08-09 (`D-S059-04-plan=1`)

Artifacts: `reports/execution-plan.md`, `build-plan-card.md` (M1 = T1.1–T1.4), `reports/04-tech-plan.md`.

### Gate B (05) — PASS 2026-08-09 (`D-S059-gateB=1`)

Report: `reports/05-verify-tech.md`. Advisories L1–L3 accepted. Next: **07-build** M1.

### Acceptance (Standard — AC1–AC8 confirmed `D-S059-01-ac=4a` + `D-S059-profiles=1b`)

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | **Offline harvest:** Standing harvest from `vendor/schemas/iwxxm-codelists` (+ pin RDF under `vendor/schemas/iwxxm/…/rule/`) produces machine-readable membership set(s) consumed by CI / `tac-validate` — **no live HTML in PR CI** | TC-EV050-001 |
| AC2 | **Membership Validated:** Happy + unknown/sad asserts for v1 families (`D-S059-families=1a`): present/forecast weather, recent weather, cloud amount/type, SIGMET + AIRMET phenomena, nilReason where lint already emits/checks URIs | TC-EV050-002 |
| AC3 | **Cadence:** Harvest refresh documented vs `vendor/manifest.json` `iwxxm-codelists` pin; refresh with normal vendor sync PRs | TC-EV050-003 |
| AC4 | **Gaps / fixtures:** Aggressive fixture expansion (`D-S059-fixtures=2c`) closes EV-046 gap rows for RE*, AIRMET underscore matching, SpaceWxPhenomena, TCU; remaining gaps → child issues or explicit deferrals with cite | TC-EV050-004 |
| AC5 | **#889 Validated:** Parent Validated triad element satisfied (or explicit re-scope recorded here + on #889/#959) | TC-EV050-005 |
| AC6 | **#882 compose (design-only):** Short design note for optional scheduled live refresh **outside** PR CI composing with #882 notify — **no** full notification pipeline; **no** job implementation this cycle (`D-S059-882=3a`) | TC-EV050-006 |
| AC7 | **Profile compare:** Document + CI-checkable delta of membership / lint outcomes for the same TAC under **`profile=annex3` vs `profile=iwxxm_us`** for **all supported F6 products**. Where `iwxxm_us` is not defined for a product, record **N/A** (not a fail). Where both apply (typically METAR/SPECI/TAF + shared WMO L3), classify each delta: **shared WMO expected** · **intentional US overlay (L5 REMARKS / FMH-1)** · **suspect / true error**. WMO harvest remains SoT for L3; US SoT for L5 only | TC-EV050-007 |
| AC8 | **True-error fixes:** For deltas classified **true error** (wrong severity, false fail/pass, missing membership, incorrect profile gating), fix in this cycle with regression tests; intentional diffs and N/A rows get a cited disposition (no silent ignore). Do **not** invent US weather vocab outside FMH-1 / documented NWS / iwxxm-us pins | TC-EV050-008 |

### Out of scope

- Hand-edit `vendor/schemas/*`
- Live `codes.wmo.int` HTML in PR CI
- Replacing XSD/Schematron (`iwxxm-validate`)
- Full #882 notification pipeline / scheduled live job implementation
- `#958` AMS abstract (parked S058)
- Promote `stage`→`main` unless separately approved
- Exhaustive 402 weather combinations (representative + aggressive gap packs only)
- Colour / MetFeature / VONA encode duals beyond nil/phenomena already in v1 families (defer unless needed for sad packs)
- Country / regional scorecards beyond the two product profiles (`annex3` / `iwxxm_us`)
- Inventing national weather tokens not grounded in FMH-1 / NWS / iwxxm-us docs

### Preset

**Standard** — `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 11`.  
Skip `03`, `06`, `10`, `12`, `13`.

### Gate A (02)

Pass when AC1–AC6 + TC-EV050-* + feature-list deepen + this section are consistent — then 04.

---

## Cycle EV-048 — Strip internal doc refs from UI + public API (#951) (S057)

**Session**: S057-strip-internal-doc-refs  
**Features**: deepen **F7 / F21** (no new Fn)  
**Started**: 2026-08-08  
**Branch**: `evolve/EV-048-strip-internal-doc-refs` (base `stage@d7652d5d`)  
**Status**: **completed** 2026-08-09 (`D-S057-close=1`; PR #963 → `stage` @ `06a9543f`)  

**Issues**: [#951](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/951) (closed)  
**Corpus**: [Corpus: product §F7], [Corpus: product §F21], [Corpus: api],
[Corpus: journeys], [Corpus: tests], [Corpus: decisions]

### Scope (Phase 0 — locked 2026-08-08)

| ID | Decision |
|----|----------|
| D-S057-open | **1** — Open S057 → EV-048 for #951 |
| D-S057-scope | **1** — Full #951: UI + OpenAPI + client errors + automated guard |
| D-S057-preset | **1** — Standard (amended from initial Lean) |
| D-S057-preset-reconfirm | **1** — `00→16→01→02→04→05→07→08→09→10→11`; skip 03/06/12/13 |
| D-S057-ui-preview | **1** — Non-deployed local UI at http://localhost:5173/ |
| D-S057-01-ac | **1** — Approve AC1–AC6 + UJ-055 as drafted |
| D-S057-guard-s0 | **1** — Include `\bS0\d+\b` in guard patterns |
| D-S057-gateA | **1** — Gate A PASS; S2.1–S2.4 as 04/07 defaults |
| D-S057-04-plan | **1** — Approve M1–M3 / T1.1–T3.3 as drafted; proceed 05 then 07 |
| D-S057-04-guard-ext | **1** — Extend guard with `\bTC-[A-Z0-9-]+\b`, `\bE\d{2}-\d+\b`, `\b#\d{3,}\b` on scanned surfaces |
| D-S057-gateB | **1** — Gate B PASS; S5.M1–S5.M3 defaults; proceed 07-build M1 |
| D-S057-phaseC | **1** — Continue 09-qa + 10-e2e (delta/light) → 11-verify-impl |
| D-S057-ui-preview-verify | **2** — No non-deployed UI preview before Verify (FE catalogs clean) |
| D-S057-uj055 | **1** — Approve UJ-055 |
| D-S057-f7 | **1** — Approve F7 deepen (copy hygiene) |
| D-S057-f21 | **1** — Approve F21 deepen (OpenAPI/errors) |
| D-S057-qa003 | **2** — Expand guard with `\bF\d+\b`; strip Fn IDs from privacy + OpenAPI |
| D-S057-11-next | **1** — Push branch + open PR to `stage` (12/13 stay skipped) |
| D-S057-merge | **1** — Merge PR #963 → `stage` @ `06a9543f` |
| D-S057-close | **1** — Close EV-048 / S057; clear `active_session` |

### Acceptance (confirmed `D-S057-01-ac=1`)

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | Audit findings listed in PR | TC-EV048-001 |
| AC2 | OpenAPI descriptions pass guard | TC-EV048-002 |
| AC3 | Operator UI string catalogs pass guard | TC-EV048-003 |
| AC4 | Client-facing API errors pass guard | TC-EV048-004 |
| AC5 | Automated guard fails on synthetic regression | TC-EV048-005 |
| AC6 | Soft-preview etc. operator-friendly; tests updated | TC-EV048-002/003 |

---

## Cycle EV-047 — M0 stabilize + operator trust (#833/#834/#956/#957) (S056)

**Session**: S056-m0-stabilize-operator-trust  
**Features**: deepen **M5 / F6 / F7** (no new Fn)  
**Started**: 2026-08-08  
**Branch**: `evolve/EV-047-m0-stabilize-operator-trust` (base `stage@adcf3b1f`)  
**Status**: **completed** 2026-08-08 (`D-S056-close=1`; PR #961 → `stage`)  

**Issues**: [#833](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/833),
[#834](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/834),
[#956](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/956),
[#957](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/957)  
**Corpus**: [Corpus: product §M5], [Corpus: product §F6], [Corpus: product §F7],
[Corpus: tests], [Corpus: tech-spec], [Corpus: decisions] · ops
`docs/ops/DEVELOPMENT.md`

### Scope (Phase 0 — locked 2026-08-08)

| ID | Decision |
|----|----------|
| D-S056-open | **1** — Open S056 → EV-047 for #833+#834+#956+#957 |
| D-S056-bundle | **1** — One cycle, all four issues |
| D-S056-husky | **1** — Husky day-to-day = lint + fast units; heavier gates CI / opt-in `make` (**explicit reverse** of EV-036/S044 local-heavy developer path) |
| D-S056-preset | **1** — Standard; amended by D-S056-docs for Help → **re-enable 10-e2e**; 12/13 stay waived unless deploy gate needed at 11 |
| D-S056-husky-shape | **1 (A)** — `pre-commit` = lint/format only; `pre-push` = fast unit subset |
| D-S056-perf | **1** — convert-only wall **p95** vs committed YAML; hard-fail **>20% or absolute ceiling**; METAR/SPECI/TAF + thin SIGMET-family smoke; **CI required check only** (not husky); pure-Python first; median-of-N + flake retry doc |
| D-S056-docs | **1** — one-pager `docs/guides/operator-one-pager.md` (+ printable if cheap); handbook `docs/guides/operator-handbook.md`; README Quick start **and** in-app Help (F7); no new CORPUS root member |
| D-S056-phase0 | **1** — Phase 0 locked; proceed **01-requirements** |
| D-S056-01-ac | **1** — Approve AC1–AC9 as written (2026-08-08) |
| D-S056-ui-preview | **2** — No non-deployed UI preview for 01; Help placement in 04 |
| D-S056-gateA | **2** — Gate A PASS; **require ruleset update for converter perf check** (amended by defer) |
| D-S056-ruleset-defer | **2** — Defer **requiring** `Converter perf (tac2iwxxm)` in live rulesets until CI job ships (M1 T1.4→T1.5); keep other checks; establish **baselines first** for comparison |
| D-S056-04-plan | **2** — Approve execution plan; **seed** `converter_pr.yaml` from laptop spike now; **re-record on CI** in T1.3 |
| D-S056-04-floor | **200µs** absolute floor (amended from 50µs after cross-host noise on T1.3 Linux Docker re-record) |
| D-S056-cov95 | **2** — package + per-file ≥95% this cycle (all Python packages in CI); M2.5 T2.5.1–T2.5.3 |
| D-S056-cov95-scope | **2** — literally every Python package including auth + worker; package + per-file ≥95%; M2.5 adds T2.5.4 |
| D-S056-m3-order | **2** — resolve coverage first (M2.5), then M3 docs/Help (amends sequencing after `D-S056-next-m3=1`) |
| D-S056-m4-next | **1** — M4 verify 08 → 09+10 → 11 |
| D-S056-11-ui-preview | **2** — No non-deployed preview at 11; approve from reports/tests only |
| D-S056-uj054 | **1** — Approve UJ-054 Operator Help → one-pager |
| D-S056-ac-bundle | **1** — Approve AC1–AC9 + cov95; accept T1.5 ruleset defer |
| D-S056-advisories | **1** — Accept QA-001..006 as listed in verify-impl.md |
| D-S056-close | **1** — Close EV-047; merge #961 → `stage` (12/13 waived; T1.5 deferred) |

### Locked defaults (perf / hooks / docs)

| Area | Default |
|------|---------|
| Husky | Shape **A** (`D-S056-husky-shape=1`) |
| Perf metric | convert-only p95; CI-only gate; 20% / ceiling; Annex-3 thin smoke |
| Docs | `docs/guides/operator-*.md` + README + Help |

### Acceptance (confirmed `D-S056-01-ac=1`)

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | Commit = lint/format only | TC-EV047-001 |
| AC2 | Push = fast unit subset only | TC-EV047-002 |
| AC3 | DEVELOPMENT.md + test-plan match shape A | TC-EV047-003 |
| AC4 | Offloaded gates still in CI | TC-EV047-004 |
| AC5 | Artificial convert slowdown → red; revert → green | TC-EV047-005/006 |
| AC6 | Required CI check; baselines + flake policy; p95 / 20% pack | TC-EV047-007/008 |
| AC7 | Operator one-pager (one page; no internal cites) | TC-EV047-009 |
| AC8 | Minimal handbook (sections + ingest pointer) | TC-EV047-010 |
| AC9 | README + in-app Help → one-pager (UJ-054) | TC-EV047-011 |

---

## Cycle EV-046 — codes.wmo.int aviation registers → TAC present/cite/cover (S055)

**Session**: S055-wmo-aviation-registers  
**Features**: deepen **F6 / F12 / F15 / F20 / F23 / F24 / F26 / F27 / F28 / F32**  
**Started**: 2026-08-08  
**Branch**: `evolve/EV-046-wmo-aviation-registers`  
**Status**: **completed** 2026-08-08 (`D-S055-close=1`; PR → `stage`)  
**Issues**: [#889](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/889)
(parent epic [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846);
compose [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859),
[#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882);
Validated follow-on [#959](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/959))  
**Corpus**: [Corpus: product §F6/F12/F15/F20/F23/F24/F26/F27/F28/F32],
[Corpus: tests], [Corpus: decisions] · domain opt-in
`docs/domain/rules/*`, `docs/domain/mining/*`

### Scope (Phase 0 — locked 2026-08-08)

| ID | Decision |
|----|----------|
| D-S055-open | **2** — Lean preset (docs/coverage first; defer full harvest wiring) |
| D-S055-families | **3** — Full priority-register coverage % across **all supported F6 products** (METAR, SPECI, TAF, SIGMET/VA, AIRMET, VAA, TCA, SWXA, VONA) |
| D-S055-validated | **1** — **Waive Validated** for Lean close; document gap + Standard follow-on child |
| D-S055-cite | **2** — Domain docs + COVERAGE_MATRIX + RULE_SOURCE_URLS + mining notes **and** ISSUE_CATALOG / rule provenance where notations already exist |
| D-S055-phase01 | **1** — Lock scope; proceed 01-requirements |
| D-park-doks | EV-043 / EV-044 remain **PARKED** |

### Acceptance (Lean — confirmed `D-S055-01-ac=1` 2026-08-08)

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | **Present:** Priority-register inventory (49-2, 306/4678, iwxxm, common/nil) lists members we depend on vs vendor SoT; dual/404/obsolete dispositions documented | TC-EV046-001 |
| AC2 | **Cited:** RULE_SOURCE_URLS + mining notes + COVERAGE_MATRIX rows updated; ISSUE_CATALOG / PROVENANCE_MAP entries that already claim codes.wmo.int use **stable concept URIs** (not bare register root only) where a concept URI exists | TC-EV046-002 |
| AC3 | **Cover:** Coverage report — % of priority-register members exercised by TAC fixtures **per F6 product family**; intentional exclusions with cite + reason | TC-EV046-003 |
| AC4 | **Gap report:** Registry notations with no fixture / lint / encode / citation → child issues or explicit deferrals on #846 / #889 | TC-EV046-004 |
| AC5 | **Validated (waived):** Lean close documents waiver + files Standard follow-on for harvest + automated TAC-token membership checks (no live HTML in PR CI) | TC-EV046-005 |
| AC6 | Harvest SoT path documented (vendor RDF/CSV + `vendor/manifest.json` pin/cadence); cross-links to #859 / #882 current | TC-EV046-006 |

### Out of scope (Lean)

- Standing machine harvest job + `tac-validate` membership CI (Standard follow-on)
- Live `codes.wmo.int` HTML in PR CI; vendor hand-edits; #882 notify pipeline
- Replacing XSD/Schematron; dumping non-aviation trees

### Preset

**Lean** — `00 → 16 → 01 → 02`; skip `03`–`13`.

### Gate A (02)

Pass when Lean ACs + test-plan TC-EV046-* + this section committed — then Lean close (no 04/07).

---

## Cycle EV-045 — Rust crate CI (#725) (S054)

**Session**: S054-rust-ci-crates  
**Features**: deepen **F13**, **F14**  
**Started**: 2026-08-08  
**Branch**: `evolve/EV-045-rust-ci`  
**Status**: **completed** 2026-08-08  
**Issues**: [#725](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/725)  
**PR**: [#953](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/953) → `stage` (open at close)  
**Corpus**: [Corpus: product §F13], [Corpus: product §F14], [Corpus: tech-spec],
[Corpus: tests], [Corpus: adr/ADR-017]


### Scope (Phase 0 — locked 2026-08-08)

| ID | Decision |
|----|----------|
| D-park-doks | Park EV-043 + EV-044; repair mashed `active_session`; clear for #725 |
| D-S054-open | Open S054 / EV-045; Standard with skips 03/06/10/12/13; deepen F13+F14 |
| D-S054-01-ac | **1** — confirm ACs + defaults (extend `ci-cd.yml`, clippy `-D warnings`, `make rust-check`) → 02-verify-plan |
| D-S054-gateA | **2** — PASS Gate A but **ruleset update before 04**; check names locked in test-plan + `apply_gh_branch_rulesets.sh` |
| D-S054-ac6-waive | **2** — Waive AC6 **ops** half (live GH rulesets/required checks); keep docs + `apply_gh_branch_rulesets.sh`; proceed **04**; apply later when admin available |
| D-S054-04-jobs | **2** — cargo via crate **matrix** + thin gate job `name: Rust crates (fmt/clippy/test)` (avoids GH matrix name suffix breaking required checks) |
| D-S054-04-maturin | **2** — extend `tac2iwxxm-native` → two-package matrix; `name: ${{ matrix.check_name }}` for locked maturin contexts |
| D-S054-04-trigger | **1** — run with default `ci-cd.yml` PR/push (not path-filter-only) |
| D-S054-04-local | **2** — `deploy.needs` includes rust gate + native matrix; `make rust-check` = cargo both crates **+** both maturin smokes |
| D-S054-04-plan | **1** — Approve execution plan + Build Plan Card as written → 05-verify-tech |
| D-S054-gateB | **1** — PASS Gate B; confirm syncs; proceed 07-build (06 skipped) |
| D-S054-t17-ci | **1** — Accept Actions run 31273500621 as tip CI for EV-045 jobs (docs-only tip after) |
| D-S054-phaseC | **1** — Approve Phase C; start 09-qa |
| D-S054-11 | **1** — Approve F13+F14 deepen + accept QA-001..005; close cycle (12/13 skipped) |

**Goal**: Required CI + Makefile parity for `packages/tac2iwxxm/rust` and
`packages/iwxxm-validate/rust` (`fmt`, `clippy -D warnings`, `cargo test`, maturin/PyO3
smoke for both).

**Out of scope**: Rust HTTP service; multi-arch wheel CI beyond `pypi-publish`; Schematron
perf gates; browser E2E; staging/prod deploy.

### Preset

**Standard** — skip 03/06/10/12/13 (tooling/deps/UI/deploy not in scope).

### Acceptance (F13/F14 deepen — TC-EV045-001..007) — confirmed D-S054-01-ac=1

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | `cargo fmt --check` fails on unformatted Rust (both crates) | TC-EV045-001 |
| AC2 | `clippy -- -D warnings` fails on warnings | TC-EV045-002 |
| AC3 | `cargo test` green for both crates | TC-EV045-003 |
| AC4 | Maturin/PyO3 smoke for **both** packages | TC-EV045-004 |
| AC5 | `make rust-check` mirrors CI (cargo both + both maturin smokes) | TC-EV045-005 |
| AC6 | Required check name(s) documented; merge blocked when red | TC-EV045-006 |
| AC7 | Jobs on default `ci-cd.yml` PR/push (not path-filter-only) | TC-EV045-007 |

**AC6 split (D-S054-ac6-waive=2):** docs half **in scope** (locked contexts in
`docs/test-plan.md` + script). Ops half (repo rulesets actually requiring those
contexts) **waived until admin** runs `bash scripts/deploy/apply_gh_branch_rulesets.sh`.
Same class as EV-043 admin gap. [Corpus: tests] [Corpus: decisions]

### Implementation defaults (confirmed D-S054-01-ac=1)

| Topic | Default |
|-------|---------|
| Workflow | Extend `.github/workflows/ci-cd.yml` (matrix); not a new workflow unless latency forces |
| Clippy | Hard `-D warnings` |
| Local | `make rust-check` mirrors CI |
| Cache | `Swatinem/rust-cache` (or equivalent) |
| Toolchain | `dtolnay/rust-toolchain@stable` + rustfmt,clippy |

**Closed**: 2026-08-08 — `D-S054-11=1`; reports `evolve-summary.md` + `docs/evolve-report-EV-045.md`.  
PR #953 open → `stage` (merge separate). AC6 ops still deferred.

### Corpus cites / waivers

- [Corpus: product §F13] [Corpus: product §F14]
- [Corpus: tech-spec] [Corpus: tests] [Corpus: journeys] [Corpus: adr/ADR-017]
- `[Corpus: WAIVED — AC6 GitHub rulesets/required-checks apply; reason: token admin=false / no rulesets; decided: D-S054-ac6-waive=2 / EV-045]`

---

---

## Cycle EV-044 — Separate staging DOKS + DO Project (S053)

**Session**: S053-separate-staging-doks-project  
**Features**: deepen **F30**  
**Started**: 2026-08-08  
**Branch**: `evolve/EV-044-separate-staging-doks`  
**Status**: in_progress  
**Amends**: [ADR-034](../adr/ADR-034-doks-staging-promote-from-stage.md) (shared cluster → dual cluster)  
**Corpus**: [Corpus: product §F30], [Corpus: deploy], [Corpus: tech-spec],
[Corpus: tests], [Corpus: adr/ADR-033], [Corpus: adr/ADR-034]


### Scope (Phase 0 — locked 2026-08-08)

| ID | Decision |
|----|----------|
| D-S053-open | Open S053 / EV-044; Standard routing (`1:1`) |
| D-S053-scope | Separate staging DOKS under **Staging TAC-to-IWXXM**; prod on **TAC-to-IWXXM** |
| D-S053-db | New cheapest managed PG (`db-s-1vcpu-1gb`) under Staging project (`2:1`) |
| D-S053-size | Staging DOKS 1× `s-2vcpu-4gb`, `nyc1`, name `metar-iwxxm-staging` (`3:1`) |
| D-S053-teardown | Tear down shared-cluster ns `metar-iwxxm-staging` after new stack green (`4:1`) |
| D-S053-cd | Keep promote-from-stage: `stage`→staging cluster, `main`→prod cluster |
| D-S053-dns | Staging hosts → **new** staging LB IP (Porkbun A update) |

### Acceptance (F30 deepen — amend TC-F30-008..010)

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | Staging DOKS + PG assigned to DO Project **Staging TAC-to-IWXXM** | TC-F30-008′ |
| AC2 | Prod DOKS + PG remain on **TAC-to-IWXXM** | TC-F30-008′ |
| AC3 | Staging DNS + TLS for api/app.staging → staging LB | TC-F30-009 |
| AC4 | `stage` CD targets staging cluster; `main` CD targets prod | TC-F30-010 |
| AC5 | Shared-cluster staging ns removed after cutover | TC-F30-013 (new) |
| AC6 | Promote gate unchanged (head=`stage` + Staging smoke) | TC-F30-012 |

### Preset

**Standard** — include 03 for dual-cluster / project tooling; skip 06.

### Gate A (02)

**PASS** 2026-08-08 — F30 deepen AC + ADR-034 amend + this section committed; proceed 03/04.

### Gate B (05)

Pass when execution-plan tasks T2–T4 approved — proceed 07-build provision.

---

## Cycle EV-043 — DOKS staging + prod protected-branch CI/CD (S052)

**Session**: S052-doks-staging-prod-branch-deploys  
**Features**: deepen **F30**  
**Started**: 2026-08-08  
**Branch**: `evolve/EV-043-doks-staging-prod`  
**Status**: in_progress  
**Issues**: [#886](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/886)  
**Corpus**: [Corpus: product §F30], [Corpus: deploy], [Corpus: tech-spec],
[Corpus: tests], [Corpus: adr/ADR-033], [Corpus: adr/ADR-034]

### Scope (Phase 0 — locked 2026-08-08)

| ID | Decision |
|----|----------|
| D-S052-open | Open S052 / EV-043 for #886 |
| D-S052-scope | Add DOKS **staging** + keep prod |
| D-S052-product | **DOKS** (same cluster `metar-iwxxm`) |
| D-S052-gh | Create/protect `stage` + `main`; GH Envs `staging` / `production` |
| D-S052-cd | Auto CI/CD both: `stage`→staging, `main`→prod |
| D-S052-manual | Solo-dev: **PR is the manual gate** (no required reviewers) |
| D-S052-promote | PRs to `main` must be from `stage` + **staging-gate** (Staging smoke green) |
| D-S052-dns | `api.staging.tac-to-iwxxm.com` / `app.staging.tac-to-iwxxm.com` → LB `168.144.12.70` |

### Acceptance (F30 deepen — TC-F30-008..012)

| AC | Criterion | TC |
|----|-----------|-----|
| AC1 | Staging ns `metar-iwxxm-staging` + secrets isolated from prod | TC-F30-008 |
| AC2 | Staging DNS + TLS for api/app.staging hosts | TC-F30-009 |
| AC3 | Push/merge to `stage` deploys staging; to `main` deploys prod | TC-F30-010 |
| AC4 | `stage`/`main` require PR; no force-push (rulesets) | TC-F30-011 |
| AC5 | PR to `main` fails unless head=`stage` and Staging smoke green | TC-F30-012 |

### Preset

**Standard** — include 03 for promote/env_role rule; skip 06.

### Gate A (02)

Pass when F30 deepen AC + test-plan smokes + this section committed — proceed 03/04.

---

## Cycle EV-042 — Remove dissemination destinations + operator throughput + mass ingest (S050)

**Session**: S050-remove-db-tools-operator-throughput  
**Features**: deepen **F7 / F16–F19**; new **F33**  
**Started**: 2026-08-07  
**Branch**: `evolve/EV-042-remove-db-tools-operator-throughput`  
**Status**: in_progress — 01-requirements  
**Issues**: [#897](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/897) epic;
[#898](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/898) follow-up (restore all destinations)  
**Prior**: S049 / EV-041 completed (PR #895 merged @ `fa5b2140`)  
**Corpus**: [Corpus: product §F7], [Corpus: product §F16], [Corpus: product §F33],
[Corpus: product §F17–F19], [Corpus: system-spec], [Corpus: api], [Corpus: tests],
[Corpus: adr/ADR-021], [Corpus: adr/ADR-029], [Corpus: adr/ADR-030]

### Scope (Phase 0 — locked 2026-08-07; **R2 amend**)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| Q1 | decision | Clear EV-041? | **Merge #895 then close** (user option 2) |
| Q2 | ambiguity | What to remove from UI? | **R2 amend**: hide **all** Dissemination destinations (DB + WIS2/EDIS/AMHS/SWIM/AFS); leave `DatabaseUploadDialog`; APIs retained for harness |
| Q2b | decision | 11-verify-impl flag | **Also hide Upload to Database / DatabaseUploadDialog** (user 2026-08-07); restore with #898 |
| Q3 | decision | Cycle ship bar? | Remove destinations UI + churn UX + secure mass file/folder ingest (F33) |
| Q4 | decision | Churn UX? | **Queue+keyboard and batch convert/validate** (disseminate batch **N/A** while destinations hidden) |
| Q5 | decision | Mass ingest shape? | **Multi-file + folder** (`webkitdirectory` / zip) with progress + per-file errors |
| Q6 | decision | Mass ingest security? | Auth-gated + size/count/MIME caps + reject binaries/executables + **content sniff / zip-bomb guards** |
| Q7 | ambiguity | Backend sinks? | **UI hide only** — backend still accepts sink types for tests/harness |
| Q8 | decision | Preset? | **Standard** |
| Q9 | decision | Improvements pack? | Keyboard shortcuts + mass progress toast; keep export multi-select for convert outputs; **no** default-sink polish |
| Q10 | decision | UI preview? | **Yes** — local `http://localhost:18000` |

### 01-requirements intake (locked 2026-08-07)

| ID | Topic | Decision |
|----|-------|----------|
| R1 | Mass-ingest caps | **≤200 files / request, ≤5 MiB each, ≤50 MiB total unzipped** |
| R2 | Dissemination UI | **Hide all sinks** (DB + F17–F19); drawer/send destinations gone |
| R3 | Who can mass-ingest | **Auth** for folder/zip + mass path; guests keep existing small multi-file |
| R4 | Batch disseminate | **N/A** this cycle (no operator destinations) |

### Preset

**Standard** — `00→16→01→02→04→05→07→08→09→10→11→12→13` (skip 03/06 unless needed)

### Improvements pack (in scope)

- Keyboard shortcuts for convert / validate
- Progress toast for mass jobs
- Keep export multi-select for convert outputs (no sink send)
- ~~Default drawer sink~~ — **removed** (no destinations)

### Proceed gate (Phase 0→1 — locked 2026-08-07)

| ID | Decision |
|----|----------|
| D-S050-proceed | **Allocate F16 deepen + F7 deepen + new F33**; F17–F19 UI-hide via R2 amend |

### Fn allocation

| Fn | Role | Status |
|----|------|--------|
| F16–F19 deepen | UI-hide all drawer sinks; API retained | deepen |
| F7 deepen | Queue+keyboard + batch convert/validate + improvements | deepen |
| **F33** | Secure mass file/folder ingest | **Planned** |

### Impacted docs / packages

| Artifact | Delta |
|----------|-------|
| [Corpus: product] | F33 ACs; F7/F16–F19 deepen notes |
| [Corpus: journeys] | UJ-051..053 |
| [Corpus: system-spec] | Destinations UI policy; mass ingest |
| [Corpus: api] | Mass upload caps + auth |
| [Corpus: tests] | TC-F33-*; TC-EV042-*; H4–H5 |
| [Corpus: tech-spec] | Upload limit env/config |
| `apps/frontend` | Hide Convert&Send / drawer destinations; churn; F33 UI |
| `apps/backend` | Sniff/zip-bomb; auth on mass path |
| `packages/dissemination` | Keep adapters |

### Acceptance (locked — **D-S050-ac** = user option 1, 2026-08-07)

| AC | Criterion |
|----|-----------|
| AC1 | Operator UI has **no** Dissemination sink chooser / Convert&Send destination path (F16–F19 UI hidden) |
| AC2 | Backend dissemination preflight/send still works in harness/tests (UI-hide only) |
| AC3 | Result queue + keyboard next/prev + Enter convert/validate; multi-select batch convert/validate |
| AC4 | F33: auth required for folder/zip mass ingest; caps **200 / 5 MiB / 50 MiB**; sniff + zip-bomb reject; progress + per-file errors |
| AC5 | Guests retain existing small multi-file upload (if already allowed); mass path returns clear 401/403 without JWT |
| AC6 | UJ-051..053 + TC-F33-001..006 + H4–H5 mapped in test-plan |
| AC7 | #898 tracks restore of **all** destinations (not DB-only) |

### Gate A (02) — PASS 2026-08-07

| ID | Decision |
|----|----------|
| D-S050-C1 | Dedicated mass-route body limit; keep global `MAX_REQUEST_BODY_BYTES` = 2 MiB |
| D-S050-gate-a | Gate A PASS → 04-tech-plan |

### Tech plan (04) — approved 2026-08-07

| ID | Decision |
|----|----------|
| D-S050-04-tech | Accept defaults: server zip unpack; client folder expand; F31 JWT; no new ADR; mass rate limit 10/min; stdlib zipfile |
| D-S050-04-plan | Execution plan M1–M4 approved → Gate B → 07-build |

### Gate B (05) — PASS 2026-08-07

| ID | Decision |
|----|----------|
| D-S050-gate-b | Gate B PASS → 07-build M1 |

---

## Cycle EV-041 — Operator UI runbook + source-centric PPT pack (S049)

**Session**: S049-operator-sources-briefing  
**Features**: deepen **F7** narrative (no new Fn)  
**Started**: 2026-08-06  
**Branch**: `evolve/EV-041-operator-sources-briefing`  
**Status**: **completed** — PR [#895](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/895) merged @ `fa5b2140`  
**Prior**: S048 / EV-040 completed  
**Corpus**: [Corpus: product §F7], [Corpus: system-spec], [Corpus: tech-spec];
path-cites [docs/domain/README.md], [docs/domain/rules/RULE_SOURCE_URLS.md],
[docs/domain/rules/ACCESS_AND_CITATION.md], [docs/domain/rules/PROVENANCE_MAP.md],
[docs/domain/mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md];
[Corpus: WAIVED — ops/guides CORPUS membership; reason: path-cite only (EV-035 G3 pattern); decided: EV-041]

### Scope (Phase 0 — locked 2026-08-06; plan `operator_sources_docs` → **D-S049-open**)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| Q1 | decision | Deliverables? | Docs-only runbook + PPT **source pack** + guided `.pptx` walkthrough (no binary in git) |
| Q2 | decision | Audience? | **Split** — runbook = operators; PPT = external sources/architecture briefing |
| Q3 | decision | CORPUS? | Path-cite domain/ops/guides — **no** minimal-corpus membership |
| Q4 | decision | UI preview? | **N/A** — docs-only (optional local screenshots for personal deck only) |

### Preset

**Lean (docs override)** — `00→16→01→02→07→08` (skip 03–06, 09–13)

### Acceptance (locked — **D-S049-ac**)

| AC | Criterion |
|----|-----------|
| AC1 | Runbook covers operator workflow **and** maps each major surface to standards/vendor/package sources |
| AC2 | PPT pack has complete slide outline + bibliography + image pointers + build walkthrough |
| AC3 | All citations follow ACCESS_AND_CITATION (paywall labeled; no copyrighted full text) |
| AC4 | Walkthrough can produce a briefing deck without inventing new normative claims |
| AC5 | Session artifacts + branch recorded; PR when requested |

### In / out

- **In**: `docs/ops/operator-ui-runbook.md`; `docs/guides/operator-sources-pptx/*`; this section; domain README pointer
- **Out**: product code; `.pptx`/PDFs/PNGs in git; provenance catalog rewrite; deploy

## Cycle EV-040 — Workbench lint UX + examples + prefs (S048)

**Session**: S048-workbench-lint-ux  
**Features**: deepen **F7 / F10 / F15** (no new Fn)  
**Started**: 2026-08-06  
**Completed**: 2026-08-06  
**Branch**: `evolve/EV-040-workbench-lint-ux`  
**Status**: completed  
**PR**: [#893](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/893) **merged** @ `4be24994`  
**Issues**: [#894](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/894) closed under [#840](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/840)  
**Close**: **D-S048-close=1,1,1** — Merge #893; file+close #894 under #840; stop  
**Prior**: S047 / EV-039 completed  
**Corpus**: [Corpus: product §F7/F10/F15], [Corpus: api], [Corpus: tests], [Corpus: journeys], [Corpus: adr/ADR-028]

### Scope (Phase 0 — locked 2026-08-06; plan approve + chat → **D-S048-open**)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| Q1 | decision | Session? | Open **S048** → **EV-040** (feature / Standard) |
| Q2 | decision | Example lint fails? | **False positives** — note + fix (RVR tendency; AHL YYGGgg) |
| Q3 | decision | Prefs + examples? | Prefs → name + extension; official AHL + Collect; F22 untouched |
| Q4 | decision | UI preview? | **Yes** — non-deployed local |

### False-positive notes

| Fixture | Code | Verdict | Disposition |
|---------|------|---------|-------------|
| WMO A3-1 `R12/1000U` | `INVALID_RVR` | FP | Extend `_RVR_OK` for tendency U\|D\|N |
| AHL `SAUS31 KZNY 121200` | `INVALID_VISIBILITY` | FP | Skip AHL heading before vis scans |

### Preset

**Standard** — `00→16→01→02→04→05→07→08→09→10→11→12→13` (skip 03, 06)

### Acceptance (locked from approved plan — **D-S048-ac**)

| AC | Criterion |
|----|-----------|
| AC1 | Lint console emits one line per issue (no `+N more` truncation) |
| AC2 | Convert / Convert&Send does not clear manual TAC input |
| AC3 | New TAC label; action strip below header, above selects, above bench |
| AC4 | UserPreferences slimmed to output name + extension (F22 Privacy unchanged) |
| AC5 | Examples include official-provenanced AHL bulletin + IWXXM Collect |
| AC6 | Lint catalog (MD/JSON/API/FE) shows WMO/ICAO/IWXXM source attribution |
| AC7 | A3-1 and AHL demo lint `ok=True` for errors after FP fixes; FPs logged |

## Cycle EV-039 — SQL ingest live e2e + teardown (S047)

**Session**: S047-sql-ingest-live-e2e  
**Features**: deepen **F16** (no new Fn expected)  
**Started**: 2026-08-06  
**Branch**: `evolve/EV-039-sql-ingest-live-e2e`  
**Status**: **completed** (`D-S047-13=1` / `D-S047-close=1`) — 2026-08-08  
**Completed**: 2026-08-08  
**Prior**: S046 / EV-038 completed  
**PR**: [#891](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/891) MERGED @ `fea30aba`  
**Corpus**: [Corpus: product §F16], [Corpus: tests], [Corpus: journeys §UJ-027], [Corpus: tech-spec], [Corpus: adr/ADR-029], [Corpus: adr/ADR-030]

### Scope (Phase 0 — locked 2026-08-06; AskQuestion unavailable — chat `1,1,1,1,2` → **D-S047-open**)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| Q1 | decision | Session? | Open **S047** → **EV-039** (feature / deepen F16) |
| Q2 | decision | DB coverage? | **All four**: Postgres + MySQL + SQL Server + SQLite |
| Q3 | decision | Teardown? | **Integration + e2e + local** — audit and fix gaps |
| Q4 | decision | Harness? | **Docker Compose profile** + Playwright against local stack |
| Q5 | decision | UI preview? | **No** — docs/repo only |

### In scope

- Local live SQL engines for F16 BYOC upload verification via Playwright (non-mocked preflight/send)
- Compose-managed disposable DBs + SQLite file path; hard teardown (containers, volumes, temp files, processes)
- Test-plan / journey / tech-spec deltas for live local SQL suite

### Out of scope

- New DB vendors; live WIS2/EDIS/F19; production SQL containers; new product Fn; UI preview this cycle

### Preset

**Standard** — `00→16→01→02→04→05→07→08→09→10→11→12→13` (skip 03, 06 unless later need)

### Acceptance (locked 2026-08-06; chat `1` → **D-S047-ac**)

| AC | Criterion |
|----|-----------|
| AC1 | Compose mock-byoc healthy PG/MySQL/SQL Server; SQLite disposable file |
| AC2 | Live Playwright preflight→send for all four dialects + write assertion |
| AC3 | Mocked H6′ UJ-027 suite stays green and separate |
| AC4 | Compose/e2e teardown — no orphans; SQLite temps removed |
| AC5 | Testcontainers fixtures always tear down |
| AC6 | Teardown audit gaps fixed or waived in session report |
| AC7 | TC-F16-LIVE-* mapped; make/CI documents live suite (opt-in OK) |

**01-requirements**: standing deltas written 2026-08-06 — feature-list §F16, user-journeys UJ-027, test-plan TC-F16-LIVE-*, tech-spec pointer, requirements-decisions EV-039 rows.

### Gate A (locked 2026-08-06; chat `2` → **D-S047-02-gate-a**)

| ID | Decision |
|----|----------|
| D-S047-02-gate-a | **2** — PASS; add `spec.md` EV-039 deepen note in 02; S02.M1/M2/M4/M5 → 04/07 |

**Status:** Gate A **PASS** — close 02 → **04-tech-plan**.

### 04-tech-plan (locked 2026-08-06; chat `Q1:1 Q2:1 Q3:1+3 Q4:1+2+3(local only)` → **D-S047-04**)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| Q1 | decision | Teardown (S02.M1)? | **1** — `compose … down -v --remove-orphans` + post-check no named containers/volumes |
| Q2 | decision | Write assertion (S02.M4)? | **1** — query DB via async drivers after UI success |
| Q3 | decision | Harness (S02.M2)? | **1+3** — `make test-e2e-f16-live-sql` **and** `F16_LIVE_SQL=1` on `test-live-e2e` |
| Q4 | decision | LIVE vs CI (S02.M5)? | **1+2+3 local-only** — **Local:** LIVE in `make test-live` + all four dialects required. **CI:** opt-in; SQL Server skippable; LIVE not on default CI path |

**Artifacts:** `docs/sessions/S047-sql-ingest-live-e2e/reports/execution-plan.md` (10 tasks M1–M2); `build-plan-card.md` (M1 active).  
**Status:** draft pending `D-S047-04-plan` approval → then **05-verify-tech**.

### Plan approve (locked 2026-08-06; chat `1` → **D-S047-04-plan**)

| ID | Decision |
|----|----------|
| D-S047-04-plan | **1** — approve execution plan + Build Plan Card as written; close 04 → **05-verify-tech** |

**Status:** 04 **COMPLETE** — handoff Gate B.

### Gate B (locked 2026-08-06; chat `1` → **D-S047-05-gate-b**)

| ID | Decision |
|----|----------|
| D-S047-05-gate-b | **1** — PASS; S05.M*/L1 as 07 work; close 05 → **07-build M1 T1.1** (06 skipped) |

**Status:** Gate B **PASS** — Phase B complete; handoff **07-build**.

### 07-build notes (T1.1–T1.2)

- Teardown uses `BYOC_COMPOSE` with `-p metar-iwxxm-mock-byoc` so `down -v --remove-orphans`
  cannot remove backend/frontend (shared compose files).
- Contract tests: `tests/unit/test_compose_mock_byoc_teardown.py`.

### 11-verify-impl (locked 2026-08-06; chat `1` → **D-S047-11**)

| ID | Decision |
|----|----------|
| D-S047-11 | **1** — Approve AC1–AC7 (SQL Server waive OK); close 11 → **12-verify-deploy** |

**Evidence:** 09 PASS (advisories); 10 H6′ 7/7 + LIVE 001/002/004; tip `415898d0`.  
**Artifacts:** `reports/verify-impl.md`; `docs/reports/implementation-verification.md`.

### 12-verify-deploy (locked 2026-08-06; chat `1` → **D-S047-12**)

| ID | Decision |
|----|----------|
| D-S047-12 | **1** — Approve checklist; push + PR; 13 after CI/CD (**H4–H5 required**) |

- No prod SQL containers; harness + docs + `js-yaml` pin; H0c 6/6.
- Checklist: `reports/deploy-checklist.md`.
- Merge to `main` still requires explicit approval before live smoke.

### 13-deploy-smoke (resume 2026-08-08; chat `2` → **D-S047-resume**)

| ID | Decision |
|----|----------|
| D-S047-13-cli | **1** (2026-08-06) — CLI DOKS tag `20260806224839-7df9f8f` while GHA tip CI outage |
| D-S047-resume | **2** — Resume S047; finish 13 properly then close (not cancel hygiene-only) |
| D-S047-13 | **1** — Approve 13; post-merge CD [31130303373](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31130303373); H0c/H1/H4–H5 re-PASS 2026-08-08 |
| D-S047-close | **1** — Close S047 / EV-039; land closeout docs on `main` |

**Artifacts:** `reports/deploy-smoke.md`; `docs/evolve-report-EV-039.md`.  
**Status:** EV-039 / S047 **CLOSED**.

---

## Cycle EV-038 — Epic #846 corpus residuals #849–#861 (S046)

**Session**: S046-iwxxm-corpus-residuals  
**Features**: deepen **F2 / F4 / F6 / F7 / F32** (no new Fn expected — Q2 whole residual set)  
**Started**: 2026-08-05  
**Branch**: `evolve/EV-038-iwxxm-corpus-residuals`  
**Status**: **completed** (`D-S046-13`=1) — PR [#890](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/890) MERGED @ `619a7ac3`; DOKS `20260806144346-619a7ac`; H1–H5 + UJ-050 PASS  
**Completed**: 2026-08-06  
**Prior**: S045 / EV-037 completed  
**Issues**: [#849](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/849)–[#861](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/861) under epic [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) — **all closed**  
**Epic**: [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) **CLOSED**

### Scope (Phase 0 — locked 2026-08-05; AskQuestion unavailable — chat `Q1=1,Q2=5,Q3=2`)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| Q1 | decision | Session? | Open **S046** → **EV-038** |
| Q2 | decision | Scope? | **Whole residual set** #849–#861 (split milestones) |
| Q3 | decision | Preset? | **Standard** — `00→16→01→02→04→05→07→08→09→10→11→12→13` (skip 03, 06) |

### Milestone plan (locked 2026-08-05; AskQuestion unavailable — chat `Q1=1,Q2=1,Q3=1` → **D-S046-mplan**)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| D-S046-mplan Q1 | decision | Order? | **M1 docs → M2 release-line → M3 corpus soft → M4 encode** |
| D-S046-mplan Q2 | decision | UI preview? | **Yes** — open local non-deployed UI when M2/#854 |
| D-S046-mplan Q3 | decision | Proceed? | Lock → commit session-open → **01-requirements** |
| D-S046-ac | decision | ACs? | **AC=1** approve AC1–AC14 |
| D-S046-02-gate-a | decision | Gate A? | **2** — PASS after OpenAPI/SoT decision in 02 |
| D-S046-sot | decision | #851 SoT shape? | **1** — Python SoT → generated committed JSON → FE + OpenAPI/CI |
| D-S046-04-plan | decision | Execution plan? | **1** — approve as written; close 04 → start 05 |
| D-S046-05-gate-b | decision | Gate B? | **1** — PASS; S05.M*/L1 as 07; close 05 → 07 M1 T1.1 |
| D-S046-853 | decision | #853 US lag? | **1** — **Ship WMO-only first**; document lag in sync PR; do not block ICAO default |
| D-S046-853-push | decision | Push before T2.7? | **1** — continue T2.7 then push (lag+push chat `1,1`) |
| D-S046-859 | decision | #859 drift? | **1** — offline SCH↔CSV non-flake gate; live RDF optional soft; known SpaceWx SCH-ahead allowlisted |
| D-S046-850 | decision | #850 resuspended? | **1** — cite-only deferral (no WMO peer / no invented TAC); matrix G-VONA-5 |
| D-S046-phase-c | decision | Phase C checkpoint? | **1** — push + start T5.2 (09-qa + 10-e2e); `gates.c_to_d` passed (tech + user) |
| D-S046-11 | decision | 11-verify-impl? | **1** — approve AC1–AC14 + UJ-050; proceed to T5.4 |
| D-S046-12 | decision | 12-verify-deploy? | **1** — approve checklist; open PR; merge+13 after CI |
| D-S046-13 | decision | 13-deploy-smoke? | **1** — approve H1–H5 + UJ-050; close EV-038 / S046 |

| Milestone | Issues | Theme | Notes |
|-----------|--------|-------|-------|
| **M1** | #858, #861, #855 | Docs / process | G5 OOS, G8 modelling watch, deprecation template — chip epic early |
| **M2** | #851, #852, #853, #854 | Release-line automation + UX | SoT → tip-diff → US gate → picker Latest/Previous (#854 after SoT); local UI preview |
| **M3** | #859, #860, #857 | Corpus soft / gates | Codes drift, translation-failed (optional), SWXA unlock |
| **M4** | #849, #850, #856 | Encode deepen | VONA vertical/resuspended + VA-EGGX `wmoPass` |

### Out of scope

Metrics UI (#836); workbench epic (#840) unless tiny catalog-tier; hand-edit
`vendor/schemas/*`; re-pin as primary goal of this cycle.

### Corpus cites / waivers

| Ref | Kind | Target | Notes |
|-----|------|--------|-------|
| `[Corpus: product]` | cite | F2 / F4 / F6 / F7 / F32 deepen | no new Fn expected |
| `[Corpus: tech-spec]` | cite | versions / vendor pin / CI | #851–#853, #859 |
| `[Corpus: api]` | cite | OpenAPI enum alignment | #851 |
| `[Corpus: tests]` | cite | TC-EV038-* / quality pack | per milestone |
| `[Corpus: decisions]` | cite | this cycle | — |
| `[docs/domain/iwxxm/RELEASE_LINE_ADOPTABILITY.md]` | cite | adopt gaps | #851–#855, #861 |
| `[docs/domain/rules/COVERAGE_MATRIX.md]` | cite | G3–G8 / F32 residuals | #849–#850, #856–#861 |

### Acceptance criteria (01 — **approved** AC=1 / **D-S046-ac**)

See [01-requirements-summary.md](../sessions/S046-iwxxm-corpus-residuals/reports/01-requirements-summary.md).

| ID | Milestone | Ticket | Summary | Status |
|----|-----------|--------|---------|--------|
| AC1–AC3 | M1 | #858/#861/#855 | OOS docs, modelling watch, deprecation template | **approved** |
| AC4–AC7 | M2 | #851–#854 | SoT, tip-diff, US gate, picker Latest/Previous | **approved** |
| AC8–AC10 | M3 | #859/#860/#857 | Codes drift, translation-failed, SWXA unlock | **approved** |
| AC11–AC13 | M4 | #849/#850/#856 | VONA deepen + VA-EGGX `wmoPass` | **approved** |
| AC14 | Roll-up | #846 | Close/defer all residuals | **approved** |

### SoT decision (02 — locked **D-S046-sot**=1)

| Layer | Choice |
|-------|--------|
| Runtime SoT | `apps/backend/src/config/iwxxm_versions.py` |
| Shared artifact | Generated committed JSON (roles: `latest` / `previous` + `default` + version ids) |
| FE | Import JSON for picker options/labels (#854) |
| OpenAPI | Enum/docs from same export; CI asserts match |
| CI | Regen + drift fail (`git diff --exit-code` or equivalent) |

### Stage log

| Stage | Status | Note |
|-------|--------|------|
| 00-context | completed | Session-open; D-S046-mplan locked |
| 16-evolve | **completed** | Closed `D-S046-13`=1 @ 2026-08-06 |
| 01-requirements | completed | **D-S046-ac** AC=1 |
| 02-verify-plan | completed | Gate A PASS |
| 04-tech-plan | completed | **D-S046-04-plan**=1 |
| 05-verify-tech | completed | Gate B PASS |
| 07-build | completed | M1–M4 through T4.8 |
| 08-verify-build | completed | T5.1 PASS |
| 09-qa | completed | pass_with_advisories |
| 10-e2e | completed | T0 PASS |
| 11-verify-impl | completed | **D-S046-11**=1 |
| 12-verify-deploy | completed | **D-S046-12**=1; #890 |
| 13-deploy-smoke | completed | **D-S046-13**=1; DOKS `20260806144346-619a7ac`; H1–H5 + UJ-050 |

### #853 lag policy (07 — locked **D-S046-853**=1)

**Ship WMO-only first.** Annex 3 / `DEFAULT_VERSION` adopt proceeds when WMO checklist is
ready. If `make iwxxm-us-compat-smoke` fails, record lag in the sync PR and keep US on the
last-known-good WMO base until NWS pin catches up; open a child under #846 if encode work
is needed. Do **not** block ICAO adopt on US lag.
See [RELEASE_LINE_ADOPTABILITY.md §iwxxm-us lag policy](../domain/iwxxm/RELEASE_LINE_ADOPTABILITY.md).

### #859 drift policy (07 — locked **D-S046-859**=1)

Offline **SCH RDF ↔ iwxxm-codelists CSV** is the CI gate (no HTML). Live `--live` is
advisory (soft-skip HTML/network). Known SCH-ahead URIs allowlisted until codelist pin
catches up. Drift always emits stable `http://codes.wmo.int/…` for #889.
See [RELEASE_LINE_ADOPTABILITY.md §codes.wmo.int URI drift](../domain/iwxxm/RELEASE_LINE_ADOPTABILITY.md).

---

## Cycle EV-037 — Matrix dispositions #869 / #870 / #872 (S045)

**Session**: S045-matrix-disposition-residuals  
**Features**: deepen **F2 / F6 / F32** only (no new Fn — Q2/Q3)  
**Started**: 2026-08-05  
**Branch**: `evolve/EV-037-matrix-disposition-residuals`  
**Status**: **completed** 2026-08-05 — 11 **APPROVED** (`D-S045-11`); 12/13 **WAIVED** (`D-S045-12-13-waive`); PR [#887](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/887) **MERGED** @ `b7302fe4` (`D-S045-merge=1`)
**Prior**: S044 / EV-036 completed
**Issues**: [#869](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/869), [#870](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/870), [#872](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/872) under epic [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) — **all closed** 2026-08-05 @ `c51e6e9b`

### Scope (Phase 0 — locked 2026-08-05; AskQuestion unavailable — chat `Q1=1,Q2=1,Q3=1,Q4=1` + `G2=1`)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| Q1 | decision | Session? | Open **S045** → **EV-037** |
| Q2 | decision | Dispositions? | **Approve all three** research dispositions as cycle scope |
| Q3 | decision | Preset? | **Lean + 07/08** — `00→16→01→02→07→08→11` (skip 03–06, 09, 10, 12/13) |
| Q4 | decision | UI preview? | **N/A** — no product UI |
| G2 | decision | Proceed? | Approve → commit session-open → **01-requirements** |
| AC | decision | AC1–AC4? | **Approved** (AC=1) — close 01 → start **02-verify-plan** |
| Gate A | decision | S02.M1–M3 / Phase A? | **PASS** (`D-S045-02-gate-a`) GateA=1 — accept S02.M1–M3 as **07** work; close 02 → start **07-build** |
| D-S045-11 | decision | 11-verify-impl? | **Approve all ACs met** — close 11 |
| D-S045-12-13-waive | decision | Deploy 12/13? | **Waive** — no runtime product change |
| D-S045-next | decision | After 11? | **Push branch + open PR** to `main` |
| D-S045-merge | decision | Merge #887? | **1** — merge + close EV-037 / S045 |

### Locked dispositions

| Ticket | Disposition |
|--------|-------------|
| **#869** | Non-blocking upstream Guidance gap; VONA SoT = ICAO + FM205 + AHL + XSD/SCH + code lists; cookbook = derived implementation guide |
| **#870** | Official US Schematron = **N/A / not published**; retain WMO XSD/SCH + US XSD + semantic/fixtures columns (do not N/A all US validation) |
| **#872** | AHL **source** ✅ for all mapped families; redesign Bulletin AHL cell into source \| T1T2 map \| parser \| BBB \| splitter \| filename \| COLLECT \| fixtures \| CI; children only for true impl gaps |

### Acceptance criteria (01 — **approved** AC=1)

| ID | Criterion | TC | Status |
|----|-----------|-----|--------|
| AC1 | VONA SoT hierarchy + non-blocking Guidance silence; cookbook derived | TC-EV037-001 | **approved** |
| AC2 | US Schematron N/A; validate class split | TC-EV037-002 | **approved** |
| AC3 | AHL source ✅ + source vs impl matrix columns | TC-EV037-003 | **approved** |
| AC4 | Close/reword #869/#870/#872; link #846 | TC-EV037-004 | **approved** — issues **closed** 2026-08-05 |

### Out of scope

New Fn; browser UI; deploy runtime; inventing US Schematron; editing upstream
`TAC-to-XML-Guidance.txt`; full AHL parser/fixture implementation beyond matrix redesign
and residual child tickets.

### Corpus cites / waivers

| Ref | Kind | Target | Notes |
|-----|------|--------|-------|
| `[Corpus: product]` | cite | F2 / F6 / F32 deepen | no new Fn |
| `[Corpus: tests]` | cite | provenance / matrix TCs | TC-EV037-* as needed |
| `[Corpus: decisions]` | cite | this cycle | — |
| `[docs/domain/rules/COVERAGE_MATRIX.md]` | cite | matrix cells | domain opt-in |
| `[docs/domain/rules/PROVENANCE_MAP.md]` | cite | VONA / US / AHL cites | + `.json` |

### Proposed Lean+07/08 routing (Q3=1)

`00 → 16 → 01 → 02 → 07 → 08 → 11`  
Skip: `03`, `04`, `05`, `06`, `09`, `10`, `12`, `13` (docs/matrix; no UI; waive 12/13 at gate)

### Gate A / 02 (locked 2026-08-05)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| S02.M1 | decision | PROVENANCE status lag? | **1** — accept as **07** work (`US_SCH_ABSENT`→N/A; VONA silence non-blocking) |
| S02.M2 | decision | Bulletin AHL gaps? | **1** — accept as **07** — split source vs impl columns |
| S02.M3 | decision | TC-EV037 tests missing? | **1** — accept as **07** — add `tests/provenance/test_tc_ev037_*.py` |
| Gate A | gate | Phase A / 02 close? | **PASS** (`D-S045-02-gate-a`) GateA=1 — start **07-build** (Lean; no 04) |
| B→C | gate | Phase B skipped (Lean)? | **waived_lean** — 04/05 skipped; 07 COMPLETE → **08-verify-build** |

### Stage log

| Stage | Completed | Notes |
|-------|-----------|-------|
| 00-context | 2026-08-05 | S045 open; Lean+07/08 Q1–Q4 |
| 01-requirements | 2026-08-05 | AC=1 approve AC1–AC4; `reports/01-requirements-summary.md` |
| 02-verify-plan | 2026-08-05 | Gate A **PASS**; S02.M1–M3 → 07; `reports/02-verify-plan-audit.md` |
| 07-build | 2026-08-05 | COMPLETE @ `c51e6e9b`; #869/#870/#872 closed; `reports/07-build-report.md` |
| 08-verify-build | 2026-08-05 | PASS @ `90c2e8a3`; provenance 188 green; `reports/verification-report.md` |
| 11-verify-impl | 2026-08-05 | **APPROVED** (`D-S045-11`); AC1–AC4 MET; `reports/verify-impl.md` |
| 12 / 13 | waived | `D-S045-12-13-waive` — docs/matrix only |

### Implementation AC status (11 — locked)

| ID | Status |
|----|--------|
| AC1 | **MET** |
| AC2 | **MET** |
| AC3 | **MET** |
| AC4 | **MET** — issues closed |

---

## Cycle EV-036 — Local long jobs on pre-commit / slim CI (S044)

**Session**: S044-local-precommit-long-jobs  
**Features**: deepen **M5** only (no new Fn — B4=1)  
**Started**: 2026-08-05  
**Branch**: `evolve/EV-036-local-precommit-long-jobs`  
**Status**: **completed** 2026-08-05 — 11 approved (`D-S044-11`); deploy 12/13 waived (`D-S044-12-13-waive`); push+PR (`D-S044-next`)  
**Prior**: S043 / EV-035 completed

### Scope (Phase 0–02 — locked 2026-08-05; AskQuestion unavailable — chat)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| Q1 | decision | Session? | Open **S044** → **EV-036** |
| Q2 | decision | Intent? | Local-capable long jobs on developer hooks to **save CI runner time** (4+1) |
| Q3 | decision | UI/deploy? | **N/A tooling only** — “frontend” = Vitest/`audit-frontend` gates, not product UI |
| B1 | decision | Local timing? | **Both** — fast+**medium on commit**; long suite on **push** |
| B2 | decision | Remote CI? | **Amended (D-S044-02-gate-a)** — drop remote **validate** + **Compose integration**; **keep** unit matrix + coverage + **PR coverage comment**; lint/format = local only |
| B3 | decision | Job set? | `validate-ci` + `ci-prepush` (+ **R1** Compose integration on push) |
| B4 | decision | Fn + preset? | Deepen **M5**; **Lean** |
| G1 | decision | Routing? | **Lean** `00→16→01→02→07→08→09→11` (skip 03–06, 10, 12/13) |
| G2 | decision | Proceed? | Approve → branch → **01-requirements** |
| R1 | decision | Compose integration? | **Local only** — remove remote `integration`/Compose from `ci-cd.yml`; pre-push runs `make ci` (= `ci-prepush` + `test-integration` [+ wis2box harness if part of local target]) |
| AC | decision | M5 / TC-EV036? | **Approved** (AC3 amended with B2: remote keeps units/coverage) |
| Gate A | decision | S02.M1/M2/M3/L1 | **1,1,1,1** with **S02.M2 modified** — units+coverage stay remote |
| D-S044-11 | decision | 11-verify-impl? | **Approve all ACs met** — close 11 |
| D-S044-next | decision | After 11? | **Push branch + open PR** to `main` |
| D-S044-12-13-waive | decision | Deploy 12/13? | **Waive** — no runtime product change |

**Branch created**: `evolve/EV-036-local-precommit-long-jobs` (from `main` @ 97a5c131)

### Resource model (canonical — Gate A amend)

| Tier | When | Contents | Rationale |
|------|------|----------|-----------|
| **Fast** | every `git commit` | format/lint/types/secrets/yaml/catalog/canaries | cheap always-on |
| **Medium** | every `git commit` | `validate-ci` medium extras (de-duped vs fast) | config/audit before push |
| **Long (local)** | every `git push` | `make ci` = `ci-prepush` + Compose **integration** (ports 18000/18001); no second `validate-ci` | units (local) + integration local |
| **Remote** | PR / push CI | **No** validate job, **no** Compose integration; **keep** package **unit matrix + coverage** + sticky **PR coverage comment**; keep `tac2iwxxm-native`, `e2e-smoke`, `test-alembic`, deploy | save Compose/validate minutes; retain coverage signal |

**Out of scope**: Product Fn; browser UX; family `test-*-quality` on every hook; Playwright smoke on every push (stays remote e2e-smoke); live prod E2E; GHCR/PyPI publish changes.

### Corpus cites / waivers

| Ref | Kind | Target | Notes |
|-----|------|--------|-------|
| `[Corpus: product]` | cite | M5 deepen | workspace tooling / hooks |
| `[Corpus: tech-spec]` | cite | Makefile + hook layout | + `dependency-inventory.md` |
| `[Corpus: tests]` | cite | `test-plan.md` Quality Gates / EV-002 dual-run amend |
| `[docs/ops/DEVELOPMENT.md]` | cite | ops satellite | install-hooks runbook |

### Proposed Lean routing (B4=1)

`00 → 16 → 01 → 02 → 07 → 08 → 09 → 11`  
Skip: `03`, `04`, `05`, `06`, `10`, `12`, `13` (no UI; no runtime deploy; tooling-only — waive 12/13 at gate)

---

## Cycle EV-035 — Rule-source traceability / provenance registry (S043)

**Session**: S043-rule-source-traceability  
**Features**: deepen **F6 / F12 / F15 / F2** (no new Fn — G1=2)  
**Started**: 2026-08-05  
**Branch**: `evolve/EV-035-rule-source-traceability`  
**Status**: **completed** 2026-08-05 — deploy 12/13 waived (`D-S043-12-13-waive`)  
**Prior**: S042 / EV-034 completed

### Scope (Phase 0 — locked 2026-08-05; AskQuestion unavailable — chat `Q1=3,Q2=4,Q3=1,Q4=2` + `G1=2,G2=1,G3=1,G4=1`)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E35-1 | decision | Deliverable? | **Both** — re-analyze/link **and** standing provenance under `docs/domain/rules/` |
| E35-2 | decision | Rule stack? | **Full** — ISSUE_CATALOG + encode/SCH + bulletin AHL/ops |
| E35-3 | decision | Session? | Open **S043** → **EV-035** |
| E35-4 | decision | Preset? | **Standard** `00→16→01→02→04→07→08→09→11→12→13` |
| E35-5 | decision | Tests? | **Dense asserts** for every rule cited or revisited |
| G1 | decision | Fn? | **Deepen only** F6/F12/F15/F2 — **no F33** |
| G2 | decision | Routing? | Approve Standard as drafted |
| G3 | decision | CORPUS? | **Path-cite only** `[docs/domain/…]` |
| G4 | decision | Proceed? | Start **01-requirements** |

**Scope (verbatim)**: Re-analyze documents already reviewed and rules already extracted;
link each rule back to its authoritative source (canonicals + `RULE_SOURCE_URLS` + mining
digs); establish ongoing tracking via a standing provenance artifact under
`docs/domain/rules/` (**no new product Fn**); raise to the user any rule without a findable
source. Cover full stack: lint `ISSUE_CATALOG`, encode / Schematron asserts, and bulletin
AHL/ops cites. Ship parametric/matrix tests with **many asserts** per cited or revisited
rule (reuse F29 harness patterns). Standard evolve path; no UI.

**Out of scope**: New Fn (F33); browser provenance UX; hand-editing `vendor/schemas/*`;
re-pin IWXXM line; auto-closing all #846 residual children (may file provenance gap tickets
only).

### Corpus cites / waivers

| Ref | Kind | Target | Notes |
|-----|------|--------|-------|
| `[docs/domain/README.md]` | cite | hub | Domain opt-in (not minimal CORPUS) |
| `[docs/domain/rules/RULE_SOURCE_URLS.md]` | cite | URL catalog | |
| `[docs/domain/rules/COVERAGE_MATRIX.md]` | cite | coverage | |
| `[docs/domain/rules/ISSUE_CATALOG.md]` | cite | lint codes | F15/F12 |
| `[Corpus: product]` | cite | deepen F6/F12/F15/F2 | no new Fn |
| `[Corpus: tests]` | cite | TC-EV035-001..006 | |
| `[Corpus: WAIVED — domain CORPUS membership; reason: G3=1 path-cite; decided: EV-035]` | waiver | CORPUS row | path-cite sufficient |

### Gap disposition (`D-S043-gaps` — 2026-08-05)

**Policy**: re-mine first; open ticket on fail.

| Gap | Remine | Ticket |
|-----|--------|--------|
| VONA Guidance silent | Partial — AHL/FM205 found; Guidance still empty | [#869](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/869) |
| iwxxm_us validate ⚠ | Confirmed — no US SCH in pin | [#870](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/870) |
| ISSUE_CATALOG thin cites | Needs PROVENANCE_MAP | [#871](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/871) |
| Bulletin AHL matrix gaps | AHL sources OK; matrix may be stale | [#872](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/872) |

Dig: `docs/domain/mining/vona-encode-remine-ev035-mining-notes.md` · report: `reports/provenance-gaps.md`

### Stage log

| Stage | Completed | Notes |
|-------|-----------|-------|
| 00-context | 2026-08-05 | S043 open; Standard approved G2=1 |
| 01-requirements | 2026-08-05 | Deepen ACs + TC-EV035; `reports/01-requirements-summary.md` |
| 02-verify-plan | 2026-08-05 | Gate A **PASS**; Batch A `1,1,1,1`; remine→#869–#872; `reports/02-verify-plan-audit.md` |
| 04-tech-plan | 2026-08-05 | Gate B **PASS**; Batch B `1,1,1,1`; execution-plan approved |
| 07-build | 2026-08-05 | M0–M3 complete; tip 5a03b930; TC-EV035 182 green |
| 08-verify-build | 2026-08-05 | PASS — verification-report.md; C→D passed |
| 09-qa | 2026-08-05 | PASS — qa-report.md; 182 + format + H0c |
| 11-verify-impl | 2026-08-05 | APPROVED — `continue` / D-S043-11 |
| 12-verify-deploy | 2026-08-05 | **WAIVED** — no runtime surface (S02.L1) |
| 13-deploy-smoke | 2026-08-05 | **WAIVED** — with 12 |

### Gate A / 02 (locked 2026-08-05)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| S02.M1 | decision | VONA cell? | **1** — ⚠ Guidance silence; ✅ AHL/FM205/XSD/peer in PROVENANCE_MAP (`D-S043-02-batch-a`) |
| S02.M2 | decision | #871 scope? | **1** — umbrella catalog↔URL; closes when TC-EV035-002 greens |
| S02.M3 | decision | #872 close path? | **1** — 07 matrix refresh may close some cells without new code |
| S02.L1 | decision | Deploy 12/13? | **1** — may waive if no runtime surface (AskQuestion later) |
| E35-02 | gate | Gate A / 02 close? | **PASS** — start **04-tech-plan** (`D-S043-02-phase-a`) |

### Gate B / 04 (locked 2026-08-05)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E35-T1 | decision | Milestones? | **1** — M0–M3 |
| E35-T2 | decision | Map format? | **1** — MD + JSON twin |
| E35-T3 | decision | Catalog scope? | **1** — all ISSUE_CATALOG codes |
| E35-T4 | decision | Deps/CI/deploy? | **1** — no new deps; tiered CI; plan 12/13 waive |
| E35-04 | gate | Gate B / 04 close? | **PASS** — start **07-build** @ T0.1 (`D-S043-04-plan`) |
| E35-11 | decision | 11 ACs? | **approve all MET** (`continue` / `D-S043-11`) |
| E35-12-13 | gate | Deploy 12/13? | **WAIVE** — docs/tests-only (`D-S043-12-13-waive`; S02.L1) |

## Cycle EV-034 — Automate DOKS image rollout in CD (S042)

**Session**: S042-doks-cd-rollout  
**Features**: deepen **F30** (infra/CD — no new product Fn)  
**Started**: 2026-08-05  
**Branch**: `evolve/EV-034-doks-cd-rollout`  
**Status**: **completed** 2026-08-05 (`D-S042-13` = 1) — TC-F30-007 live @ `20260805115809-d3f4bb9`  
**Prior**: S041 / EV-033 lean-closed (`D-S041-1+3`); S040 / EV-032 remains suspended (`resume_after` S042 — eligible to resume)

### Scope (Phase 0 — locked 2026-08-05; AskQuestion unavailable — chat `A,A,A,B,A`)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E34-1 | decision | Rollout targets? | **API + frontend + worker** |
| E34-2 | decision | Image pin? | **Immutable `TIMESTAMP-SHA` tag** + `rollout status` |
| E34-3 | decision | Cluster auth? | GitHub Actions secret **`KUBE_CONFIG`** (base64 kubeconfig) |
| E34-4 | decision | Render steps? | **Remove / optional no-fail** — DOKS-only CD |
| E34-5 | decision | Preset? | **Standard** `00→16→01→02→04→07→08→09→11→12→13` (skip 03/05/06; 10 optional) |

**Scope (verbatim)**: After successful GHCR push on `main`, CD must `kubectl set image` +
`rollout status` for `metar-api`, `metar-frontend`, and `metar-worker` in namespace
`metar-iwxxm`, pinning each container to the immutable push tag
(`ghcr.io/empiric2/tac-to-iwxxm/{backend,frontend,worker}:TIMESTAMP-SHA`). Auth via
Actions secret `KUBE_CONFIG` (base64 kubeconfig). Render deploy-hook steps become
optional/non-blocking (or removed); missing Render hooks must not fail Deploy.
Missing `KUBE_CONFIG` on `main` Deploy **fails** (fail-closed). Baseline one-shot
already live: `20260805003332-5245f8d`.

**Out of scope**: New product Fn; S040 resume; changing DOKS topology/IaC beyond image
roll; Alembic redesign (initContainer remains).

## Cycle EV-033 — F8 worker INGEST_POLLER_URL hardening (S041)

**Session**: S041-worker-poller-hardening  
**Features**: deepen **F8**  
**Started**: 2026-08-04  
**Completed**: 2026-08-05  
**Branch**: `main` @ `5245f8de` (PR #865)  
**Status**: **completed** (lean-close `D-S041-1+3`)  
**Prior**: S040 / EV-032 **suspended** (not cancelled) during this cycle

### Scope (Phase 0 — locked 2026-08-04; AskQuestion unavailable — user “proceed 1–5”)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E33-1 | decision | Session vs S040? | New session S041; suspend S040 |
| E33-2 | decision | Scope? | All prevention items **1–5** + worker code refuse placeholder/non-https |
| E33-3 | decision | Preset? | **Standard** |
| E33-4 | decision | Close path? | **D-S041-1+3** lean-close (waive 09–13) + DOKS one-shot + open S042 |

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
| E33-4 | decision | Lean-close + DOKS one-shot? | Yes (`D-S041-1+3`) — waive 09–13; tag `20260805003332-5245f8d` | — |

### Stage log
| Stage | Completed | Notes |
|-------|-----------|-------|
| 00-context | 2026-08-04 | S041 open; S040 suspended |
| 01–04 / 07–08 | 2026-08-04 | Standard path; #865 merged; 08 PASS |
| 09–13 | waived 2026-08-05 | `D-S041-1+3`; deploy passed_via_ops |
| 16-evolve | 2026-08-05 | cycle closed; see evolve-summary.md |

## Cycle EV-032 — Official IWXXM corpus quality / WMO source parity (S040)

**Session**: S040-iwxxm-corpus-quality  
**Features**: **F32** (new — VONA quality bar) + deepen **F23** (#835) + **F4** / **F6** / **F2** / **F13** (#808 + corpus)  
**Issues**: [#846](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/846) (epic), [#835](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/835), [#741](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/741), [#808](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/808)  
**Started**: 2026-08-04  
**Branch**: `evolve/EV-032-iwxxm-corpus-quality` (from `main`)  
**Status**: **completed** 2026-08-05 (`D-S040-close` = 1) — T4.5 re-verified on `20260805115809-d3f4bb9`; #846 epic remains open for residual children

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

## Cycle EV-031 — Platform independence #842 / #830 / #712 (S038)

**Session**: S038-platform-independence-842  
**Features**: **F30** + **F31** (deepen F5/F7/F8/F21/F22/M4)  
**Issues**: [#842](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/842), [#830](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/830), [#712](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/712)  
**Started**: 2026-08-03  
**Branch**: `evolve/EV-031-platform-independence-842`  
**Status**: **completed** — `D-S038-13` = 1 (2026-08-03); F30/F31 Done; public DNS live

### Scope (Phase 0 — locked 2026-08-03)

| ID | Category | Question | Decision |
|----|----------|----------|----------|
| E31-1 | decision | Session open? | **3,1,1,1** — full epic+#712 IaC/cutover; general; Standard; local UI (`D-S038-open`) |
| E31-2 | decision | DOKS depth? | **3** — production cutover; Render decommission after soak (`D-S038-doks-depth`) |
| E31-3 | decision | F8 persistence? | **1** — keep F8 on **DigitalOcean Postgres** (`D-S038-f8`) |
| E31-4 | decision | Routing? | **1** — Standard (`D-S038-route`) |
| E31-5 | decision | Auth model? | **1** — Reintroduce **Supabase Auth** for **long-term storage**; amend F21 (`D-S038-auth-model`) |
| E31-6 | decision | Session store? | **1** — Logged-in → DO Postgres; guests → local + **loss notice** + **F22 privacy** (`D-S038-session-store`) |
| E31-7 | decision | #830? | **1** — Amend ticket: Auth-kept / strip data plane (`D-S038-830-amend`) |
| E31-8 | decision | Fn allocation? | **1,1,1** — **F30** + **F31**; start 01; commit open (`D-S038-fn`) |
| E31-M | decision | Document Manifest? | **1,1** — full 1–10; Feature List first (`D-S038-E31-M`) |
| E31-F30 | decision | F30 Feature List? | **1,1,1,1** — accept draft; F30 owns #830+#712; public convert APIs; continue F31 (`D-S038-F30`) |
| E31-F31 | decision | F31 Feature List? | **1,2,1,1** — accept draft; **auto-upload** local drafts on login; F21 **Amended**; write Feature List (`D-S038-F31`) |
| E31-guest-merge | decision | Guest→login drafts? | **2** — auto-upload all eligible local drafts (`D-S038-guest-merge`) |
| E31-spec-topo | decision | Spec topology? | **1,1,1,1** — accept topo; restore `packages/auth`; restore `/api/v1/work-sessions*`; data/cutover next (`D-S038-spec-topo`) |
| E31-spec-data | decision | Spec data/cutover? | **1,1,2,1** — single DO DB; Alembic; **one-time migrate** legacy Supabase→DO; write Spec then UJ (`D-S038-spec-data`) |
| E31-uj | decision | User Journeys? | **1,1,1** — UJ-045..048; persistent guest banner; write then Test Plan (`D-S038-uj`) |
| E31-tp | decision | Test Plan? | **1,1,1** — TC-F30/F31/EV031; H4–H5 required; lean remaining docs (`D-S038-tp`) |
| E31-gate-a | decision | 01 Gate A? | **1,1,1** — accept lean docs; defer tech gaps to 04; commit `fc3bbe5` (`D-S038-01-gate-a`) |
| E31-02 | decision | 02 batch C + Gate A? | **1,1,1** — fix C1–C5; keep ADR-033 Proposed; Gate A PASS → 04 (`D-S038-02-batch-c` / `D-S038-02-phase-a`) |
| E31-04-b1 | decision | 04 Batch 1? | **1,2,1,1** — M0–M7 shape; **JWKS-only**; Alembic in backend; restore `packages/auth` from git + strip admin (`D-S038-04-b1`) |
| E31-04-b2 | decision | 04 Batch 2? | **1,1,1(+CI),1** — placeholder DOKS DNS; **7d soak**; pg_dump + verify; **CI auto idempotent Alembic**; ADR-020 wire; ADR-033 @ Gate B (`D-S038-04-b2`) |
| E31-04 | gate | Gate B / plan approve? | **1** — approve M0–M7 (38 tasks) + **ADR-033 Accepted** → **07 @ T0.1** (`D-S038-04-plan`) |
| E31-T0.2 | docs | Amend #830? | **Done** — title/body Auth-kept + data-plane strip; link F30/F31/ADR-033 ([#830](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/830)) |
| E31-t63-waive | decision | T6.3 DNS? | **3 / waive_ip** — waive real DNS; pin `LIVE_*`/`liveE2e` to LB `168.144.12.70` + Host-header placeholders; public `api.baseUrl` stays Render; proceed T6.4 (`D-S038-t63-waive`) |
| E31-t65-waive | decision | T6.5 soak? | **1 / waive** — waive 7-day soak (day 0/7); suspend Render API+FE+worker now; archive LIVE_*; retarget `prod.json` + CI to DOKS (`D-S038-t65-waive`); DNS residual superseded by `api.tac-to-iwxxm.com` / `app.tac-to-iwxxm.com` |
| E31-11 | decision | 11 verify-impl? | **1** — approve F30+F31; skip local UI preview (`D-S038-11`) |
| E31-12 | decision | 12 deploy strategy? | **1** — approve mitigations + rollback; start 13 (`D-S038-12`) |
| E31-13 | gate | 13 smoke + Phase D? | **1** — approve 13 PASS; close Phase D / cycle closeout (`D-S038-13`) |

**Topology**: Supabase = Auth/JWT verify only. DigitalOcean = all product DB + DOKS compute.  
**Guest UX**: transient local storage; UI notice that progress is lost without login; honor privacy preference center.

**In:** #830 amend; hybrid sessions; F8→DO Postgres; DOKS prod cutover; ADR/corpus/deploy.  
**Out:** Engine rewrites; Supabase product PostgREST/DB; long-lived dual hosts after soak.

### Acceptance (cycle)

1. **F30**: Auth-only Supabase; DO Postgres data; DOKS cutover; #830 amended acceptance (**TC-F30-001..006**).
2. **F31**: Hybrid sessions; guest notice; auto-upload on login; F22 deepen; F21 Amended (**TC-F31-001..006**).
3. Public convert without login remains; JWT only for server session APIs.
4. Deploy smoke / H0–H5 against DOKS (and Auth) per routing.


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
