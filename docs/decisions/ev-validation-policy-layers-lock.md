# Design lock — Registry / Detector / Policy / Runtime (pre-evolve)

**Locked:** 2026-09-20  
**Status:** Design locked — awaiting evolve intake (ADR-046 draft + ADR-028/038 amends in Spec band)  
**Corpus:** [Corpus: product §F15] [Corpus: product §F2] [Corpus: adr/ADR-028] [Corpus: adr/ADR-038] [Corpus: adr/ADR-044] [Corpus: adr/ADR-045] [Corpus: system-spec] [Corpus: api] [Corpus: decisions]

Pre-implementation lock for TAC lint + IWXXM output validation configuration. Does **not** authorize Build. Evolve must open Spec→gate before code.

## Architecture (four layers)

| Layer | Responsibility |
|---|---|
| **Registry** | Stable issue codes, default severity, message templates, tags |
| **Detector** | How a finding is produced (declarative pack DSL or `python:` escape hatch) |
| **Policy** | `extends` / select / ignore / severity / preview; IWXXM assert enablement |
| **Runtime** | Load, budgets, draft vs activate, overlays, shadow→flip |

## Round 1 locks (D-VPL-*)

| ID | Lock |
|----|------|
| D-VPL-01 | Registry stays in `packages/tac-validate` (ADR-028) |
| D-VPL-02 | Detectors are `tac-validate` packs (not decode packs as home) |
| D-VPL-03 | IWXXM inventory + output policy home: `packages/iwxxm-validate` |
| D-VPL-04 | Policy attached to conversion profile (ADR-038) |
| D-VPL-05 | Runtime lives in each owning package (no umbrella validation package) |
| D-VPL-06 | Small detector DSL v1 + escape hatch `detector: python:module:fn` registered by id |
| D-VPL-07 | Activate = fail-closed on unknown codes/assert ids; draft = warn-only (`library_yaml` lifecycle) |
| D-VPL-08 | National IWXXM rules = Schematron **bundles**; YAML customs only for tiny experiments |
| D-VPL-09 | No inline/file suppression language in v1 (use severity/`info` + policy ignore) |
| D-VPL-10 | Strict pack binding for annex3 METAR (pack-default path) |
| D-VPL-11 | Executable overlays = file/env only (ADR-044/045 trust); UI catalogs = read-only projections |
| D-VPL-12 | Cycle acceptance includes full METAR/SPECI **R1–R8** themes (sequenced flips, not one PR) |

## Round 2 locks (recommended → accepted)

### A — Composition & identity

| ID | Lock |
|----|------|
| D-VPL-A1 | **One** user-facing conversion profile; quality/IWXXM policies are modules it references |
| D-VPL-A2 | Policy ids are **separate** from profile ids (e.g. `annex3-metar-quality`) |
| D-VPL-A3 | **Per-product** policy docs; profile lists/references them |
| D-VPL-A4 | TAC policy applies **per contained report**; AHL/COLLECT envelope rules are separate detector packs |
| D-VPL-A5 | Resolve to a **single** policy at load (no dual lint pass by default) |

### B — Detector DSL & MatchPort

| ID | Lock |
|----|------|
| D-VPL-B1 | **MatchPort** protocol in `tac-validate`; apps/CLI may inject `tac-decoding` match (no hard import required for install) |
| D-VPL-B2 | No match: **strict error** on annex3 METAR pack-bound detectors; **standalone fallback** elsewhere |
| D-VPL-B3 | Inherit decode **spans** when MatchPort present |
| D-VPL-B4 | Membership tables stay in `tac-validate`; detectors reference family ids |
| D-VPL-B5 | Many detectors may map to one registry **code**; wire emit always uses registry code |
| D-VPL-B6 | Detector stages: `parse_gate` → `token` → `cross_field` |
| D-VPL-B7 | **Separate** lint step budget (not shared with decode 10k); exceed → fail closed with registered code (severity TBD in evolve) |

### C — Policy merge & severity

