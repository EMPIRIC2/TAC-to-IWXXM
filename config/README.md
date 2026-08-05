# Runtime configuration (non-secrets)

Committed JSON per environment. Secrets stay in repo-root `.env` only.

| File | When used |
|------|-----------|
| `local.json` | `METAR_CONFIG_ENV=local` (default for `make dev`) |
| `e2e.json` | Playwright / local e2e |
| `prod.json` | `METAR_CONFIG_ENV=prod` (Render transitional; DOKS after T6.3) |

See [docs/config-spec.md](../docs/config-spec.md) for field reference.

**Frontend `/config.json`:** Static deploy runs `scripts/frontend/prepare-config.sh`, which copies
the selected profile and injects `supabase.publishableKey` from `SUPABASE_PUBLISHABLE_KEY`
(not committed). Required Auth bootstrap fields: `api.baseUrl`, `supabase.url`, plus the
injected publishable key.

**CORS (F30/F31):** `prod.json` `api.corsOrigins` lists the live Render FE origin and the DOKS FE
placeholder (`https://app.doks.placeholder.metar-iwxxm.local`) so dual-traffic soak can allow
both. Pin real DOKS DNS and retire placeholders at **T6.3**.
