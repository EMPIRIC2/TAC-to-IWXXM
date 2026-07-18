# 02-verify-plan audit — S014 / EV-010

**Date**: 2026-07-18  
**Mode**: delta (F11–F14)  
**Status**: pending medium/low user review

## Document inventory

| # | Document | Delta scope | Status |
|---|----------|-------------|--------|
| 1 | feature-list.md | F11–F14 + F2 note | audited |
| 2 | spec.md | backend msgspec; packages PyPI/Rust/codegen | audited |
| 3 | user-journeys.md | UJ-022/023, UJ-DEV-005 | audited |
| 4 | test-plan.md | TC-F11–F14 | audited |
| 5 | api-contract.md | ADR-026 serialization table | audited |
| 6 | dependency-inventory.md | msgspec/Rust/bundle | audited |
| 7 | ADR-016 / ADR-026 | HTTP boundary amend | audited |
| 8 | config-spec.md | PyPI OIDC secrets | **gap** — recommended in manifest, not yet delta'd |
| 9 | deploy.md | PyPI + Render 12–13 | **gap** — recommended; defer to 04/12 OK if noted |

## Consistency checklist (Phase 4)

| Check | Result |
|-------|--------|
| Feature ↔ Spec | **PASS** — F11–F14 mapped to backend + three packages |
| Feature ↔ Journey | **PASS** — F11→UJ-022; F12–F14→UJ-023/DEV-005 |
| Journey ↔ Test | **PASS** — UJ-022/023/DEV-005 → TC-F11–F14 |
| Feature ↔ Test | **PASS** — TC-F11–F14 cover acceptance stubs |
| Spec ↔ Config | **GAP** — config-spec.md not updated for PyPI trusted publishing |
| Test ↔ Acceptance | **PASS** — gates mirror feature-list acceptance |
| Cross-doc naming | **PASS** — package/PyPI names consistent |
| Scope boundaries | **WATCH** — must-ship 11B is large; no doc conflict |
| Connectivity H4–H5 | **PASS** — UJ-022 + F11–F14 gate require H4–H5 after Render |

## Auto-approved (high confidence)

Traceable to E10 interview / requirements-decisions EV-010 table.

| ID | Statement | Source |
|----|-----------|--------|
| S1.1 | F11–F14 Planned for S014/EV-010 | E10-12 |
| S1.2 | PyPI names `tac-validate`, `iwxxm-validate`, `tac2iwxxm` at `0.1.0` | E10-4, E10-19 |
| S1.3 | `tac2iwxxm[validate]` depends on both validators | E10-20 |
| S1.4 | Schema bundle in `iwxxm-validate` wheel | E10-6 |
| S1.5 | Native Rust Schematron + XSD codegen from published XSD | E10-22, E10-23 |
| S1.6 | Domain rules: all 7 products; METAR/SPECI/TAF full depth | E10-21 |
| S1.7 | Soft benches; hard-fail at publish | E10-24 |
| S1.8 | OIDC trusted publishing per package version tag | E10-25 |
| S1.9 | Full Render 12–13 included (msgspec HTTP) | E10-15 |
| S1.10 | Pydantic retained for OpenAPI; no dual runtime validation | E10-17, E10-18, ADR-026 |
| S2.1 | Auth/work-sessions stay pydantic | E10-17 |
| S3.1 | UJ-022/023 + UJ-DEV-005 are the cycle journeys | E10-26 |
| S4.1 | TC-F11–F14 exist and gate publish/deploy | E10-24, E10-26 |

## Medium / low — need user verdict

### S2.M1 `[Ambiguity]` — msgspec on multipart routes

**Document**: api-contract.md §Serialization boundary; apps/backend `api.py`  
**Statement**: "High-churn routes use msgspec Struct decode/encode"  
**Evidence**: Convert/validate/lint/decode are **`multipart/form-data`** with FastAPI `Form`/`File`, not JSON bodies. msgspec’s primary win is JSON decode+validate ([msgspec why](https://msgspec.dev/why.html)).  
**Risk**: Claiming msgspec “request validation” on multipart may overstate the win; real gains are likely **response encode**, **package IR**, and optional post-parse Struct validation of form fields.

**Options for user**:
- **A (Recommended)**: Clarify ADR-026/api-contract — msgspec validates/encodes **response DTOs + internal Structs**; multipart intake stays FastAPI Form parsing; optional msgspec Struct after form assemble
- **B**: Add JSON body alternatives for high-churn routes this cycle (bigger contract change)
- **C**: Keep wording as-is; tech plan invents multipart→msgspec bridge without clarifying docs

### S8.M1 `[Gap]` — config-spec / deploy docs

**Statement**: Manifest recommended Config Spec + Deploy deltas for PyPI OIDC secrets and Render+PyPI  
**Status**: Not written in 01  
**Options**:
- **A (Recommended)**: Back-add minimal config-spec + deploy.md notes in a quick 01 fix before 03; else 04 owns them
- **B**: Explicitly defer both to 04-tech-plan / 12-verify-deploy (waiver)
- **C**: Defer config; write deploy.md PyPI section now only

### S1.M1 `[Uncertainty]` — must-ship 11B schedule risk

**Statement**: Everything must-ship including Rust Schematron, all-product domain rules, production codegen  
**Confidence**: High that user said it (E10-11=B); Medium that it is deliverable in one cycle without follow-ups  
**Options**:
- **A (Recommended)**: Keep must-ship; 04-tech-plan milestones with kill-switch only via AskQuestion if blocked
- **B**: Reclassify stretch now (contradicts E10-11)
- **C**: More context

## Contradictions found

None blocking after E10-15 amended skip-13. Pre-existing F7 “Planned” vs #716 merged is out of EV-010 scope.

## Overall

**PASS** — medium items resolved 2026-07-18:

| Item | Verdict |
|------|---------|
| S2.M1 multipart/msgspec | **A** — clarify response+Structs; Form intake unchanged (docs updated) |
| S8.M1 config/deploy gap | **A** — minimal PyPI OIDC notes in config-spec + deploy |
| S1.M1 must-ship risk | **A** — keep 11B; 04 milestones; AskQuestion if blocked |

**Status**: completed  
**Next**: 03-plan-tooling (PyPI/release guardrails) → 04-tech-plan
