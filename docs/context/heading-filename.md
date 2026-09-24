# Real heading on translation metadata and the IWXXM filename

Session: EV-1277-heading-filename. Ticket: #1277. Scale: standard. Gate: closed.

[Corpus: product §F6] [Corpus: api] [Corpus: tests]

## Goal

A bulletin conversion carries the real abbreviated heading in its translation metadata and in the suggested IWXXM filename.

## Out of scope

Do not gzip the XML bytes. Do not open an AMHS connection. Do not invent a heading when the paste has no heading line. Do not implement parent #1275. Do not promote `stage` to `main`.

## What is already true

- `iwxxm_filename` in `packages/tac2iwxxm` already builds `A_{IWXXM-T1T2…}_C_{CCCC}_{timestamp}.xml`, and `.xml.gz` when `gzip=True`. Tests already show SA mapping to LA, not the TAC designator.
- Successful translation-centre emit (`emit_translation_centre`) writes only `translationCentreDesignator` and `translationCentreName`. It does not write `translationTime`, `translatedBulletinID`, or `translatedBulletinReceptionTime`.
- Canada (`ca_eccc`) turns that centre emit on and suggests an MSC datamart name ending in `.xml`, not `.xml.gz`.
- A failed translation shell still hardcodes `translatedBulletinID="TTAAiiCCCYYGGgg"` and `translationCentreDesignator="YUZZ"`. `translationFailedTAC` is the original TAC.
- Ordinary in-state convert leaves the translation attributes off.

## Gap

On-behalf convert does not yet copy the parsed heading into `translatedBulletinID`, or stamp `translationTime` and `translatedBulletinReceptionTime`. The failed-translation shell still uses the workshop placeholders when a heading was parsed. Bulletin convert does not yet return the existing `.xml.gz` filename. A paste with no heading line stays without an invented heading. The Canada `.xml` datamart name is a separate contract.

## Success

- An on-behalf METAR bulletin includes translation time and the real `TTAAiiCCCCYYGGgg` identifier.
- A failed translation no longer emits `YUZZ` or `TTAAiiCCCYYGGgg` when a heading was parsed.
- Bulletin convert returns a suggested filename ending in `.xml.gz` whose T1T2 is the IWXXM designator.

## Docs

Delta only: this brief, a feature-list note under F6 if the emit contract is specified there, and a test-plan row for the three checks.

## UI

No new operator screen. The suggested filename is a convert result field. Non-deployed UI preview: not applicable unless that field is newly shown.
