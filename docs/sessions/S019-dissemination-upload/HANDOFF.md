# Handoff — S019 / EV-014 (2026-07-21)

## Resume in next chat

```
/16-evolve continue S019/EV-014 — 07-build M6 T6.6 (needs E2E_USER_* + BYOC destinations; secrets gitignored only)
```

| Field | Value |
|-------|-------|
| Session | `S019-dissemination-upload` |
| Cycle | `EV-014` |
| Merged | #761–#**771** (through **T6.5**; M5+M6 code on `main` @ `2bbe9f5`) |
| Open PRs | [#772](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/772) T6.6 partial smoke + allowlist docs |
| Done | M1–M5; T6.1–T6.5; T6.6 **partial** (H0c/H1/H4/H5 PASS; #771 merged; live FE **drawer present** in `App-*.js`) |
| Deferred | Live Render allowlist set (`RENDER_API_KEY`) — keep empty fail-closed until BYOC hosts known |
| Blocked | Authenticated H3 + live BYOC Postgres+WIS2+EDIS — **no workspace `.env` yet** |
| Branch | `cursor/s019-t66-deploy-smoke-151c` |
| Reports | `deploy-smoke.md` (T6.6); `deploy-checklist.md` (T6.5); `verification-report.md` (T6.4) |

## Secrets policy (operator)

- **Never commit** `.env` / BYOC URIs / passwords (already gitignored).
- Inject secrets **session-only** for live smoke (write gitignored `.env` or export env vars).
- BYOC destination creds stay **memory-only** in preflight/send (ADR-021/029) — do not persist to F5.
- Live `DISSEMINATION_EGRESS_ALLOWLIST`: exact demo hosts only when testing; leave empty (fail-closed) otherwise.

## Allowlist (operator-approved path)

| Env | Value |
|-----|--------|
| Local / CI | `wis2box,127.0.0.1,127.0.0.0/8,localhost` (in `.env.example` + CI harness default) |
| Render (now) | **Empty** (fail-closed) — no API key this session |
| Render (live BYOC demos) | Exact Postgres / WIS2 / EDIS SMTP hostnames only |

## Unblock checklist

1. Provide `E2E_USER_EMAIL` / `E2E_USER_PASSWORD` (admin login) + BYOC destination params (memory-only) — paste into chat or private-worker secrets; agent writes **gitignored** `.env` only.
2. ~~Merge #771~~ **DONE** (`2bbe9f5`) — CI Deploy green; live FE `App-C1eOPfC1.js` contains `dissemination` / `preflight`.
3. Optional: `RENDER_API_KEY` to set live allowlist to demo hosts before BYOC.
4. Capture live BYOC evidence; F19 live optional waive.
5. Mark T6.6 completed → C→D / Phase D stages.

## Do not skip

- Live BYOC close gate: Postgres + WIS2 + EDIS (Q15=A / Q21=A)
- TC-F18-002 live EDIS remains cycle-close only
- F19 live demo optional (evidence or waive); does not block EV-014 close
