# TAC template amendments in the profile catalog

Session: EV-1274-template-catalog. Ticket: #1274. Scale: standard. Gate: open.

[Corpus: product §F6] [Corpus: product §F15] [Corpus: domain-profiles] [Corpus: tests]

## Goal

When ICAO or WMO changes a TAC template, record that change in a catalog next to the country profile catalog, and update conversion only where the template actually changed.

## Out of scope

Do not implement the Amendment 82 element changes in this ticket. Do not reopen the closed METAR/SPECI matrix. Do not invent national TAC rules that were not seen in a published bulletin or a cited template. No operator UI. Do not implement parent #1267. Do not promote `stage` to `main`.

## What is already true

Country lint differences are detector and policy YAML under `packages/tac-validate`. There is no `lint_profiles.yaml`. The profile machine catalog is `docs/domain/profiles/catalog.yaml`. The national-profile playbook already says a new country is a catalog row. It does not yet say that a TAC template update is the same kind of row.

IWXXM 2025-2 is the first watched set. Its release notes name METAR/SPECI, volcanic ash advisory, and space weather advisory changes, plus products that have no TAC form.

## Locked rule

- The catalog is `docs/domain/profiles/template-amendments.yaml`, next to `catalog.yaml`, and the playbook links to it.
- Each row has a source, a product, what changed, which profiles inherit it, a status of `done`, `partial`, or `not_started`, and `tac_convertible`.
- Status is judged against the converters we already have. This ticket does not change emitters.
- `tac_convertible: false` means TAC cannot carry the element. That row is recorded so it is not treated as missing converter work. Its status is `done` because the disposition is recorded.
- Annex 3 inherits a row for a product it converts. US or Canada inherits it only when that profile already converts the product.
- The first list is Amendment 82 METAR/SPECI, VAA, and SWXA, plus IWXXM-only items: extra RVR groups, temperature in tenths, QVACI, and WAFS significant weather.

## Success

- The catalog schema has a place for a TAC template change: source, product, what changed, and which profiles inherit it.
- Amendment 82 METAR/SPECI, VAA, and SWXA template changes are listed, each marked done, partial, or not started.
- The national-profile playbook says a template update is a catalog row, reviewed the same way as a country lint delta.
