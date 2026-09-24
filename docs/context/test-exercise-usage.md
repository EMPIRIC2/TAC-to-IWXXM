# Test and exercise bulletins are non-operational

Session: EV-1276-test-exercise. Ticket: #1276. Scale: standard. Gate: open.

[Corpus: product §F6] [Corpus: tests]

## Goal

When a bulletin is a test or an exercise, the IWXXM marks it non-operational, with a reason and a short supplementary note.

## Out of scope

Do not send the message over AMHS. Do not change in-state translation-centre omission. Do not implement parent #1275. Do not promote `stage` to `main`.

## What is already true

Successful emitters set `permissibleUsage="OPERATIONAL"` and omit the reason and supplementary attributes. That includes Annex 3, Canada, and US success paths, and the failed-translation shell.

IWXXM allows `OPERATIONAL` or `NON-OPERATIONAL`. A non-operational report must carry `permissibleUsageReason` of `TEST` or `EXERCISE`. An operational report must not carry that reason. The exchange guidelines also ask for `permissibleUsageSupplementary`, and say to stay operational when the mapping is uncertain or the translation failed.

NOAA space-weather text already in the quality matrices uses `STATUS: TEST` and a remark such as `THIS IS A TEST SPACE WEATHER ADVISORY`. The space-weather parser stores unknown labelled lines and still converts when the required fields are present. A Canada volcanic-ash fixture contains `VA TEST` as source text. That is not a status line.

## Locked rule

- Mark non-operational only for an explicit marker: a `STATUS: TEST` line, a remark that says this is a test, or the word `EXERCISE` / the phrase `THIS IS AN EXERCISE`. The same rule applies to every product we already convert.
- When both a test marker and an exercise marker are present, the reason is `EXERCISE`.
- Supplementary text is the remark when the bulletin has one. Otherwise it is `Test bulletin` or `Exercise bulletin`.
- Text that merely contains `VA TEST`, or any other uncertain wording, stays operational.
- A failed translation stays operational. The guidelines treat a failed translation as operational so the original TAC can still be recovered.

## Gap

Nothing reads those markers. Every successful convert stays operational.

## Success

- A TEST space-weather bulletin converts with `NON-OPERATIONAL`, reason `TEST`, and supplementary text.
- An ordinary METAR stays `OPERATIONAL` and has no reason or supplementary attribute.
- An exercise SIGMET, when the TAC says it is an exercise, uses reason `EXERCISE`.

## Docs

This brief, a feature-list note under F6, and test-plan row TC-F6-037.

## UI

No new operator screen.
