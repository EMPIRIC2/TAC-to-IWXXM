# PDF mining notes template

Use for **transitory** digs under `docs/domain/mining/<slug>-mining-notes.md`.
Replace bracketed fields. **Not normative** — promote durable citations into
`TAC_VALIDATION.md` / `IWXXM_CONVERSION.md` / `IWXXM_VALIDATION.md` (+ `rules/`) via
[mine-domain-sources](../mine-domain-sources/SKILL.md).

Prefer the fuller [mine-domain-sources/notes-template.md](../mine-domain-sources/notes-template.md)
when the PDF maps to F6 validation / conversion / IWXXM-validation (product matrix +
catalog paste rows + defer-to-latest cross-check).

```markdown
# [Document short title] — focused mining notes

**Status:** working notes (not normative). Verify against the PDF / official registry.  
**Focus of this pass:** [sections / topics]  
**Local PDF + extracts (gitignored):** `.local/reference/<slug>/`

**Standing catalog (promote into):**

| Doc | Path |
|-----|------|
| Domain hub | [../README.md](../README.md) |
| TAC validation | [../TAC_VALIDATION.md](../TAC_VALIDATION.md) |
| IWXXM conversion | [../IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| IWXXM validation | [../IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |

| Item | Value |
|---|---|
| Title | [full title] |
| Edition / date | [edition] |
| Official record | <[permalink]> |
| Pages | [N] |
| Local text | `.local/reference/<slug>/fulltext.txt` |
| Access | public / captcha / paywall |
| Label | normative / informative / … |

---

## Document map

| Section | Approx. PDF pages | Relevance |

---

## Key findings

### [Topic 1]

[Bullets with page citations, e.g. (PDF p. 98)]

### [Topic 2]

…

---

## Domain-knowledge cross-check

When this PDF **contradicts** an earlier claim, defer to latest per mine-domain-sources.

| Older claim (doc + date/edition) | This PDF finding | Action |
|----------------------------------|------------------|--------|
| … | … | supersede / caveat / historical |

---

## Implications for this repo

- **tac-validate / TAC_VALIDATION.md:** …
- **tac2iwxxm / IWXXM_CONVERSION.md:** …
- **iwxxm-validate / IWXXM_VALIDATION.md:** …
- **Promotion pending:** [yes/no — what rows]

---

## Local extract index

| Extract | Contents |
|---|---|
| `extracts/…` | … |

---

## Suggested next mining passes

1. …
```
