# ADR-045: Shared TAC pack engine for decode and convert

**Status:** Accepted (requirements lock — EV-configurable-tac-decode-packs, 2026-09-19)
**Date:** 2026-09-19
**Corpus:** [Corpus: product §F6] [Corpus: product §F9] [Corpus: product §F23] [Corpus: product §F28] [Corpus: product §F32] [Corpus: system-spec] [Corpus: api] [Corpus: adr/ADR-032] [Corpus: adr/ADR-044]

## Context

Natural-language decode already lives in `packages/tac-decoding`, but product structure is still hardcoded Python. Convert parses the same TAC again in `packages/tac2iwxxm/products/`. The two paths drift. Whitespace-spanning groups (for example fractional statute miles) become residuals. Label-field products (VAA, TCA, SWXA, VONA) need a different layout from METAR/TAF token streams. SIGMET volcanic-ash and tropical-cyclone forms need their own packs without a new HTTP product enum.

## Decision

1. **One engine, many packs.** `tac-decoding` owns a grammar engine. Product behavior lives in YAML/JSON packs. The engine is not a separate decoder per product.
2. **Two projections from one match.** Each successful match can emit a natural-language explanation and a convert IR slot. `tac2iwxxm` consumes the IR projection. Decode does not import `tac2iwxxm`.
3. **Layouts.** `token_stream` for METAR, SPECI, TAF, SIGMET, and AIRMET. `label_fields` for VAA, TCA, SWXA, and VONA. Commas and hyphens are delimiters inside values, not a separate file type. COLLECT is a third path: decode contained TAC when present; otherwise walk XML fields. No IWXXM encoder in `tac-decoding`.
4. **Products.** Core packs: METAR/SPECI, TAF, ordinary SIGMET, VA SIGMET, TC SIGMET, AIRMET, VAA, TCA, SWXA, VONA. WAFS and QVACI are stub packs (whole-body residual) only.
5. **Wire.** `product=sigmet` stays the only SIGMET HTTP value. The package still selects the IWXXM root from TAC / abbreviated heading. `POST /api/v1/decode-tac` response fields do not change this cycle.
6. **Legacy stays.** Pack matches run in shadow beside the existing parsers. Do not delete `products/*.py`, validation, or the version comparisons. Profiles already choose the pin: Annex 3 uses `2023-1` and `2025-2`; `ca_eccc` uses `3.0.0`. A pack does not pick a pin. The caller passes `iwxxm_version` and `profile`; the same TAC explains the same way on every pin. XML emit and golden compares stay on the existing profile path, including every pin that already has the example. `tac2iwxxm.decode` and `glossary` shims stay.
7. **Goldens.** Use existing `vendor/schemas` examples and in-repo fixtures. Do not fetch or commit new WMO copies.
8. **Trust.** Pack overlays are file or environment only (no in-app editor, ADR-044). Regex and repeat budgets fail closed. Explanation locale hook is English-only this cycle.
9. **Non-goals.** Do not emit `tac-validate` issues. Do not mutate TAC. Do not add explanation languages. Do not treat the 2026-09 research note as a path authority (VONA is an IWXXM product in this repo).

## Consequences

- Convert and decode can no longer diverge on a product once that product’s legacy parser is deleted.
- Bulletin split becomes an injected port so decode does not depend on `tac2iwxxm`.
- A bad overlay must not silently disable the builtin pack.
- Vendor XML equality is the delete gate, not a softer semantic compare.

## Tech locks (tech-plan, 2026-09-19)

- **Overlay env.** `TAC_DECODING_PACK_DIR` is a directory of YAML/JSON packs. Unset means built-in packs only. It does not replace `TAC_DECODING_GLOSSARY_PATH`.
- **Match budget.** 10,000 matcher steps per report. Exceeding the budget fails closed. Pack rule ids are not exported on the Decoding catalog this cycle.
- **Versions.** Keep every pin a profile already compares (`2023-1`, `2025-2`, `3.0.0`, and any later profile pin). Do not fetch missing older copies. Shadow XML must stay byte-identical on each pin that already has the example. Parsers and validation stay.
- **Deploy.** No new dependency and no required Render secret. PyYAML is already allowed.

