---
name: asd-ste100
description: >
  Apply ASD-STE100 Issue 9 Simplified Technical English to repository Markdown
  in check or rewrite mode (strict vocabulary), remove unexplained project
  jargon, and rewrite ambiguous references (the/this/that/it) so every noun is
  trackable for a first-time reader. Use only when the user explicitly attaches
  or names this skill, or asks to apply ASD-STE100 / STE / Simplified Technical
  English to docs. Does not auto-invoke.
disable-model-invocation: true
metadata:
  standard: ASD-STE100 Issue 9 (2025-01-15)
  modes: check, rewrite
  register: strict
---

# ASD-STE100 for repository Markdown

Apply **ASD-STE100 Issue 9** (Simplified Technical English) to Markdown in this
repo. This skill is **explicit-only**: run it only when the user attaches or
names it.

**Authority:** The free official standard at
[asd-ste100.org](https://www.asd-ste100.org/STE_downloads.html) is the primary
reference. This skill is not affiliated with, endorsed by, or certified by the
STEMG or ASD. Plausible STE-like text is not verified compliance. See
[references/ai-oversight.md](references/ai-oversight.md).

## Modes

| Mode | When | Action |
|------|------|--------|
| **check** | User asks to check, audit, review, or report STE issues | Report findings only. Do not edit files. |
| **rewrite** | User asks to rewrite, apply, fix, or make STE-compliant | Edit Markdown prose in place. |
| **both** | User asks for both, or says “check then rewrite” | Check first, then rewrite after confirmation unless they already authorized rewrite. |

If the mode is unclear, ask once: check, rewrite, or both.

## Scope

**Default target:** all repository Markdown (`.md` / `.mdx`) unless the user
names files or directories.

**Include:** `docs/`, root and package READMEs, `.cursor/**/*.md` skill/rule
prose when the user includes them, and other tracked `.md` / `.mdx`.

**Exclude unless the user overrides:**

- `node_modules/`, `.git/`, `vendor/`, `dist/`, `build/`, coverage reports
- `docs/ARCHIVE/`, session dumps the user did not name
- Binary or generated dumps that happen to end in `.md`

**Protected regions (never rewrite content):** fenced code, inline code,
identifiers, file paths, URLs, TAC/IWXXM samples, XML/JSON/YAML examples,
frontmatter keys/values that are machine-read, quoted errors, product/legal
names, and `[Corpus: …]` cites. Report findings inside protected regions in
**check** mode; leave the text unchanged in **rewrite** mode.

**Facts:** Do not invent steps, limits, hosts, or causes. If STE needs a clearer
construction and the source lacks a fact, flag the gap instead of guessing.

**Clarity (required with STE):** Every document must read clearly to someone who
does not know this project. Remove unexplained jargon. Make every `the` /
`this` / `that` / `it` / `they` point to one explicit, trackable noun. See
[references/clarity-and-jargon.md](references/clarity-and-jargon.md).

## Before any work

1. Read [references/writing-rules.md](references/writing-rules.md).
2. Read [references/strict-vocabulary.md](references/strict-vocabulary.md).
3. Read [references/clarity-and-jargon.md](references/clarity-and-jargon.md).
4. Read [references/ai-oversight.md](references/ai-oversight.md).
5. Resolve the official dictionary (required for **strict**):

   | Priority | Source |
   |----------|--------|
   | 1 | Env `ASD_STE100_PATH` (PDF or extracted text of Issue 9) |
   | 2 | `docs/ste/` local copy (gitignored; see strict-vocabulary) |
   | 3 | User-supplied path this turn |

   If none exist, **stop** and ask the user to provide Issue 9 (free request at
   asd-ste100.org) or set `ASD_STE100_PATH`. Do not invent Part 2 entries.
   Writing-rule findings may still be reported as **style-only** if the user
   waives dictionary lookup for this run.

6. Say once per conversation: no tool guarantees ASD-STE100 compliance; human
   review against Issue 9 remains required.

## Workflow

```
Progress:
- [ ] Mode and file scope confirmed
- [ ] Official Issue 9 / dictionary path resolved (or waiver recorded)
- [ ] Classify each editable passage: procedural vs descriptive
- [ ] Apply Sections 1–9 + strict vocabulary
- [ ] Strip unexplained project jargon; define terms at first use
- [ ] Resolve ambiguous the/this/that/it/they to explicit nouns
- [ ] Self-check (below)
- [ ] Deliver check report and/or rewritten files
```

### Classify text

- **Procedural:** tells the reader what to do → imperative, ≤20 words/sentence,
  one instruction per sentence (unless simultaneous actions), condition before
  command.
- **Descriptive:** explains systems/facts → no imperative, ≤25 words/sentence,
  one topic per paragraph, ≤6 sentences per paragraph.
- **Notes:** information only (descriptive limits). Never put commands in notes.
- **Warnings / cautions:** command or condition first, then the concrete risk.

### Check report format

For each finding:

```text
[Rule X.Y | Clarity:jargon | Clarity:ambiguous-ref] file:line — "offending phrase"
→ STE: "compliant rewrite"
Note: (optional: dictionary unverified / protected region / fact gap)
```

Group by file. End with counts: STE findings, clarity findings, unprotected vs
protected, dictionary unverified.

### Rewrite behavior

1. Change only editable prose in scope.
2. Prefer the smallest edit that satisfies the rule.
3. Keep heading hierarchy and list structure unless a rule requires a vertical
   list or sentence split.
4. American English spelling (Rule 1.14) unless quoted text must stay as-is.
5. After edits, re-run the self-check on changed paragraphs.

## Self-check (strict)

Before delivering:

1. Longest sentences: procedural ≤20 words, descriptive/notes ≤25 (count per
   [references/writing-rules.md](references/writing-rules.md) §8).
2. No `;` semicolons in editable prose.
3. No contractions; keep articles (Rule 4.5). Keep connector `that` when it
   removes ambiguity (GR-1). Never leave demonstrative `this`/`that` without a
   noun.
4. Active voice; no present perfect / progressive where STE forbids them.
5. No unapproved `-ing` verbals (Rule 3.5 exceptions only).
6. Multi-word nouns ≤3 words, or introduce then shorten (Section 2).
7. Verbs/nouns checked against Part 2 when the dictionary path is available;
   otherwise mark remaining risk as dictionary-unverified.
8. Consistent technical nouns for the same item (Rule 1.11 / 9.4).
9. Common traps from [strict-vocabulary.md](references/strict-vocabulary.md)
   (check/verify/ensure → `make sure that`, etc.).
10. First use of every project/domain term includes a plain definition
    ([clarity-and-jargon.md](references/clarity-and-jargon.md)).
11. Ambiguous-reference test: every `the` / `this` / `that` / `it` / `they` in
    editable prose has one trackable noun; no “the above”, bare “this”, or
    assumed pipeline slang.

## Examples

See [references/examples.md](references/examples.md).

## Related

- Pair with `avoid-ai-writing` only when the user asks for both; STE controls
  controlled language, avoid-ai-writing controls AI-ism patterns.
- Official downloads and AI white paper:
  https://www.asd-ste100.org/STE_downloads.html
