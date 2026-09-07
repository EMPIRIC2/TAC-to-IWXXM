# EV-097 — Deep-research domain handoff (evolve sub-skill + rule)

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-09-02 | Process/meta evolve — **no product Fn** | Agents need durable handoff prompts for deep-research domain mining with operator checkpoints; not a convert/validate feature |
| 2026-09-02 | New project skill `deep-research-domain-handoff` | Evolve-invokable; emits copy-pasteable prompts; owns AskQuestion gates A/B/C (scope → findings → promote) |
| 2026-09-02 | Optional rule `deep-research-domain-handoff.mdc` | Agent-requestable; fail-closed on silent promote to canonicals |
| 2026-09-02 | Promote/conflict ownership stays on `mine-domain-sources` | Avoid a second domain tree; lean `docs/domain/` layout unchanged |
| 2026-09-02 | No new minimal CORPUS member | `docs/domain/` remains non-minimal; cite **decisions** + domain hub in agent docs |
| 2026-09-02 | Project wiring only | protocol-card + skill-routing; **no** pack `orchestrators/evolve` rewrite |
| 2026-09-02 | PR base **`stage`** | Repo policy (`pr-into-stage-first`) |
| 2026-09-02 | No user-facing internal doc refs | EV-/Corpus cites stay in agent docs/rules only |
| 2026-09-02 | No mining pass this cycle | Deliver skill/rule/wiring only |

## Acceptance

See session `EV-097-deep-research-domain-handoff` (`reports/requirements.md` REQ-EV097-01..10).

## Related

- `.cursor/skills/mine-domain-sources/`
- `docs/domain/README.md` (hub; non-minimal corpus)
- EV-096 pattern: skill/rule harden via evolve (`docs/decisions/ev-096-ci-rules-skills-harden.md`)

[Corpus: decisions] [Corpus: product] (process — no Fn)
