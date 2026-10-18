# Context — lowercase report keywords and tester-packet fixtures

**Session:** `EV-1405-tester-packet-tests`
**Date:** 2026-10-17
**Mode:** standard evolve
**Tickets:** [#1405](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1405) under [#1396](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1396)
**Corpus:** [Corpus: product §F6] [Corpus: api] [Corpus: tests]

## Goal

Accept a fully lowercase METAR or SPECI the same way as its uppercase twin, and keep a unit test plus a regression test for every full TAC report in the October 2026 regional tester packet.

## Out of scope

- Jamaica log rows that record only a station code
- Reopening #1397–#1404 and #1406–#1412
- Case-folding TAF or SIGMET
- Case-folding a weather token on a report whose keyword is already uppercase, as a separate rule
- UX, onboarding, and spreadsheet repair
- A new feature id
- Deploying this cycle (the staging check runs after the fix is on staging)

## Users

Regional meteorological-service testers paste METAR and SPECI into the public convert page. St Maarten’s note is that the report must be in capitals or conversion fails. Urgency is normal. The parent epic is on the 11 November gate.

## What the product already says

[Corpus: product §F6] already requires the report keyword in any case, and it records letter case as unbuilt. The failure string is `no METAR/SPECI report found in TAC`.

The St Maarten sample on #1405 is entirely lowercase, including the station and the groups:

`metar tncm 081200z 14006kt 9999 few020 28/24 q1013=`

The packet extract states the same defect in words and does not contain that full line. The line lives on the issue.

## Where case is rejected

`parse_metar_speci` searches for `METAR` or `SPECI` in capitals, then `_REPORT` requires a capital station and `Z`. Wind, visibility, temperature, and QNH patterns also expect capitals. Uppercasing the whole METAR or SPECI report before those patterns run makes the lowercase sample match its uppercase twin. TAF and SIGMET patterns stay case-sensitive.

## Packet inventory

Unique full reports in `.local/reference/tac-iwxxm-translator-testing-results/extracts/`, matched as a product keyword, a four-character station, and a six-digit time (SIGMET when the line also has a time, `VALID`, or `=`). Index, manifest, and feedback-summary files are excluded. XML is excluded.

| Product | Count |
|---------|------:|
| METAR | 600 |
| TAF | 70 |
| SPECI | 65 |
| SIGMET | 20 |
| **Total** | **755** |

| Country folder | Count |
|----------------|------:|
| Belize | 618 |
| St Kitts and Nevis | 56 |
| Guyana | 50 |
| Jamaica | 21 |
| Saint Lucia | 10 |

The largest file is Belize Week 1 METAR dataset (433). St Maarten’s folder has the capital-letter note and no full report line. Add the #1405 sample beside the 755.

## Checks

- Local Playwright on the public convert page, using the existing manual-METAR helper, for the lowercase sample
- Staging API check of that sample after the fix is on staging
- No local UI preview in this spec pass
- Docs delta later: feature-list status note and test-plan rows. No API contract edit in this cycle
- H4–H5 stay as they are. One local browser check covers the widened input. No new CORS or `VITE_*` wiring

## Locked decision

Every unique full report is a fixture. A report that already converts must still convert. A report that still fails keeps today’s error and is not fixed in this cycle. The lowercase St Maarten sample must convert, and its report status and groups must match the uppercase twin.

## Memory

Retrieve skipped. Neo4j at `bolt://localhost:7687` was down.
