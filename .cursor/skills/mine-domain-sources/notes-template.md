# Domain mining notes template

Tracked **transitory** notes under `docs/domain/mining/` only. Replace bracketed fields.
**Not normative / not SoT** — after the dig, promote durable rows into
`TAC_VALIDATION.md` / `IWXXM_CONVERSION.md` / `IWXXM_VALIDATION.md` and
`rules/RULE_SOURCE_URLS.md` (see skill §Publish). Index new files in
`docs/domain/mining/README.md`.

Do **not** place digs under `docs/domain/iwxxm/` or `docs/domain/validation/`.

```markdown
# [Source short title] — focused mining notes

**Status:** working notes (not normative). Verify against official registry / schemas.  
**Focus of this pass:** [products · role · sections]  
**Ticket:** [#N](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/N)  
**Local extracts (if any, gitignored):** `.local/reference/<slug>/`

**Promote durable findings into:**

| Doc | Path |
|-----|------|
| Domain hub | [../README.md](../README.md) |
| TAC validation | [../TAC_VALIDATION.md](../TAC_VALIDATION.md) |
| IWXXM conversion | [../IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| IWXXM validation | [../IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |

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

## Domain-knowledge cross-check (required on full / refresh passes)

When this source **contradicts** an earlier mined claim, **defer to the latest**
source per `SKILL.md` §Conflict resolution. Fill every conflict row:

| Older claim (doc + date/edition) | This source finding | Action (supersede / caveat / keep as historical) |
|----------------------------------|---------------------|--------------------------------------------------|
| … | … | … |

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
