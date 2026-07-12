# Migrations moved

Canonical Supabase migrations are at the **repo root**:

```
supabase/
  config.toml
  migrations/   # timestamp-ordered SQL migrations
  seed.sql
```

Local development:

```bash
make supabase-start    # Docker + local stack
make supabase-reset    # apply migrations + seed
make supabase-status   # URLs and keys for .env
```

See [Supabase local development](https://supabase.com/docs/guides/local-development/overview)
and `docs/ops/env-sync-runbook.md` §Database advisor remediation.

Edge functions remain under `apps/frontend/supabase/functions/`.
