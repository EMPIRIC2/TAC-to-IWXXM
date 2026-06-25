# PR Remediation — PRM-007 (PR #692)

- **PR:** [#692](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/692) — `[hotfix] Bundle Postgres in docker-compose so backend can create DB tables (#671)`
- **Branch:** `fix/S005-issue-671-docker-db` → `main`
- **Session:** S005-issue-671-docker-db
- **Linked review cycle:** none (Sourcery left a `COMMENT` review; no 18-pr-review cycle ran for #692)
- **Review source:** Sourcery AI bot — 1 inline nitpick + 2 high-level (overall) comments. No blockers, no `CHANGES_REQUESTED`.

## Scope decision

User selected: fix the typo (F-001) and the explicit `db`-name assertion (F-003);
mark the shared-test-util extraction (F-002) **won't-fix** (YAGNI — only one
infra bug test exists, the abstraction is speculative).

## Findings

| ID | Severity | Source | Path | Disposition | Commit |
|----|----------|--------|------|-------------|--------|
| F-001 | advisory (nitpick) | inline thread | `docs/sessions/S005-issue-671-docker-db/session-brief.md:7` | fixed — "connect refused" → "connection refused" (also aligned the `intent` in `workflow-state.yaml`) | `2877800` |
| F-002 | advisory | review body | `tests/bugs/test_bug_2026_06_25_docker_db_connect.py` | won't-fix — speculative shared-util extraction; revisit when a 2nd infra bug test lands | — |
| F-003 | advisory | review body | `tests/bugs/test_bug_2026_06_25_docker_db_connect.py` | fixed — `_db_service` now asserts the service is literally named `db` and runs a Postgres image; both compose tests use the `DB_SERVICE` constant | `c08d50a` |

**Counts:** fixed 2 · deferred 0 · won't-fix 1

## Verification

- `uv run ruff check` + `ruff format --check` on the touched test — clean.
- `uv run pytest tests/bugs/test_bug_2026_06_25_docker_db_connect.py` — 8 passed.
- `uv run pytest tests/bugs` — 38 passed (no regression).

## GitHub

- Replied on inline thread `PRRT_kwDOQW-3CM6MVByh` (F-001) and resolved it.
- Posted a [summary comment](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/692#issuecomment-4803745366) addressing the two overall comments (F-003 fixed, F-002 won't-fix).

## CI (post-push)

Branch `984feff` pushed to origin. All in-scope checks pass: `Validate`, every
`Test (*)` (auth/backend/bugs/frontend/gifts/integration/shared), and `E2E Smoke`.
`Deploy edge functions` failed in ~7s on *"Failed to resolve latest Supabase CLI
release: rate limit exceeded"* — a transient GitHub/Supabase CLI rate limit
unrelated to the doc + test changes; **out of scope** (not greenwashed).

## Follow-up

- `pr_review_rerun: offered`
- No merge performed — user merges after re-review.
