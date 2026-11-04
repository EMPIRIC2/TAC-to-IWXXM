# AI oversight (STEMG white paper alignment)

STEMG published guidance on Simplified Technical English and Artificial
Intelligence (see Downloads on asd-ste100.org, including the white paper linked
near Issue 9). Apply these constraints whenever this skill runs.

## Core positions

1. **ASD-STE100 remains the primary reference.** Model output does not replace
   Issue 9 Part 1 (rules) or Part 2 (dictionary).
2. **Plausibility is not compliance.** Text can look clear, consistent, and
   “STE-like” while breaking approved meanings, parts of speech, or word limits.
3. **Human oversight is required.** An author or reviewer accountable for the
   document must verify critical passages against the official standard.
4. **No endorsement.** This skill and any AI output must not be described as
   approved by, affiliated with, or certified by STEMG or ASD. ASD-STE100 is a
   registered trademark of ASD.
5. **Accountability stays with the user/org.** Use of the standard and of this
   skill is at the user’s risk; respect the Copyright Statement of the current
   issue.

## Agent obligations

- State once per conversation that no tool guarantees ASD-STE100 compliance.
- Prefer check reports with rule ids over vague “made it simpler” claims.
- Never paste large excerpts of Part 2 into the repo or chat logs beyond what is
  needed to justify a single swap.
- Do not commit the official PDF into git.
- When rewriting safety-critical procedure text, prefer check-first and ask
  before broad rewrite if the user did not clearly authorize rewrite.

## Confidentiality

Do not upload customer/proprietary manuals to third-party services solely to
“STE-check” them unless the user explicitly directs that workflow. Prefer local
dictionary path + in-editor review.
