# Older IWXXM on the publishing profile

Session: EV-1273-older-iwxxm-pin. Ticket: #1273. Scale: standard. Gate: closed.

[Corpus: product §F4] [Corpus: domain-profiles] [Corpus: adr/ADR-036]

## Goal

When a country profile publishes an older IWXXM package than the app default, convert and validate that package on that profile. Files that already use that package are included. The first pin is Canada IWXXM 3.0.0.

## Out of scope

Parent epic #1267. No 2021-2, 2018, or 2016 on the global version dropdown. 3.0.0 is not a global convert default. No new vendored schema tree. QVACI stays deferred. Australia's public TAF schema maps to 3.0.1 and stays a note until that pin is confirmed. No operator dropdown change. Do not promote `stage` to `main`.

## What is already true

- The global window is 2025-2 (default) and 2023-1 (previous). `supported_iwxxm_versions_for_profile("annex3")` includes both and excludes 3.0.0.
- `CA_ECCC` / `ca_eccc` is pinned to 3.0.0 only. The version-support policy already says a non-3.0.0 request on that profile is rejected, and 3.0.0 is not a global default.
- Vendor trees for `iwxxm/3.0.0` and `iwxxm-ca/3.0` are already on disk. This session does not fetch a new schema.
- METAR, TAF, AIRMET, SIGMET, and TCA examples exist on the 3.0.0 tree. VAA, SWXA, and VONA examples on disk are 2025-2 only.
- Local 3.0.0 XSD compile can raise `SCHEMA_PARSE_ERROR` (`AngleWithNilReasonType`). That limit is recorded, not treated as a new defect.

## Gap

The catalog records one Canada pin (`iwxxm_version_pin: 3.0.0`). It does not list, for every catalogued profile, the IWXXM release and the package version per product (METAR/SPECI, TAF, SIGMET, AIRMET, TCA, VAA, SWXA, WAFS, VONA, QVACI). Incoming IWXXM is not yet checked against the package version the file itself declares when that version is outside the profile's allowed pin.

## Success

- A table lists each catalogued profile, the IWXXM release it emits, and the package version per product.
- A Canada 3.0.0 METAR and a 2025-2 METAR each validate on their own pin. Selecting one pin does not select the other by default.
- A file whose declared package is not allowed for that profile is rejected with a plain-language error.
- 2023-1 remains selectable as the previous global line.

## Docs

Delta only: feature list F4, `docs/domain/iwxxm/VERSION_SUPPORT_POLICY.md`, and the test plan.

## UI

No dropdown change. A rejected package is a plain-language error only. Non-deployed UI preview: not applicable.