| ID | Lock |
|----|------|
| D-VPL-C1 | `extends` depth **capped** (e.g. 5) + cycle detection |
| D-VPL-C2 | Empty `select` = all non-preview defaults for that product (registry ∩ enabled detectors) |
| D-VPL-C3 | Single spelling: **`ignore`** (ESLint `off`); no parallel `severity: off` |
| D-VPL-C4 | Loosen severity in overlay requires **`rationale`**; CI warns; activate may allow for national profiles |
| D-VPL-C5 | Disable Schematron assert: same bar as C4; assert id must exist on that pin |
| D-VPL-C6 | Preview rules run in production API **only** if profile opts in or explicit API/CLI flag |

### D — IWXXM output policy

| ID | Lock |
|----|------|
| D-VPL-D1 | XSD failures always **error** — not in policy select |
| D-VPL-D2 | Well-formed / parse failures always **error** |
| D-VPL-D3 | `SCHEMATRON_SKIPPED` stays engine behavior — not a select surface |
| D-VPL-D4 | Unknown/stale assert id on activate for that pin → **fail** |
| D-VPL-D5 | Operator profile has **one primary pin**; multi-pin maps are CI helpers only |

### E — API / CLI / apps

| ID | Lock |
|----|------|
| D-VPL-E1 | Public HTTP: **profile id only** this cycle; policy overrides CLI/internal first |
| D-VPL-E2 | CLI: `--profile` resolves; `--policy` overrides |
| D-VPL-E3 | SDK: `profile=` primary; `policy=` advanced |
| D-VPL-E4 | `tac2iwxxm[validate]`: existing opt-in validate flags; profile supplies which policies when enabled |
| D-VPL-E5 | Workflows (ADR-042): stages take **profile id** only |
| D-VPL-E6 | Profile **resolver** in `tac2iwxxm` (contract owner); validators remain dumb loaders |

### F — Catalogs, UI, trust

| ID | Lock |
|----|------|
| D-VPL-F1 | Mined `tac_validation_rules.yaml` / IWXXM assert YAML = **generated only** + CI drift gate |
| D-VPL-F2 | Library kinds `tac_validation` / `iwxxm_validation` remain **catalog views**, not executable SoT |
| D-VPL-F3 | **No** separate operator “lint profile” picker in v1 (conversion profile only) |
| D-VPL-F4 | Draft policies: API/CLI only (not operator UI) |

### G — Testing, migration, versioning

| ID | Lock |
|----|------|
| D-VPL-G1 | Shadow compare bar: **code + span** (message text out of bar) |
| D-VPL-G2 | R1–R8 flip by **theme** (R2, R1, …) under one evolve |
| D-VPL-G3 | After flip: remove dual Python paths (delete or thin-wrap behind same detector id) |
| D-VPL-G4 | Policy `schema_version` = **integer**; breaking = bump + migrate note |
| D-VPL-G5 | New registry codes → package **minor**; builtin policy-only → **patch** |

## Explicit non-goals (v1)

- Decode packs emitting lint issues
- One YAML dialect for both TAC detectors and IWXXM Schematron asserts
- Executable overlays in guest storage or operator CRUD
- Remapping XSD / well-formed into style ignores
- Merging `tac-validate`, `iwxxm-validate`, and `tac-decoding`
- In-app executable detector editor
- Re-authoring WMO Schematron `test=` XPath in hand YAML
- Whole R1–R8 in a single flip PR (sequenced themes under one cycle)

## Packaging (developer use cases)

| Use case | Package |
|---|---|
| Convert TAC → IWXXM | `tac2iwxxm` |
| Lint / validate TAC | `tac-validate` (+ optional MatchPort from `tac-decoding`) |
| Validate IWXXM | `iwxxm-validate` |
| Convert + validates | `tac2iwxxm[validate]` |
| Explain TAC | `tac-decoding` |

No new umbrella validation package.

## Next steps (when evolve opens)

1. Evolve intake → session + routing plan (cite this lock file).
2. Spec: ADR-046 (four layers) + amend ADR-028 / ADR-038; feature-list F15/F2 deepen; schemas.
3. Build: M1 policy load → M2 R2 shadow/flip → M3 remaining R1–R8 → M4 IWXXM policy → M5 profile/CLI wiring → M6 generated catalogs only.
4. Issue + PR into `stage` per repo policy.

## Supersedes / relates

- Does not replace ADR-028 registry home — deepens authoring + policy.
- Composes with ADR-038 conversion profile as policy owner.
- Complements ADR-045 (decode/convert packs); lint detectors may consume MatchPort without merging packages.
