# 01-requirements — EV-058 / S068 (delta)

**Mode**: delta (deepen F7.q — #983)  
**Status**: **completed** (`D-S068-01-ac=2b`)  
**Corpus**: [Corpus: product §F7.q] [Corpus: journeys §UJ-056] [Corpus: tests] [Corpus: decisions]

## Document manifest (approved)

| Doc | Action |
|-----|--------|
| `docs/feature-list.md` | F7 / F7.q EV-058 deepen + AC1–AC5 |
| `docs/user-journeys.md` | UJ-056 deepen (layout toggle + persist) |
| `docs/test-plan.md` | TC-EV058-001..005; UJ-056 map |
| `docs/decisions/requirements-decisions.md` | §EV-058 |
| `docs/decisions/evolve-decisions.md` | §EV-058 |
| api-contract / config / system-spec / deploy | **skip** — FE-only; no API/`match_status` change |

## Acceptance (approved `D-S068-01-ac=2b`)

| ID | Criterion |
|----|-----------|
| AC1 | Switch Inline ↔ Side-by-side without reload |
| AC2 | Default = unified |
| AC3 | Side-by-side via existing line-diff util; no new npm `diff` |
| AC4 | Preference in localStorage |
| AC5 | TAC/diagnostics/collapse kept; Vitest + Playwright both modes; H4–H5 via 13; synced scroll **best-effort** |

## Phase 0 / 01 locked

| ID | Choice |
|----|--------|
| D-S068-01-start | 1a — delta F7.q #983 |
| D-S068-01-ac | 2b — AC1–AC5; synced scroll best-effort |
| D-S068-01-control | 3a — segmented Inline \| Side-by-side |
| D-S068-01-uj | 4a — deepen UJ-056 + TC-EV058-* |
| D-S068-ui-preview | 1 — http://127.0.0.1:18000/ |

## Out of scope

- API / backend / C14N / `match_status` / corpus regen
- New npm diff library
- Promote to main
- Synced scroll as hard AC (best-effort only)

## Next

**02-verify-plan** — Gate A on this delta.
