---
slug: propagate-residuals-to-remarks
topic: "Optional propagate decode residuals into remarks / humanReadableText (#981)"
status: active
created: 2026-08-31
session_id: EV-981-feature-optional-propagate-decode-residuals-into
evolve_cycle_id: EV-981
linked_features: [F6, F9, F7.q]
github_issue: 981
---

# Context — propagate-residuals-to-remarks

[Corpus: product] [Corpus: api] [Corpus: journeys] [Corpus: tests]

## Goal

Give operators an **opt-in** to fold **decode residuals** into the remarks / `humanReadableText`
retention path (alongside RMK / free-text), instead of only showing them in the decode panel.
Default remains **off** so annex3 / UJ-026 semantics stay unchanged.

**Expansion (intake option 3):** profile-level defaults + Quality metrics (#836 / F7.q) residual
drill-down hooks.

## Baseline (2026-08-31)

| Surface | Today |
|---------|--------|
| Decode (`POST /decode-tac`, F9) | Residuals are explicit spans + "Not decoded: …" in summary; **not** written into IWXXM |
| Convert annex3 + `RMK` | `ConvertIssue` `REMARKS_EXCLUDED` (info); RMK not in XML — **UJ-026** |
| Convert `iwxxm_us` | Structured remark codecs; unparsed RMK remainder → `iwxxm-us:humanReadableText` — **UJ-026** |
| Quality metrics (F7.q) | Precomputed `GET /quality-metrics*` exposes `residuals[]` per stem; no fold/propagate flag |
| Profiles | No `propagate_residuals_to_remarks` (or equivalent) knob |

## Target

### R1 — Convert / package flag (default off)

- Request/API (and package convert options): boolean e.g. `propagate_residuals_to_remarks`
  (exact name in requirements/draft-docs).
- **Off:** current behavior (residuals diagnostic-only; UJ-026 unchanged; goldens unchanged).
- **On:** residual token text is appended into the profile-aware remarks / HRT emit path, with
  clear `ConvertIssue` / provenance (plain-language; no internal doc ids on operator surfaces).

### R2 — Profile-level default

- Semantic/exchange profile may declare a default for the flag.
- **annex3 default remains off** (must not silently retain all residuals).
- Operator/API override wins over profile default when explicitly set.
- Enabling a non-annex3 profile default requires corpus/ADR decision in Spec (do not invent).

### R3 — Workbench UI

- Toggle (or equivalent) on convert workbench; copy plain-language only
  ([Corpus: product] F7 / no-internal-doc-refs).
- Reflects effective value (explicit override vs profile default).

### R4 — Quality metrics hooks (deepen F7.q only)

- Residual / detail path surfaces whether residuals were or would be folded into remarks/HRT
  given flag or profile default (fixture field and/or UI indicator).
- **Do not** rebuild corpus browser; **do not** imply live WMO fetch (fixtures stay precomputed).

## Out of scope

- Silent annex3 default change to retain all residuals
- Structured remark codecs for known types (**UJ-040**)
- Full #836 Quality metrics rebuild
- Blind auto-enable across all profiles

## Must not break

- UJ-026 annex3 `REMARKS_EXCLUDED` when flag off
- Existing convert goldens / default-off CI
- F9 decode response shape (residuals stay on decode; fold is convert/emit concern)
- Operator-visible strings free of planning ids (EV-048)

## Journeys / features

| Id | Role |
|----|------|
| UJ-026 | Baseline fence (extend or sibling UJ for flag-on path) |
| UJ-042 / F7.q | Residuals in quality metrics; hook target |
| F6 | Convert / remarks emit |
| F9 | Decode residuals source |
| F7 / F7.q | Workbench toggle + QM deepen |

## Likely touchpoints (Build intent — gated)

- `packages/tac2iwxxm` convert + profile remark paths
- `apps/backend` convert Form field + OpenAPI; optional QM fixture field
- `apps/frontend` workbench toggle + Quality metrics residual UI
- Tests: package + API unit + journey/e2e; H4–H5 after UI

## Docs delta (Spec)

- `docs/feature-list.md` — F6 / F9 / F7.q deepen (not a new top-level Fn unless requirements chooses)
- `docs/api-contract.md` — convert flag + QM field if any
- `docs/user-journeys.md` — extend UJ-026 or new UJ
- `docs/test-plan.md` — T0/T2/H4–H5 mapping
- `docs/decisions/` and/or ADR if profile-default policy needs a standing decision

## Interview lock (2026-08-31)

- Intake: expand (profile + QM hooks)
- Routing: approved standard Spec + Build (e2e yes); gate closed
- Context batches E1–E8: accept all recommended (map as F6/F9/F7.q deepen)
- Requirements: A2 (no UI preview) + B1 package → UJ-070; flag `propagate_residuals_to_remarks`; QM field `residuals_propagated_to_remarks`

## Refs

- [#981](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/981)
- [#667](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/667) / UJ-026 — [Context: metar-remarks-667]
- [#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836) F7.q — closed; hook only
- Session: `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-981-feature-optional-propagate-decode-residuals-into/`
- Memory: `{session}/reports/memory-context.md` (KG empty — keep-local)
