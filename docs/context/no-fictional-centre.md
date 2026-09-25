# No fictional translation centre

Session: EV-1290-no-fictional-centre. Ticket: #1290. Scale: standard. Gate: open.

[Corpus: product §F6] [Corpus: tests]

## Goal

A failed translation with no heading and no supplied centre does not invent `YUZZ` or `Fictional translation centre`.

## Out of scope

Do not invent a heading for a paste that has none. Do not change AMHS. Do not gzip the XML bytes (#1291). Do not re-check the guidelines' minimum fields (#1292). Do not promote `stage` to `main`.

## What is already true

A failed shell with a parsed heading uses that heading. If the caller supplied a centre, that centre is written. If the caller did not, the centre attributes are empty strings, not `YUZZ`. That is #1277.

A failed shell with no parsed heading used to write `TTAAiiCCCYYGGgg`, `YUZZ`, and `Fictional translation centre`. Those placeholders are omitted now.

The centre attributes are optional in IWXXM 2025-2. A failed METAR still needs issue time, aerodrome, and observation time.

## Locked rule

- When no heading was parsed, do not write `translatedBulletinID`, and do not write the placeholder `TTAAiiCCCYYGGgg`.
- When no heading was parsed and the caller did not supply a centre, omit `translationCentreDesignator` and `translationCentreName`.
- When no heading was parsed and the caller did supply a centre, write that centre and still omit the bulletin id.
- When a heading was parsed, keep the current behaviour: that heading, and the caller's centre, including empty strings when none was supplied.

## Success

- A failed METAR with no heading line does not contain `YUZZ` or `Fictional translation centre`.
- A failed bulletin that has a heading still uses that heading and the caller's centre.
