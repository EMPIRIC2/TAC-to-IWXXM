# 12-verify-deploy — S042 / EV-034 checklist

**Date:** 2026-08-05  
**Scope:** DOKS CD auto-rollout (F30 AC7) — delta

| Item | Status | Notes |
|------|--------|-------|
| Strategy matches E34-1..4 | OK | API+FE+worker; immutable tag; `KUBE_CONFIG`; Render optional |
| Secret `KUBE_CONFIG` present + static (no doctl) | OK | Deploy passed doctl grep; rollout succeeded |
| Rollback | OK | Re-run `doks_rollout_images.sh <prior-tag>` or pin previous `TIMESTAMP-SHA` |
| Fail-closed missing secret | OK | documented + workflow |
| Browser H4–H5 readiness | N/A delta | No UI change this cycle; prior H4/H5 pass on public DNS |
| H0c CORS | OK | unit green |
| Data / Alembic | Unchanged | out of scope |

**Recommendation:** Approve deploy evidence already produced by main Deploy on #868 merge; proceed to formal 13 sign-off.
