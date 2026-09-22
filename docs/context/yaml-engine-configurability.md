# Context — YAML / overlay engine configurability

**Session:** `EV-yaml-engine-configurability`  
**Ticket:** [#1224](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1224)  
**Baseline:** `stage` (post #1223 / #1221)  
**Gate:** documenting → implementing **closed**

[Corpus: product §F2/F6/F9/F15] [Corpus: adr/ADR-044] [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: tech-spec] [Corpus: tests]

## Problem

Operators and SDK users need **clear, fail-closed YAML/file-env configurability** for:

1. TAC decoding (`tac-decoding`)
2. TAC validation (`tac-validate`)
3. IWXXM validation (`iwxxm-validate`)
4. TAC → IWXXM conversion (`tac2iwxxm` + backend wiring)

Today the **engines exist** with uneven declarative surfaces. It is easy to over-claim “full YAML coverage” while convert emit and many TAC detectors remain Python, mined catalogs under `tac2iwxxm/data/` are **projections** (not executors), and package READMEs under-document overlays/`extends`.

## Intent (locked intake)

**Honesty + usability first** (not a full emit-as-YAML rewrite):

- Publish a product × engine matrix (full | partial | stub | N/A)
- Shared overlay cookbook + per-package example templates
- Overlay preflight / fail-closed checks
- README / PyPI / `config-spec` deployer docs
- Backend: document server-resolved policies; **no** client YAML injection
- Optional high-value YAML deepen only where the matrix justifies it

**Users:** SDK / PyPI embedders + deployers (env overlay dirs). In-app catalogs stay read-only (ADR-044).

## Current capability (as-is)

| Engine | Executable YAML | Overlay env | Backend |
|--------|-----------------|-------------|---------|
| Decode | Product packs (`data/packs/*.yaml`, ~11) + glossary | `TAC_DECODING_PACK_DIR`, `TAC_DECODING_GLOSSARY_PATH` | `/decode-tac`; airport names via Python resolver hook (#724) |
| TAC validate | Quality policies + some detector YAML (~7 detector files) | `TAC_VALIDATE_POLICY_DIR`, `TAC_VALIDATE_DETECTOR_DIR`, `TAC_VALIDATE_DETECTOR_MODE` | Profile → policy bind (ADR-046) |
| IWXXM validate | Output policies (assert select/ignore) over vendor XSD/SCH | `IWXXM_VALIDATE_POLICY_DIR` | Server-resolved `output_policy_id` |
| Convert | Profile→policy binding; pack IR path (`TAC2IWXXM_CONVERT_IR_SOURCE`) | `TAC2IWXXM_PROFILE_DIR` | HTTP profile/semantic profile only |

Shared extension header: `id`, `profiles`, `extends` ([Corpus: adr/ADR-045] / EV-yaml-extension-header). Env inventory: [Corpus: tech-spec] `docs/config-spec.md` §F24/F9 deepen.

## Gaps → verify angles

| ID | Gap | Verify angle | Recommendation |
|----|-----|--------------|----------------|
| G1 | Convert emit mostly Python; mined YAML = catalog | `product-engine-matrix` (convert column) | Keep emit in Python; document pack-IR vs plugin; no emit-YAML rewrite this cycle |
| G2 | TAC detectors incomplete as YAML | `product-engine-matrix` + detector parity note | Honesty matrix; optional METAR/SPECI deepen only |
| G3 | README/PyPI under-document overlays | `pypi-readme-overlay-smoke` | Cookbook + `examples/overlays/` per package |
| G4 | No overlay preflight UX | `overlay-fail-closed` | CLI/script fails closed on bad `extends` / unknown ids |
| G5 | Dual glossary / catalog copies | `glossary-single-home` | SoT = `tac-decoding`; shim drift note |
| G6 | “Full coverage” ambiguous | `product-engine-matrix` | Publish CORPUS-cited matrix |
| G7 | HTTP vs library parity | `api-no-policy-injection` | Keep wire clean; deployer mount docs |

## Out of scope

- Profile Builder / in-app YAML editor (ADR-044)
- Client-supplied policy/pack YAML on HTTP
- Replacing vendor Schematron with hand XPath
- #1222 exchange packaging / marketplace

## Journeys / must-not-break

- Convert / lint / decode / validate HTTP contracts (no new policy body fields)
- Operator-visible copy free of planning vocabulary
- Fail-closed overlay merge (bad overlay must not silently disable builtins)

## UI / connectivity

**None** for this slice unless operator copy strings change (then H4–H5). No Profile Builder work.

## Anticipated Build (deferred — gate closed)

- Docs + templates + matrix tests
- Preflight script/CLI in packages or `scripts/`
- README updates; optional detector YAML only if requirements lock it
- No FE feature work by default

## Related

- #1224 (this ticket) · ADR-044/045/046 · #1210 · #1216 · #1221 (closed on stage)
- Session gap brief: `~/.cursor/workflow/…/EV-yaml-engine-configurability/reports/gap-brief-draft.md`
