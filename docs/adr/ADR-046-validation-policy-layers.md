# ADR-046: Registry / Detector / Policy / Runtime for TAC and IWXXM validation

**Status:** Accepted (requirements lock — EV-validation-policy-layers / #1216, 2026-09-20)  
**Date:** 2026-09-20  
**Corpus:** [Corpus: product §F15] [Corpus: product §F2] [Corpus: adr/ADR-028] [Corpus: adr/ADR-038] [Corpus: adr/ADR-039] [Corpus: adr/ADR-044] [Corpus: adr/ADR-045] [Corpus: system-spec] [Corpus: api] [Corpus: decisions]

## Context

TAC lint has a maintainable **registry** (ADR-028) but detectors remain mostly imperative Python. Mined YAML under `tac2iwxxm` is a **catalog projection**, not an execution engine. IWXXM validation correctly uses vendor XSD + Schematron; mined assert lists help operators but are not a policy surface. Decode packs (ADR-045) proved declarative packs can scale match/explain/convert IR. Operators and SDK users need conversion profiles to bind **which** quality checks run, without a second peer “lint profile” picker or re-authoring WMO Schematron in hand YAML.

Design lock: [ev-validation-policy-layers-lock.md](../decisions/ev-validation-policy-layers-lock.md) (D-VPL-*).

## Decision

1. **Four layers**
   - **Registry** — stable codes / default severity / templates (`tac-validate`, ADR-028).
   - **Detector** — how findings are produced: `tac-validate` packs (small DSL v1) + `python:module:fn` escape hatch by id.
   - **Policy** — select / ignore / severity / preview / `extends`; IWXXM assert enablement + Schematron bundles. Owned by the **conversion profile** (ADR-038) via separate policy document ids.
   - **Runtime** — load, budgets, draft vs activate, file/env overlays; each package owns its runtime.

2. **Package homes**
   - Registry + TAC detectors + TAC quality policy runtime → `packages/tac-validate`.
   - IWXXM assert inventory + output policy runtime → `packages/iwxxm-validate`.
   - Profile **resolver** (compose profile → policy ids) → `packages/tac2iwxxm`.
   - No umbrella validation package.

3. **MatchPort** — `tac-validate` defines a protocol for optional decode match injection. Apps may pass `tac-decoding` results. Strict pack binding for annex3 METAR when detectors require match; inherit spans when present. Decode packs **do not** emit lint issues (ADR-045 boundary).

4. **UX / wire** — One user-facing **conversion profile**. No separate lint-profile picker in v1. Public HTTP remains profile-id only (no new policy override fields this cycle). CLI may use `--policy` overrides.

5. **IWXXM** — Vendor `.sch` remains SoT. Policy enables/disables assert ids and attaches national **bundles**. XSD and well-formed are always errors (not selectable). YAML custom XPath only for tiny experiments.

6. **Lifecycle** — Draft: warn on unknown ids. Activate / CI: fail-closed. Executable overlays: file/env only. UI catalogs: read-only generated projections.

7. **Migration** — Shadow detectors vs Python on **code + span**; flip METAR/SPECI **R1–R8 by theme**; remove dual paths after flip.

8. **Non-goals** — Suppressions language; package merge; in-app detector editor; Schematron XPath re-authoring; remappable XSD; decode→lint emit.

## Consequences

- Conversion profiles gain explicit `tac_quality` / `iwxxm_output` policy references (ADR-038 amend).
- Registry stays code-stable; policy grows without inventing codes.
- National IWXXM rules stay as Schematron bundles (trust + pin fidelity).
- R1–R8 becomes the first large declarative detector program under F15 deepen.

## Amends

- **ADR-028:** Registry remains SoT for codes; detectors and policy are additional layers (not a YAML-only registry).
- **ADR-038:** `validation.tac` / `outputValidation` resolve to policy document ids loaded by package runtimes (loader authorized this cycle).
- **ADR-044/045:** Catalogs remain projections; executable overlays stay file/env; MatchPort does not merge packages.

## Remainder (2026-09-21, EV-validation-policy-remainders)

Milestones M1–M6 loaded policy and resolved ids. They did not apply the IWXXM policy inside validation, and they did not build MatchPort.

1. `validate_iwxxm` takes the resolved output policy id. Schematron issue codes that are assert ids and are not enabled are omitted. XSD, well-formed, and `SCHEMATRON_SKIPPED` always remain. Empty `select` is the full assert set, so the default annex3 report is unchanged.
2. The backend passes that id into validation. Public HTTP stays profile-id only.
3. MatchPort is a protocol on `tac-validate`. Strict mode applies only when the caller passes a port, including an empty one. An empty port makes every annex3 METAR theme detector emit `MISSING_DECODE_MATCH`. Omitting the port, including `/lint-tac`, keeps today's TAC scan. Other products scan TAC. A present match supplies the issue span. Decode packs still do not emit lint.

