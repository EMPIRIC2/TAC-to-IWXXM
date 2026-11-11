# Runtime configuration (non-secrets)

Committed JSON per environment. Secrets stay in repo-root `.env` only.

| File | When used |
|------|-----------|
| `local.json` | `METAR_CONFIG_ENV=local` (default for `make dev`) |
| `e2e.json` | Playwright / local e2e |
| `staging.json` | Staging DOKS profile |
| `prod.json` | `METAR_CONFIG_ENV=prod` |

Field reference: [docs/env-variable.md](../../docs/env-variable.md) and
[docs/tech-spec.md](../../docs/tech-spec.md).

**Frontend `/config.json`:** Static deploy runs `scripts/frontend/prepare-config.sh`,
which copies the selected profile and injects `supabase.publishableKey` from
`SUPABASE_PUBLISHABLE_KEY` (not committed). Required Auth bootstrap fields:
`api.baseUrl`, `supabase.url`, plus the injected publishable key.
