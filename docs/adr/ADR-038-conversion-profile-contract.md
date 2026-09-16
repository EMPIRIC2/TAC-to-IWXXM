# ADR-038: ConversionProfile executable contract (spike #924)

> **Status**: Accepted (EV-924 / #924)  
> **Date**: 2026-09-03  
> **Deciders**: User (EV-924 evolve — contract accept, overlays defer)  
> **Related**: [ADR-013](ADR-013-tac2iwxxm-package-architecture.md), [ADR-036](ADR-036-semantic-vs-exchange-profiles.md), [ADR-030](ADR-030-dissemination-package-architecture.md)  
> **Issues**: [#924](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/924), [#922](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/922)  
> **Write-up**: session `reports/924-conversion-profile-contract.md` (EV-924)

## Context

Spike [#924](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/924) asks whether the conversion
profile should become an **executable deployment/conformance contract** (grammar, validation
rule-sets, mapper, output validation, optional dissemination defaults) including custom/operator
overlays ([#906](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/906) absorbed).

[ADR-036](ADR-036-semantic-vs-exchange-profiles.md) already split **semantic** and **exchange**
profile kinds and shipped nested HTTP wire fields. The monorepo implements behavior through:

- `tac2iwxxm.profile_registry` + emit plugins
- `tac-validate` product rules + ADR-028 issue registry
- `iwxxm-validate` for output validation
- `dissemination.exchange_registry` + packaging for exchange overlays
- `docs/domain/profiles/catalog.yaml` as machine index

Constraints:

- Fail-closed unknown profile ids
- No dissemination credentials in profile objects (ADR-021/029)
- No browser-uploaded unsigned schema bundles
- #924 is investigation-only — no runtime engine rewrite

## Decision

1. **Accept a normative ConversionProfile contract** as standing documentation. The contract
   **composes** ADR-036 semantic + exchange fields; it does **not** merge them into one wire enum.

2. **Implementation model (M5 / this spike):** behavior remains **code plugins + registries +
   catalog.yaml**. The contract is the **map**, not a new runtime loader.

3. **Contract field ownership**

   | Field group | Owner package / doc |
   |-------------|---------------------|
   | `id`, `appliesTo.products` | `docs/domain/profiles/catalog.yaml` |
   | `input.*`, `conversion.*` | `packages/tac2iwxxm` emit plugins |
   | `validation.tac` | `packages/tac-validate` + ADR-028 registry |
   | `validation.canonical` / staged pipeline | Deferred to #925 |
   | `outputValidation` | `packages/iwxxm-validate` + vendor pins |
   | `dissemination.exchangeProfile` | `packages/dissemination` (defaults only) |
   | `dissemination.defaultDestinations` | **Excluded** — BYOC memory-only |

4. **Custom / operator overlays (#906):** **Deferred** to #933 ConversionProfile editor evolve
   cycle. v1 trust model = **first-party catalog entries only**; unknown ids rejected.

5. **catalog.yaml schema v2 (Planned):** incrementally add contract fields already factual in
   repo (products, vendor_pins, implementation refs). No big-bang manifest migration in #924.

6. **OpenAPI:** keep ADR-036 nested `semantic_profile` / `exchange_profile` / `iwxxm_version` /
   `extensions`. Optional future shorthand `conversionProfile=` documented in api corpus only
   after #933 — not authorized by this ADR.

## Normative contract sketch

```yaml
ConversionProfile:
  id: US_FAA_NWS
  kind: semantic          # semantic | exchange (ADR-036)
  appliesTo:
    products: [METAR, SPECI, TAF, SIGMET, AIRMET]
  input:
    grammar: { implementation: tac2iwxxm/profiles/iwxxm_us }
    units: { policy: FAA_FMH1 }
  validation:
    tac: { registry: tac-validate, profile_emit_key: iwxxm_us }
  conversion:
    iwxxmVersion: independent   # HTTP field — not derived from id
    mapper: { emit_key: iwxxm_us }
    extensionSchemas: [IWXXM_US_3]
  outputValidation:
    engine: iwxxm-validate
  dissemination:              # optional defaults — not credentials
    exchangeProfile: GLOBAL_AFS
```

Exchange-only profiles (`GLOBAL_AFS`, …) use `kind: exchange` and omit conversion/input blocks.

## Alternatives considered

| # | Alternative | Why rejected / deferred |
|---|-------------|-------------------------|
| A | Runtime profile loader executing declarative RuleSet[] now | Premature vs #925; code plugins already work |
| B | Browser operator pack upload | Trust/SSRF — reject |
| C | Reject contract — keep ad hoc plugins only | Loses #922 platform narrative; catalog already partial contract |
| D | **Contract doc + deferred loader** | **Accepted** |

## Consequences

### Positive

- #924 acceptance criteria met without risky engine rewrite
- Clear field ownership for #925 / #933 follow-ons
- ADR-036 remains authoritative; ADR-038 extends without contradiction

### Negative / follow-ups

- Contract fields not yet machine-validated against runtime — #933 or #925 may add loader
- `appliesTo.stations` / state filters unimplemented — document as future

### Amend (EV-933 / #933 — Accepted)

Operator-scoped **signed overlays** are persisted on product Postgres (`DATABASE_URL`) with
JWT ownership (`user_id` = Auth `sub`). Trust model:

1. Client submits overlay body JSON over JWT (no client-supplied signature).
2. Server canonicalizes the body, computes **HMAC-SHA256** with
   `PROFILE_OVERLAY_HMAC_SECRET` over `user_id:base_profile_id:canonical_json`, and stores
   the hex digest.
3. Reads and convert apply **re-verify** the HMAC; missing or mismatched signature → 400.
4. Convert accepts optional multipart `overlay_id`. When set, Bearer JWT is required and
   ownership (or `shared=true`) is enforced; guests without `overlay_id` keep public convert.
5. First-party catalog entries remain the default trust root. Unsigned browser-uploaded
   schema/rule packs stay **rejected**. Overlay bodies must not carry credentials or
   destination URIs (ADR-021 / ADR-029).

See Context: conversion-profile-editor-933 (archived — see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`; not a CORPUS design gate).

### Amend (EV-080 / #1146 — Accepted)

**Parameterizable conversion templates** are the **default Conversion rule object** for
operator-authored TAC→IWXXM mapping (slot-builder-first; compiled pattern secondary).
This amend authorizes **runtime-applicable** composable template objects on the existing
IR / plugin pipeline — it does **not** authorize N per-country converter engines or
browser-uploaded unsigned schema bundles.

1. **Object model:** A template is an ordered list of typed slots (digits, enum, unit,
   literal, station, time, …) with optional flags, optional literal prefixes, and mapping
   to an IWXXM block/path (including ns, nil, cardinality, choice, uom, nesting; Schematron
   hooks may appear in the model even when UI v1 does not expose every control).
2. **Pass-through:** Typed captures carry numbers/enums through — not one rule per literal
   value.
3. **Authoring:** Same builder for first-party built-ins and custom templates. Trust v1:
   JWT owner CRUD for custom; first-party **view + fork** only (no mutate of builtin
   source). Apply custom on convert when the caller is entitled; fail-closed unknown
   template/profile ids.
4. **UX contract:** No raw regex as the default authoring path; advanced compiled/RE2
   remains secondary. Operator UI must present a clear TAC → template → IWXXM bridge
   (highlighted span, captures, resulting XML block), comments under TAC, and inline
   conversion preview. Slot reorder supports drag-and-drop with keyboard/↑↓ fallback.
5. **Pipeline:** Templates compose with ADR-036 semantic profiles and existing
   `tac2iwxxm` emit — overlays on one IR pipeline. Dissemination profile/rules still apply
   only on Disseminate / Convert & Send (not Convert-only). Destination credentials remain
   memory-only (ADR-021 / ADR-029 / ADR-030).
6. **Phase-1 ship set (EV-080):** conversion templates + bridge UI only. Libraries for TAC
   validation / IWXXM validation / dissemination / decoding, rich match completeness, and
   triple-preset deepen beyond EV-1051 refs are **out of phase-1** unless a later evolve
   expands scope.
7. **Decoding:** Long-term Decoding library stays **separate** and may reuse the F9
   `decode_tac` catalog; not required to ship in EV-080 phase-1.

Product / journeys / tests: [Corpus: product §F7.w] EV-080; UJ-072e; TC-EV080-*.
Session: `EV-080-param-conversion-templates`.

### Amend (EV-conversion-profile-ux-libraries — Accepted)

Extends the Profiles authoring surface beyond EV-080 phase-1 into a **Profile Builder
platform** while keeping Conversion tokens as the hero path.

1. **Shell:** Guided assembly wizard + Libraries hub (Conversion / TAC validation / IWXXM
   validation / Dissemination). Operator UI uses human-readable names; machine ids are not
   shown in primary chrome (copy-id in overflow). DnD for ordered lists.
2. **Token modes:** Each conversion token supports **Convert | Decode-only | Skip** with
   optional gloss. Skip must appear in preview (no silent drop). Parametric typed captures
   remain normative.
3. **Validation library:** Hybrid authoring (recipes + guided + Advanced regex). Issue /
   level / message; attached-profile chips.
4. **Dissemination library:** Ordered post-process transform steps + non-secret sink
   defaults; ADR-021/029 credentials unchanged. Discoverability may ship in a later phase.
5. **Selection:** Independent concern pickers and bundle presets spanning Conversion +
   Validation + Dissemination (optional decode).
6. **Decoding library:** Separate F9 deepen; catalogued NL definitions; not required for
   Phase A ship.
7. **Phase A ship set:** Output filename placement on Convert; Profile creator simplify;
   conversion token/skip/preview hero. Libraries tabs + full validation/dissem authoring =
   Phase B/C.

Product / journeys / tests: [Corpus: product §F7.w] EVCPU; UJ-072f; TC-EVCPU-*.
Session: `EV-conversion-profile-ux-libraries`.

### Amend (EV-bridge-ux-canvas-align — Accepted)

**Five Libraries** replace the monolithic semantic-profile Convert control and the Profile
builder chrome for Semantic presets / Rule packs / Dissemination templates / Signed overlays.

1. **Libraries:** Conversion · TAC validation · IWXXM validation · Dissemination · Decoding.
   Profile builder exposes **five sub-tabs**. Convert exposes Product + IWXXM version + five
   library pickers (no Exchange / preset / overlay / `semantic_profile` controls after cutover).
2. **Hard cut:** All existing national semantic profiles are split into five first-party
   default assets each and pre-loaded. Convert multipart **must not** accept `semantic_profile`
   after cutover (fail closed / remove field per OpenAPI). No one-release alias window.
3. **Fork-on-edit:** Mutating a first-party default creates an owner-scoped fork; builtins are
   immutable and non-deletable. User forks are deletable by owner.
4. **Mapping bridge:** TAC report → Template match → IWXXM block on Convert and Profile;
   Conversion library hosts the Template block builder (DnD + keyboard/↑↓).
5. **Dissemination library:** Annotations + ordered post-IWXXM transforms (envelope,
   topic/filename, checksum, bulletin re-wrap). Apply only on Disseminate / Convert & Send.
   Destination credentials remain memory-only (ADR-021 / ADR-029 / ADR-030).
6. **Decoding library:** Seeded from F9 / `decode_tac` catalog; fifth Convert picker.
7. **Dropped primary UI:** Signed overlays, Dissemination templates, Semantic preset / Rule
   pack forms. Retire or hide corresponding APIs in the same Build unless tech-plan documents
   a temporary read-only shim (not for Convert selection).
8. **Rule association (normative):** Every TAC group that emits an IWXXM block must match an
   associated Conversion library rule/template. Unmatched groups fail closed (no silent
   engine-only emit). Bridge UI surfaces the matched rule id/name.

Product / journeys / tests: [Corpus: product §F7.w] EV-bridge; UJ-072g; TC-EVBRIDGE-*.
Session: `EV-bridge-ux-canvas-align`.

### Amend (EV-profile-builder-yaml-libraries / #1196 — Accepted)

Extends Five Libraries into a **YAML-backed, DnD Profile Builder** with optional Convert
export metadata. Does not reopen the EV-bridge hard cut.

1. **Authoring model:** Each custom library asset is a **YAML document** (one YAML per asset)
   with bidirectional live sync to a guided UI. Invalid YAML locks the guided UI until fixed.
   Save validates against a strict schema (JSON Schema / msgspec). Built-in assets remain
   read-only; operators create customs (including fork-from-national).
2. **UI chrome:** Guided assembly / glossary / workflow / examples prose are **removed**.
   Hover tooltips cover every Profile Builder control. Catalog inspector sits **directly under**
   the active library editor and follows the active library tab.
3. **DnD structure:** Top-level **blocks** correspond to **IWXXM schema blocks** from WMO
   (and national extension blocks associated with country profiles). **Cards** are individual
   rules inside a block. Create paths: starter templates, duplicate mined block, import YAML.
4. **Libraries:** Conversion, TAC validation, IWXXM validation, Dissemination, and Decoding
   are all fully customizable. IWXXM validation supports mined Schematron assert toggles and
   custom XPath / regex-on-XML. Dissemination YAML/transforms remain pattern-only — **never**
   credentials or destination URIs (ADR-021 / ADR-029 / ADR-030).
5. **Defaults:** ICAO/WMO Annex 3 baseline selections for all five library pickers on Profile
   Builder and Convert, kept in sync.
6. **Lifecycle:** Phase A ships Draft-only customs + UX shell + export sidecar. Phase B ships
   comprehensive mined catalogs. Phase C ships live regex validation (compile + capture
   summary; Warn vs Fail), Activate (requires zero Fail; Draft may have Fail), and runtime
   binding of activated customs via existing Convert library-id selection.
7. **Export metadata (Phase A):** Optional Convert download / ZIP / single-result toggle
   “Include conversion metadata” writes a sidecar `*.meta.json` (not embedded in IWXXM).
   Default checklist includes all content groups (library ids; YAML snapshots/hashes;
   product/IWXXM version/timestamp/operator identity; lint/validation summary; TAC
   fingerprint; mapping-bridge summary). Opt-in default off; remember last choice per
   operator. Single-file downloads use a ZIP of two. Guests omit identity fields.
   Draft customs are not selectable on Convert until Activated (Phase C).
   Never include credentials, destination URIs, or auth tokens.
8. **Trust / beta:** Signed-in required for Profile Builder. Beta badge on Profile builder and
   export-metadata toggle (ADR-043). No planning vocabulary in operator copy (EV-048).

Product / journeys / tests: [Corpus: product §F7.w] EVPYL; UJ-072h-*; TC-EVPYL-*.
Session: `EV-profile-builder-yaml-libraries`. Issue: #1196.

### Amend — EV-profile-builder-mine-residuals (#1198+#1199)

Phase B residual mining (no Profile Builder UX change):

1. **IWXXM validation catalog:** Miner may include **latest** WMO foundation Schematron
   (`metce` / `opm` / `saf` / `collect`) in addition to core `iwxxm.sch`, tagging each assert
   with an `authority` field. Core assert ids remain stable. OpenGIS SCH under
   `externalSchema` is out of scope until a later cycle.
2. **Conversion national blocks:** AU/BR/HK/IN/JP/KR/NZ/UK blocks are mined only when
   corresponding read-only vendor pins exist (M6 sync). Until then, miners may document
   expected discovery paths and skip missing dirs; do not invent national XSD trees.
3. **Tests:** TC-EVPYL-MINE-006..008. Session:
   `EV-profile-builder-mine-residuals`. Issues: #1198, #1199.

## References

- Context: conversion-profile-contract-924 (archived — see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`; not a CORPUS design gate)
- Context: conversion-profile-editor-933 (archived — see session-store `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/` or orphan branch `docs-archive`; not a CORPUS design gate)
- [ADR-037](ADR-037-platform-logical-layers.md) Profiles layer
- EV-924 session report `924-conversion-profile-contract.md`
- EV-933 / #933 F7.w / UJ-072
