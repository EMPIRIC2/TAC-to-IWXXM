# Context — shared YAML extension header

**Session:** EV-yaml-extension-header
**Date:** 2026-09-21
**Corpus:** [Corpus: adr/ADR-045] [Corpus: adr/ADR-046] [Corpus: product §F2] [Corpus: product §F6] [Corpus: product §F9] [Corpus: product §F15] [Corpus: api]

## Problem

Decode, TAC lint, IWXXM validation, and conversion are four publishable packages. Each already has its own YAML. A country or profile addition has no shared header, so extending one surface does not look like extending the others. The Validate IWXXM list still shows Schematron failures as `SCHEMATRON_ASSERT`, so a policy cannot drop a real row. Convert-time validation does not pass the policy id that `/validate` passes.

## Locked shape

- `tac-decoding`, `tac-validate`, `iwxxm-validate`, and `tac2iwxxm` stay separate packages. The backend integrates them. They do not import each other.
- Common interface is a YAML header on each package’s own files. The payload stays package-specific.
- Builtin files keep their current `id`. Profile ids default to every profile.
- An overlay layers on the builtin. The same id replaces that one entry. An id that exists only in the overlay is added. Other builtin entries stay.
- IWXXM policy lists: overlay ignore ids are added; a non-empty select replaces the builtin select; an empty select inherits it.
- A Schematron failure with no pattern id stays `SCHEMATRON_ASSERT` and is not dropped.
- The extension key is the conversion profile id already on the wire. No new HTTP field. No country-code axis. No sample country pack this cycle.
- Schematron issue `code` becomes the pattern id. XSD, well-formed, and `SCHEMATRON_SKIPPED` codes stay. Empty select still lists every Schematron failure.
- Convert-time validation passes the same policy id as `POST /api/v1/validate`.
- UI is the existing TAC lint list and the existing Validate IWXXM list. No editor, no new panel, no local browser preview.
- MatchPort stays off `/lint-tac`.
- Decode response fields and convert XML goldens stay.

## Docs

Amend ADR-045 and ADR-046. Delta the feature list (F2, F6, F9, F15) and the test plan. No new feature id and no new corpus member.

## Memory

Retrieve returned no domain matches. Disposition: keep-local. The only hit was a process note about session store drift; this session uses the local session store.

## Must not break

- HTTP profile id only
- Package import boundaries
- Empty policy select still shows every Schematron failure
- XSD, well-formed, and `SCHEMATRON_SKIPPED` codes
- `POST /api/v1/decode-tac` response shape
- Convert XML goldens
