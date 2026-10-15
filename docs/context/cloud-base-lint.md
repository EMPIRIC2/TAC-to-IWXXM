# Context: unknown cloud base

**Session:** `EV-1407-cloud-cb-lint`
**Date:** 2026-10-15
**Mode:** micro evolve
**Ticket:** [#1407](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1407)
**Corpus:** [Corpus: product §F6] [Corpus: product §F15] [Corpus: tests]

## Goal

Accept `FEW///CB`, `SCT///CB`, and `BKN///TCU` as cloud with an unknown base and a convective type. Lint must not raise `CLOUD_CB_OR_TCU` for those groups.

## Out of scope

- Convert encoding of `FEW///CB` and `TCU` (already keeps the amount and the type, with no base height)
- Encoding `//////`
- Truly illegal tokens such as `SCT(0)45`
- A known base with `CB` or `TCU` (`FEW020CB` still notes `CLOUD_CB_OR_TCU`)
- A missing convective type (`FEW020///` still notes `CLOUD_TYPE_NOT_OBSERVABLE`)
- Other epic children

## Locked decision

`FEW///CB` already converts. The defect left on the legacy cloud rule was an info note, `CLOUD_CB_OR_TCU`, for any group ending in `CB` or `TCU`, including an unknown base. An unknown base with `CB` or `TCU` is valid. The note stays only when the base is three digits.
