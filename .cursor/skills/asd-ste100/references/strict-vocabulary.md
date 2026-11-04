# Strict vocabulary (Part 2 discipline)

Strict mode requires dictionary discipline from ASD-STE100 Issue 9 **Part 2**.
The controlled dictionary is copyrighted by ASD and is **not** shipped in this
skill.

## Obtain and locate Issue 9

1. Request the free official copy:
   https://www.asd-ste100.org/STE_downloads.html
2. Store it **outside git** or under a gitignored path, for example:

   - Env: `ASD_STE100_PATH=/absolute/path/to/ASD-STE100_ISSUE9.pdf`
   - Or: `docs/ste/` (gitignored — do not commit the PDF or extract)

3. **Seeded in this repo (local only):** after download, agents may use:

   - `docs/ste/ASD-STE100_ISSUE9.pdf`
   - Searchable extract: `docs/ste/ASD-STE100_ISSUE9.txt` (when present)
   - Path hint file: `docs/ste/.env.path` (`ASD_STE100_PATH=…`)

   Prefer `export $(cat docs/ste/.env.path)` or set `ASD_STE100_PATH` explicitly.
   Grep the `.txt` extract for Part 2 entries when checking vocabulary.

4. Before strict rewrite or vocabulary claims, open Part 2 (or searchable
   extract) for every non-technical word you keep or introduce.

If the dictionary is unavailable and the user does not waive it, stop. If they
waive it for one run, label every vocabulary-sensitive finding
`dictionary-unverified` and do not claim compliance.

## What Part 2 decides

| Rule | Obligation |
|------|------------|
| 1.1–1.4 | Approved word / POS / meaning / form |
| 1.6 | Non-dictionary words only as (part of) technical nouns |
| 3.1 | Verb forms exactly as listed |
| 9.2 | Correct approved meaning |
| GR-5 / GR-8 | False friends; careful possessives |

Technical nouns/verbs (Rules 1.5, 1.12) may be outside Part 2 when they fit a
category and match company/subject terminology. Prefer a dictionary verb +
technical noun when that is enough.

## High-frequency software/docs traps

These are operational reminders. When Issue 9 is available, **confirm each
swap against Part 2** before applying it.

| Often written | Strict handling |
|---------------|-----------------|
| check / verify / confirm / ensure (verb) | Prefer `make sure that` (state), `examine` (look for faults), or noun form `do a check of` |
| validate | Technical verb if justified (1.12), else `make sure that` |
| run / execute | Prefer `operate` / `do` unless a technical verb is justified |
| display / render / present (verb) | Prefer `show` when it matches the approved meaning |
| perform | Prefer `do` |
| need to / have to | Procedure: imperative. Description: `it is necessary to` |
| however / therefore / since (=because) | Prefer `but` / `thus` or `as a result` / `because` |
| e.g. / i.e. / etc. | Prefer `for example` / `that is` / `and so on` (GR-6) |
| Phrasal verbs (`set up`, `put out`, …) | Prefer a single approved or technical verb (9.3) |

Quoted commands, API names, SQL keywords, CLI flags, and product strings stay
unchanged (quoted / protected text).

## Project technical nouns/verbs

For this monorepo, treat established product and domain terms as technical
nouns or verbs when they name a specified concept, for example:

- Products/packages: METAR, SPECI, TAF, SIGMET, IWXXM, TAC, WIS2, AMHS
- System names: `tac2iwxxm`, `tac-validate`, `iwxxm-validate`, workbench,
  dissemination drawer, worker
- Domain nouns: bulletin, schema pin, Schematron, XSD, ICAO location indicator

Technical-noun status does **not** waive clarity. At first use in each file,
still give a plain definition (see
[clarity-and-jargon.md](clarity-and-jargon.md)). Do not invent slang. Keep one
technical noun per item across a document (Rule 1.11).

## Strict self-check additions

1. Every editable content word is: Part 2 approved, technical noun, technical
   verb, or protected/quoted.
2. Every verb form matches Part 2 (or technical-verb rules).
3. No part-of-speech misuse of approved words.
4. No dictionary-unverified claims in the final “compliance” sentence — say
   “STE-oriented rewrite pending human Part 2 review” when the PDF was missing
   or unverified.
