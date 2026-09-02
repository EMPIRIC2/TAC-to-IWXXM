---
name: deep-research-domain-handoff
description: >
  Evolve-invokable handoff for deep-research agents mining TAC / TAC→IWXXM /
  IWXXM validation domain knowledge. Emits copy-paste prompts and AskQuestion
  gates (scope → findings → promote). Promote via mine-domain-sources only.
  Use when evolve needs domain evidence beyond current docs/domain canonicals,
  or the operator asks for deep research / domain mining handoff.
---

# Deep-research domain handoff

[Corpus: decisions] `docs/decisions/ev-097-deep-research-domain-handoff.md`

Project-only skill. **Evolve** (or the operator) invokes this when domain evidence is
needed beyond current lean canonicals. This skill does **not** own promote/conflict —
that stays on [mine-domain-sources](../mine-domain-sources/SKILL.md).

Hub: [`docs/domain/README.md`](../../../docs/domain/README.md) (non-minimal CORPUS).

## When to use

- Evolve cycle hits a gap in `docs/domain/` canonicals / `rules/` / profiles evidence
- Operator asks for deep research on WMO/ICAO/vendor sources
- Quality-bar or national-profile work needs external digs before encoding rules

## When not to use

- Findings already cited in canonicals — cite those; do not re-mine
- Engine / product code changes (use evolve product REQs)
- Running a full mining pass without operator scope (gate A)

## AskQuestion gates (mandatory)

| Gate | When | Pass criteria |
|------|------|---------------|
| **A — Scope** | Before emitting handoff | Products, roles, source hints, ticket, deliverable path agreed |
| **B — Findings** | After deep-research returns | Operator reviewed dig summary; contradictions noted |
| **C — Promote** | Before editing SoT | Explicit approve to update canonicals / `rules/` via mine-domain-sources |

**Fail-closed:** Without gate **C**, write only session notes and/or
`docs/domain/mining/<slug>-mining-notes.md` (+ index). Never edit
`TAC_VALIDATION.md` / `IWXXM_CONVERSION.md` / `IWXXM_VALIDATION.md` / `rules/` SoT rows.

## Workflow

```
- [ ] 1. Gate A — AskQuestion scope (products × roles × sources × out-of-scope)
- [ ] 2. Fill handoff-prompt-template.md → paste for deep-research agent
- [ ] 3. Wait for research return (other chat / operator paste)
- [ ] 4. Gate B — AskQuestion findings review
- [ ] 5. Optional: write/update mining notes (transitory)
- [ ] 6. Gate C — AskQuestion promote?
- [ ] 7. If yes → invoke mine-domain-sources (publish + defer-to-latest)
- [ ] 8. Commit only if user asks
```

## Handoff prompt

1. Copy [handoff-prompt-template.md](handoff-prompt-template.md)
2. Fill bracketed fields from gate A
3. Present to operator / deep-research agent as the full brief
4. Keep a copy under the session `reports/` if useful (optional)

## Hard rules

- URLs + paraphrases only — no Annex 3 / Doc 8896 / Manual on Codes full-text in git
- No `git add` of `.local/reference/` PDFs or `fulltext.txt`
- No edits inside `vendor/schemas/*` except vendor sync PRs
- No second domain tree — lean layout only
- GIFTs = historical gap baseline only
- Contradictions → defer-to-latest (mine-domain-sources)
- No operator-facing EV-/Corpus ids in product UI / OpenAPI

## Related

- Rule: `.cursor/rules/optional/deep-research-domain-handoff.mdc`
- Promote: [mine-domain-sources](../mine-domain-sources/SKILL.md)
- Citation policy: `docs/domain/rules/ACCESS_AND_CITATION.md`
- PDF ingest: [extract-pdf-to-repo](../extract-pdf-to-repo/SKILL.md) (if present) / pack equivalent
