# Selectable profiles for formats the current four do not cover

Session: EV-1267-selectable-profiles. Ticket: #1267. Scale: standard. Gate: open.

[Corpus: product §F6] [Corpus: product §F7] [Corpus: domain-profiles] [Corpus: adr/ADR-036]

UI reference: declined. This note is from the repo and the issue text. It is not a local screen preview.

## Goal

Add one selectable Convert profile for each format that `annex3`, `iwxxm_us`, `ca_eccc`, and `in_imd` do not represent:

- US convective SIGMET
- G-AIRMET
- US volcano-observatory VONA (Alaska, Hawaii, Cascades), once a clean TAC source exists
- Canadian SIGMET

Each profile is accepted by convert, lint, and validate, uses the IWXXM pin that profile already uses, and has a ready quality-matrix slot in the same 20-slot layout as #1265. Dropdown help is plain language.

## What is already true

The Convert dropdown is driven by semantic profile ids. The four names in the ticket are the legacy aliases, and they stay:

| Legacy name | Semantic id | Pin | What the catalog already lists |
|---|---|---|---|
| annex3 | ICAO_2025 | IWXXM 2025-2 | METAR, SPECI, TAF, SIGMET, AIRMET, VAA, TCA, VONA |
| iwxxm_us | US_FAA_NWS | IWXXM 2025-2 and IWXXM-US 3.0 | METAR, SPECI, TAF, SIGMET, AIRMET, TCA, SWXA, VONA, VAA |
| ca_eccc | CA_ECCC | IWXXM-CA 3.0.0 | METAR, SPECI, TAF, AIRMET, SIGMET, VAA |
| in_imd | IN_IMD | core IWXXM, no national extension | METAR, SPECI, TAF, SIGMET, TCA |

HTTP `product=sigmet` stays one wire value. Ordinary, VA, and TC SIGMET stay separate packs. F6 stays Implemented. No new feature id.

The 2026-09-23 public-bulletin pass (#1266) is the reason these four formats are still uncovered:

- US convective SIGMET and G-AIRMET use a different grammar from Annex 3 SIGMET and AIRMET. There is no convert profile for that grammar. The US catalog cites an NWS convective SIGMET sample as a fixture seed only.
- Alaska and Hawaii VONA on the NWS raw `WM` gateway had spaces replaced with `?` and a truncated body, so they are not fixtures. `iwxxm_us` does not supply a US VONA path. Annex 3 VONA already exists and must stay unchanged when the new profile is not selected.
- Canadian SIGMET on the MSC datamart is published as IWXXM 3.0 with no TAC in the file. `ca_eccc` lint covers METAR, SPECI, TAF, and AIRMET. The catalog lists SIGMET on CA_ECCC, and the MSC file still has no TAC to convert.

## Out of scope

Live map and live refresh. In-app profile authoring. Treating US convective SIGMET as Annex 3 SIGMET. Vendoring partner bulletins beyond matrix fixtures. Renaming annex3, iwxxm_us, ca_eccc, or in_imd. Pull request #1269 (country lint catalog). AMHS. Promoting `stage` to `main`.

## Locked

- Each format gets a new semantic profile id. The legacy aliases annex3, iwxxm_us, ca_eccc, and in_imd stay.
- Catalog ids: `US_NWS_CONVECTIVE_SIGMET`, `US_NWS_VONA`, `CA_MSC_SIGMET`, and `US_NWS_G_AIRMET`. Wire forms are the lowercase ids.
- Canadian SIGMET (`CA_MSC_SIGMET`) stays on the dropdown. The profile validates the published IWXXM 3.0 file. Convert stays unavailable until a TAC source exists. `ca_eccc` keeps its current SIGMET TAC path.
- US VONA (`US_NWS_VONA`) stays on the dropdown. Convert and lint refuse until a clean TAC fixture exists. Annex 3 VONA and the current `iwxxm_us` VONA path stay as they are.
- US convective SIGMET (`US_NWS_CONVECTIVE_SIGMET`) converts and lints on the existing convective emitter. Annex 3 international SIGMET output stays on today's path.
- G-AIRMET (`US_NWS_G_AIRMET`) is listed and refuses convert and lint until a text bulletin exists. The public feed is hazard polygons, not TAC.
- Matrix fixtures stay small. They do not copy partner bulletins into git. A US VONA slot records the refusal. A Canadian SIGMET slot records validation of the published file, not a TAC convert.

## Success

- Each new profile appears in the Convert dropdown and is accepted by convert and lint.
- A ready quality matrix exists for the profile-specific rules.
- Annex 3 output for an international SIGMET, AIRMET, VAA, TCA, SWXA, or VONA is unchanged when the new profile is not selected.
