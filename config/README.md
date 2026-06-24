# Runtime configuration (non-secrets)

Committed JSON per environment. Secrets stay in repo-root `.env` only.

| File | When used |
|------|-----------|
| `local.json` | `METAR_CONFIG_ENV=local` (default for `make dev`) |
| `prod.json` | `METAR_CONFIG_ENV=prod` (Render deploys) |

See [docs/config-spec.md](../docs/config-spec.md) for field reference.

**Frontend:** Static deploy copies `prod.json` to `public/config.json` and injects
`supabase.publishableKey` from `SUPABASE_PUBLISHABLE_KEY` at build time (not committed).
