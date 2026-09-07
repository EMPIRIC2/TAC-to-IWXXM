# EV-096 — Harden Cursor rules/skills from CI footguns (#1096)

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-08-31 | Process/DX evolve — **no product Fn** | Turn observed CI breakage into durable agent guidance; fix underlying product bugs under their own tickets |
| 2026-08-31 | Spec docs: **test-plan delta + this decision** only | Skip Feature list / Spec / Journeys / ADR; CORPUS cites **tests** + **decisions** (+ deploy for promote) |
| 2026-08-31 | Top-3 acceptance footguns | (1) FE Vitest global **100%** / util coverage (e.g. `semanticProfile.ts`) (2) **E2E Full** on promote triage (3) Mutation **pnpm** `packageManager` dual-spec |
| 2026-08-31 | Mutation: **document + fix** pin this cycle | `pnpm/action-setup` vs root `packageManager` caused [Mutation #33386557847](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/33386557847) |
| 2026-08-31 | Vendor Schema Sync: **document only** | Recurring weekly red is triage guidance; do not chase historical sync runs here; never hand-edit `vendor/schemas` |
| 2026-08-31 | #1095 / EV-095: **verify-only** | Guard `scripts/ci/check_cursor_no_home_paths.py` already in `make validate-fast` |
| 2026-08-31 | PR base **`stage`** | Repo policy (`pr-into-stage-first`); promote path unchanged ([Corpus: deploy] §Promote) |
| 2026-08-31 | No user-facing internal doc refs | EV-/Corpus cites stay in agent docs/rules only |

## Acceptance

See issue [#1096](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1096) and session
`EV-096-ci-rules-skills-harden` (`reports/requirements.md`, TC-EV096-001..005).

## Related

- [#1095](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1095) / `docs/decisions/ev-095-em-portable-paths.md`
- `.cursor/rules/optional/ci-after-push.mdc`, `ci-quality-gates.mdc`, `doks-promote-from-stage.mdc`

[Corpus: decisions] [Corpus: tests] [Corpus: deploy]
