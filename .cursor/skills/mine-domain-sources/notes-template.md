# Domain mining notes template

Tracked working notes under `docs/domain/` (usually `docs/domain/iwxxm/` or
`docs/domain/<topic>/`). Replace bracketed fields. **Not normative** — cite official
landings for binding claims.

```markdown
# [Source short title] — focused mining notes

**Status:** working notes (not normative). Verify against official registry / schemas.  
**Focus of this pass:** [products · role · sections]  
**Ticket:** [#N](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/N)  
**Local extracts (if any, gitignored):** `.local/reference/<slug>/`

**Standing catalog:**

| Doc | Path |
|-----|------|
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |
| Companion | [link thematic *_SOURCES.md] |

| Item | Value |
|------|-------|
| Title | |
| Publisher | |
| Official landing | <url> |
| Pin / edition | e.g. iwxxm v2025-2 / Annex 3 21st ed |
| Date mined | YYYY-MM-DD |
| Access | public / paywall / … |
| Label | normative-… |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| … | … |

---

## Product × artifact matrix

| Product | Input (TAC / …) | Output (IWXXM / …) | Official example or register | Gap vs GIFTs | Consumer |

---

## Key findings

### [Topic 1]

- Finding with evidence (`path` or URL)

### [Topic 2]

…

---

## Catalog paste rows

```text
### …
```

---

## Implications for this repo

- **F6 / tac2iwxxm:** …
- **tac-validate:** …
- **iwxxm-validate:** …
- **Caveats / TBD:** …

---

## Suggested next mining passes

1. …
```

When the source is a PDF, also fill local `.local/reference/<slug>/` rows per
[extract-pdf-to-repo/notes-template.md](../extract-pdf-to-repo/notes-template.md).
