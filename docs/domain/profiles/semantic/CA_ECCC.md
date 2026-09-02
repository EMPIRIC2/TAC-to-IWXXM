# CA_ECCC — Canada semantic overlay (P1)

> **Profile id**: `CA_ECCC` · **Kind**: semantic · **Priority**: P1 · **Status**: implemented (EV-064–067 / #916, #1039 P1)  
> **Implementation**: [#916](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/916), [#1039](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1039)  
> **Catalog row**: [`catalog.yaml`](../catalog.yaml) · **ADR**: [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)

Environment and Climate Change Canada (ECCC / MSC) national semantic overlay: MANOBS
surface observations, MANAIR aviation forecasts, and Canadian IWXXM extension schemas.

## Owns (target)

| Area | Scope |
|------|-------|
| TAC parse / normalize | MANOBS METAR/SPECI/**LWIS**/**SAWR**; MANAIR TAF/AIRMET |
| IWXXM extensions | `iwxxm-ca.xsd`, `common-ca.xsd`, `taf-ca.xsd`, `airmet-ca.xsd`, **`metar-speci-ca.xsd`** |
| Products | METAR, SPECI, TAF, AIRMET (convert+validate); SIGMET (exchange emit EV-076 / validate-first ops EV-074); VAA validate-first TAC (EV-077 / `D-EV074-vaa-waiver-tac`) |

## METAR-family national report variants

Canada defines **four** MANOBS surface-report TAC leads. Only two are ICAO-standard; LWIS and
SAWR are **Canadian national products** with their own IWXXM substitution-group roots in
`metar-speci-ca.xsd`.

| TAC lead | What it is | API `product` | IWXXM root | Fixture `rule_id` |
|----------|------------|---------------|------------|-------------------|
| `METAR` | ICAO routine aerodrome report | `METAR` | `iwxxm:METAR` | `CA.METAR.*` |
| `SPECI` | ICAO special report | `SPECI` | `iwxxm:SPECI` | `CA.SPECI.*` |
| `LWIS` | **L**imited **W**eather **I**nformation **S**ystem — sparse AUTO obs (MANOBS 8 §11.3) | `METAR` | **`iwxxm-ca:LWIS`** | `CA.METAR.LWIS` |
| `SAWR` | **S**urface **A**viation **W**eather **R**eport — Canadian surface report product | `METAR` | **`iwxxm-ca:SAWR`** | `CA.METAR.SAWR` |

### Why LWIS/SAWR use `product=METAR` in the API

Per [ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md), three layers stay separate:

1. **`semanticProfile`** (`CA_ECCC`) — national parse/emit overlay (MANOBS + `*-ca.xsd`).
2. **`product`** — converter dispatch family (`METAR` \| `SPECI` \| `TAF` \| …). LWIS/SAWR are
   not global product enums; they share the METAR-family parser and fixture tree.
3. **`ca_iwxxm_root`** (IR) — TAC lead preserved from bulletin; selects IWXXM root element and
   observing-system vocabulary at emit time.

So LWIS/SAWR are **not** “METAR with a different label” — they are distinct MANOBS report types
and distinct `metar-speci-ca.xsd` roots. The API routes them through `product=METAR` because
they are aerodrome **surface observation** reports, not because they encode as `iwxxm:METAR`.

**LWIS vs SAWR vs METAR (behavioural):**

| | METAR | LWIS | SAWR |
|---|-------|------|------|
| TAC prefix | `METAR` | `LWIS` | `SAWR` |
| Typical content | Full Annex 3 body | Wind + temp/dew + altimeter only | Full body + Canadian RMK |
| Visibility / clouds | Yes (when reported) | **Omitted** (`ca_minimal_observation`) | Yes |
| IWXXM namespace | Core `iwxxm` | National `iwxxm-ca` | National `iwxxm-ca` |
| `observingSystemType` | AWOS when `AUTO` | **LWIS** code-ca href | **SAWR** code-ca href |

### `iwxxm-ca:Addendum` elements (EV-066 / EV-067)

Structured MANOBS remarks and metadata map to `metar-speci-ca.xsd` Addendum children (not
free-text-only RMK). Catalogued in [`catalog.yaml`](../catalog.yaml) under
`metar_speci_ca_addendum`.

## Authoritative sources

| Source | Access | Proves |
|--------|--------|--------|
| [MANOBS](https://www.canada.ca/en/environment-climate-change/services/weather-manuals-documentation/manobs-surface-observations.html) | public | Canadian surface observation standards |
| [MANAIR 8th Ed.](https://www.canada.ca/en/environment-climate-change/services/weather-manuals-documentation/manair-standards-procedures-aviation-weather-forecasts-8th-ed.html) | public | Canadian aviation forecast standards |
| [MSC IWXXM-CA XSD](https://dd.weather.gc.ca/today/aviation/iwxxm/schema/) | public | National extension schema tree |
| [MSC aviation IWXXM datamart](https://eccc-msc.github.io/open-data/msc-data/aviation/iwxxm/readme_aviation-iwxxm-datamart_fr/) | public | Operational IWXXM 3.0.0 + CA extensions |

## Mining notes (transitory)

- [`manobs-manair-ca-mining-notes.md`](../../mining/manobs-manair-ca-mining-notes.md) — MANOBS/MANAIR TAC rules
- [`eccc-iwxxm-ca-mining-notes.md`](../../mining/eccc-iwxxm-ca-mining-notes.md) — IWXXM 3.0.0 + `*-ca.xsd` + code-ca + datamart

## IWXXM version line

MSC operational practice pins **IWXXM 3.0.0** core (`http://icao.int/iwxxm/3.0`) plus CA
extensions — independent of the app default **2025-2** SoT line ([ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md)).

## Implementation

| Component | Location |
|-----------|----------|
| Registry | `packages/tac2iwxxm/src/tac2iwxxm/profile_registry.py` |
| Parser (TAC leads) | `packages/tac2iwxxm/src/tac2iwxxm/products/metar_speci.py` — `ca_iwxxm_root` IR |
| Emitter | `packages/tac2iwxxm/src/tac2iwxxm/profiles/ca_eccc.py` — root tag + Addendum |
| Golden fixtures | `packages/tac2iwxxm/tests/fixtures/profiles/CA_ECCC/` |
| Validate profile | `packages/iwxxm-validate` — layered `ca_eccc` stack (EV-068 M3–M5; API `extensions: [IWXXM_CA]`) |
| Vendor pin | `vendor/manifest.json` → `iwxxm-ca` 3.0 + IWXXM `3.0.0` core |

## Gaps

### EV-068 delivered (#1027 + #1035)

- Layered `ca_eccc` validation: WMO 3.0.0 XSD+SCH + product `*-ca.xsd` (TC-EV068-002/003)
- Profile-pinned 3.0.0 manifest (`vendor/manifest.json`; TC-EV068-001)
- API/CLI `extensions: [IWXXM_CA]` wire + `package_stages` on `/validate` (TC-EV068-004)
- EV-067 golden XSD gate (`metar_lwis`, `metar_sawr`, `metar_rmk_icing`) — **TC-EV068-003**

### EV-069 delivered (#1033 + #1032 + TAF gate)

- Layer 5 `code_ca` vocabulary membership (offline curated registry; TC-EV069-003)
- Layer 6 `exchange` packaging checks (operational attrs + optional AHL cross-check)
- TAF `taf-ca.xsd` NCLWS extension probe (direct global element validation; TC-EV069-002)

### EV-070 delivered (#1041 — convert deepen)

- TAF: `present_and_forecast_weather/IC` via `iwxxm-ca:weather`; `TAF AMD` → `reportStatus=AMENDMENT`
- AIRMET: GFA structured `surfaceVisibility` / `cloudBase` / `surfaceWindSpeed` for `SFC_VIS_and_BKN_CLD`
- Validate: `ca_xsd` probes `airmet-ca` global elements directly (not LWIS shell)
- Goldens: `taf_ic_weather`, `taf_amd`, `airmet_gfa_sfc_vis` + TC-EV070-001..006

### EV-071 M1 delivered (#1038 — lint pack)

- **M1 (#1038):** Full `ca_eccc` tac-validate rule pack — 12 promoted MANOBS/MANAIR rules with
  fixtures, profile isolation vs `US_FAA_NWS`, lint catalog + quality matrix rows (TC-EV071-001..004)

### EV-071 M2 delivered (#1032 + #1040 — exchange output METAR)

- **M2 (#1032):** MSC METAR filename + WMO header (`A_LACN`); `tac2iwxxm.exchange_output` contract;
  layer-6 validate extend (filename + translation centre); API `metadata.output_spec` (TC-EV071-005..009)
- **M2 (#1040):** Profile-gated translation centre metadata on CA_ECCC convert (env-configurable)

### EV-071 deferred (follow-on)

- SPECI/TAF/AIRMET exchange output filename slice; full COLLECT envelope

### EV-072 M1 delivered (#1032 residual — exchange aerodrome products)

- **M1:** SPECI (`A_LPCN`), TAF (`A_LTCN`), AIRMET (`A_LWCN`) exchange output wire +
  layer-6 validate + API `output_spec`; catalog `ev072_slice` (TC-EV072-001..006)

### EV-072 M2 delivered (#1036 — ops corpus)

- **M2:** MSC datamart ops fixture corpus — pin-date harvest script, `ops_manifest.json`,
  ≥5 METAR + ≥2 each SPECI/TAF/AIRMET `wmoReference` tier; layer-6 packaging checks
  (TC-EV072-007..010)
- **Note:** METAR/SPECI IWXXM not published on MSC datamart at pin_date 2026-08-24;
  encoder-reference fixtures with documented waiver; TAF/AIRMET from live COLLECT envelopes

### EV-072 deferred (follow-on)

- **EV-073:** full COLLECT envelope packaging + #1042 profile/extension wiring

### EV-073 M1 complete (#1032 residual — COLLECT envelope)

- **M1:** `wrap_ca_eccc_collect` + convert `exchange_output` hook; MSC `bulletinIdentifier`;
  ops-fixture shell parity (TC-EV073-001..005) — **implemented** EV-073

### EV-073 M2 complete (#1042 — profile + extension wiring)

- **M2:** FE auto-wire `IWXXM_CA` when `CA_ECCC` selected; profile metadata surfacing;
  fail-closed missing vendor pin; E2E convert+validate (TC-EV073-006..009) — **implemented** EV-073

Reusable artifact per [#1044](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1044) playbook §5 + §8.

### EV-074 delivered (#1043 — SIGMET validate-first ops)

- **M1:** ≥2 SIGMET ops IWXXM from MSC datamart (`czeg`, `czqm`); `sigmet_kind` in `ops_manifest.json`
- **M2:** Layered validate — WMO 3.0.0 XSD+SCH; `ca_xsd` / exchange skipped as not-applicable for SIGMET/VAA
- **M3:** COLLECT unwrap for SIGMET / VA SIGMET / TC SIGMET / VAA roots
- **Deferred:** VAA ops harvest — datamart `vaa/` absent; **EV-077:** Montreal VAAC TAC validate-first (`D-EV074-vaa-waiver-tac`, 1 live at pin; target ≥2)
- Tests: TC-EV074-001..010

### EV-076 delivered (#1061 — SIGMET exchange output emit)

- **M1:** SIGMET MSC filename + WMO header (`A_LSCN` / VA `A_LVCN` / TC `A_LYCN` via `sigmet_kind`); ops output spec from datamart filename
- **M2:** Layer-6 exchange packaging on SIGMET ops fixtures; catalog `ev076_slice: [SIGMET]`
- **Deferred:** VAA exchange emit — inherits `D-EV074-vaa-follow`
- Tests: TC-EV1061-001..004

### EV-077 delivered (ops corpus deepen + VAAC TAC VAA)

- **M1:** +2 AIRMET ops fixtures (`czwg`, `czeg` GFA SFC_VIS); manifest pin 2026-08-24
- **M2:** Montreal VAAC TAC harvest (`harvest_ca_eccc_vaac_tac.py`); 1 live FVCN at pin (target ≥2)
- **Deferred:** VAA exchange emit — inherits `D-EV074-vaa-follow` (datamart `vaa/` absent)
- Tests: TC-EV074-005, TC-EV074-011

### EV-078 closeout (#916 P1 audit)

- **Verified:** #916 P1 build AC met on `stage` — EV-064..077 delivered; SIGMET exchange emit (#1061) closed
- **Waived:** VAA exchange *emit* — datamart `vaa/` HTTP 404 at probe 2026-08-24; follow `D-EV074-vaa-follow`
- **Residual:** Re-harvest VAAC TAC when 31-day index publishes ≥2 bulletins
- Docs aligned: `feature-list.md`, `COVERAGE_MATRIX.md`, `test-plan.md` §EV-078

### EV-098 deepen (mining — in progress)

- **Issues:** [#1028](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1028)–[#1031](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1031)
- **Path:** deep-research-domain-handoff (EV-097) → mine-domain-sources after gate C
- **Targets:** datamart triage; MSC doc PDFs; MANOBS P0 TAC rules + fixtures; MANAIR TAF/AIRMET/GFA
- **Decisions:** [ev-098-ca-eccc-mining.md](../../../decisions/ev-098-ca-eccc-mining.md)
- **Tests:** TC-EV098-001..005

### EV-075 closeout (#1032 umbrella audit)

- **Verified:** #1032 GitHub close correct — aerodrome exchange output (EV-071..072), COLLECT (EV-073), ops corpus (#1036), translation metadata (#1040) met on `stage`
- **Waived:** SIGMET/VAA exchange *emit* — remains validate-first; follow-on [#1061](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1061) (split from #1032)
- **Waived:** VAA ops IWXXM harvest — datamart `vaa/` absent; **EV-077** Montreal VAAC TAC validate-first instead
- Docs aligned: `catalog.yaml`, `COVERAGE_MATRIX.md`, `test-plan.md` §EV-075

### Out of scope (EV-068 / backlog)

- Extended Canadian-only remark flags (CONTRAILS/AURORA) in structured Addendum
- `AerodromeVariableRVR` / `ObservedLightning` (P2 / #1039)
- LWIS/SAWR/density/icing tac-validate codes beyond EV-071 M1 slice (if not promoted)
- `#1050` `reportVariant` wire / UI (#1024)
- SIGMET/VAA TAC convert overlay — out of EV-074; **validate-first ops** EV-074 / #1043
- SIGMET exchange *emit* — **EV-076 / #1061** closed; VAA exchange emit deferred (`D-EV074-vaa-follow`)
- `#1033` SIGMET `code-ca` semantics — note-only in EV-074 (do not ship rules)
- Global app default migration from 2025-2 to 3.0.0
