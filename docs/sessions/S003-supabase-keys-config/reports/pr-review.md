# PR Review — S003 / PR #686

> Generated: 2026-06-23  
> Session: S003-supabase-keys-config  
> Skill: 18-pr-review  
> PR: https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/686  
> Head: `fix/supabase-service-key-leak` @ `77c12eb`

## Verdict

**REQUEST_CHANGES** (1 blocker) — posted as GitHub **Comment** (author cannot request-changes on own PR via API).

## Summary

| Metric | Count |
|--------|-------|
| Blockers | 1 |
| Advisories | 5 |
| Praise | 3 |
| CI | failure (Validate / Prettier) |

## Blockers

1. **Prettier format-check** on `apps/frontend/public/config.json` — CI Validate fails; Test/Deploy skipped. Reproduced locally via `make validate-ci`.

## Advisories

1. Committed `sb_publishable_*` in `public/config.json` vs ADR-010 build-time injection policy
2. Legacy `apps/frontend/utils/supabase/info.tsx` hardcoded anon JWT not removed (B8 follow-up)
3. PR scope expanded to full S003 migration (74 files)
4. H0i CORS tests still use port 5173 vs config `18000`
5. Post-merge operator rotation steps pending (documented)

## CI

- Validate: **FAIL** (Prettier)
- Test matrix: skipped
- Local parity: **FAIL** (same)

## Subagents

- Bugbot: failed (could not compute branch diff) — manual review performed
- Security: failed (could not compute branch diff) — manual review performed

## Targeted tests (local)

61 passed: `test_config_loader`, `test_supabase_env`, `test_evaluation_store_unit`, `test_evaluation_router_unit`, `test_admin_api_unit`

## GitHub artifacts

- Inline: https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/686#discussion_r3463374391
- Inline: https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/686#discussion_r3463374418
- Review body: PR #686 conversation (18-pr-review)

## Recommended fix before merge

```bash
pnpm exec prettier --write apps/frontend/public/config.json
git add apps/frontend/public/config.json && git commit -m "hotfix: format public config.json for Prettier CI"
git push
```