## Amends

- **ADR-032:** glossary remains data, but structure (not only token meanings) is pack data.
- **ADR-044:** `tac-decoding` remains the decode home; this cycle also makes it the convert IR source in shadow. Shims, legacy parsers, and the multi-pin validation compares stay. A later cycle would have to reopen deletion.

## Amend — EV-pack-ir-convert-wire (2026-09-20)

Deepen only. Does not reopen mass deletion of `products/*.py`.

1. **Span IR boundary.** `tac-decoding.project_ir` stays span/residual projection. Mapping spans → legacy convert slots and IWXXM emit live only in `tac2iwxxm`.
2. **Pack fill.** Builtin METAR/SPECI packs gain real rules. Coverage bar: vendor peers `metar-A3-1` and `speci-A3-2` on every pin that already has the example. Out of bar: `metar-NIL-collect`, `metar-translation-failed`.
3. **Default flip (not delete).** When pack-IR emit XML is byte-identical to legacy on that bar, METAR/SPECI convert **default** may switch to the pack-IR path mid-cycle. Legacy parsers remain in tree until a later evolve reopens the delete gate.
4. **Packages stay separate.** Do not merge `tac-decoding` and `tac2iwxxm`.
5. **Deploy.** Still no required Render secret. Optional override env (if any) is documented in config-spec and is not required for production.

## Amend — EV-pack-fill-delete-gate (2026-09-20)

Deepen #1214. Reopens **selective** deletion only.

1. **Fill + wire.** Remaining core packs (TAF, ordinary/VA/TC SIGMET, AIRMET, VAA, TCA, SWXA, VONA) gain real rules and pack-IR emit. METAR/SPECI stay.
2. **Stricter coverage bar.** In-bar peers include primary Annex examples **plus** `sigmet-A6-1b-CNL`, `sigmet-multi-location-VA`, and SWXA `_alternate` XML peers on pins where they exist. Out of bar: NIL-collect / translation-failed families unless later deepen.
3. **Mapper independence.** `pack_ir_map` (and pack emit) must not import `products/*.py` for any product whose legacy parser is deleted.
4. **Selective delete-gate.** Vendor XML byte-identical on every existing pin for in-bar peers → may delete that product’s legacy parser. Shared files (`metar_speci.py`, `sigmet_airmet.py`, `vaa_tca.py`) are **all-or-nothing**: delete the file only when every product it owns passes; otherwise keep the file and remove only safe dead paths. **Zero deletes this cycle is acceptable** if siblings fail — still ship pack fill.
5. **SWXA alternates.** Where a pin has both primary and `_alternate` vendor XML, pack-IR emit must match **both** before flip/delete for SWXA.
6. **METAR/SPECI.** May delete `metar_speci.py` in this cycle if goldens still pass after mapper independence.
7. **Packages stay separate.** WAFS/QVACI remain stubs. No HTTP wire change. No required Render secret.

## Amend — EV-yaml-extension-header (2026-09-21)

Deepen only. Does not merge packages and does not add an in-app editor.

1. **Four homes.** `tac-decoding`, `tac-validate`, `iwxxm-validate`, and `tac2iwxxm` stay separate publishable packages. The backend integrates them. They do not import each other. Decode packs still do not emit lint.
2. **Header.** Extension YAML in each package uses `id`, `profiles`, and `extends`. A builtin may omit `profiles` (every profile) and omits `extends`. An overlay must set `extends` to exactly one builtin id and must list `profiles`. A missing base fails closed and the builtin stays in force.
3. **Merge.** An overlay layers on that builtin for those profiles. The same payload id replaces that one entry. A new id is added. Other builtin entries stay.
4. **Key.** The conversion profile id already on the wire is the only extension key. No new HTTP field.
5. **Trust.** Overlays stay file or environment. No in-app editor.
