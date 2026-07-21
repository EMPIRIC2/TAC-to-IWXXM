# Deploy Checklist — S019 / EV-014 (T6.5 / 12-verify-deploy delta)

> Generated: 2026-07-21  
> Status: **PASS** (docs + CI harness ready; live Render allowlist value confirm at T6.6)  
> Scope: F16–F19 dissemination — `DISSEMINATION_EGRESS_ALLOWLIST` (E14-08) + wis2box Compose harness (E14-04)  
> Branch: `cursor/s019-t64-verify-build-7820` · PR [#771](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/771)  
> CI: [29846488131](https://github.com/joseph-c-mcguire/metar-to-IWXXM/actions/runs/29846488131) **success**

## Target topology (unchanged)

| Role | Render service | Notes |
|------|----------------|-------|
| API | `metar-to-iwxxm-api` | Image deploy; holds `DISSEMINATION_EGRESS_ALLOWLIST` |
| Frontend | `metar-to-iwxxm-frontend-v4-web` | Dissemination drawer (T6.2) |
| Worker | `metar-to-iwxxm-worker` | **No** F8 auto-push; operator sinks only (F16–F19) |
| wis2box | **Compose/CI only** | Not a Render web service (E14-04=B) |

## Delta scope (this cycle)

| Surface | Change |
|---------|--------|
| `packages/dissemination` | SSRF allowlist, writer-contract, WIS2/EDIS/F19 stubs |
| `apps/backend` | Thin `/api/v1/dissemination/preflight` + `/send` |
| `apps/frontend` | Dissemination drawer |
| `docker-compose.wis2box.yml` | MQTT+HTTP harness overlay |
| Env | `DISSEMINATION_EGRESS_ALLOWLIST` (hosts/CIDRs only; never destination secrets) |

## Allowlist (E14-08 / ADR-029)

| Check | Status | Evidence |
|-------|--------|----------|
| `docs/env-contract.md` documents var + empty fail-closed | **PASS** | env-contract rows |
| `docs/config-spec.md` documents var | **PASS** | config-spec §Dissemination |
| `docs/deploy.md` Render table + Compose usage | **PASS** | deploy.md allowlist + wis2box sections |
| `docs/ops/staging-secrets-matrix.md` API row | **PASS** | matrix row (dashboard, sync: false) |
| `.env.example` placeholder | **PASS** | `DISSEMINATION_EGRESS_ALLOWLIST=` + commented harness hosts |
| Package fail-closed when empty | **PASS** | T1.3/T1.4 unit tests; CI Test (dissemination) green |
| Staging harness hosts documented | **PASS** | `wis2box,127.0.0.1,localhost` in deploy.md / `.env.example` |
| Live Render value set | **BLOCKED (T6.6)** | T6.6 agent: no `.env` `RENDER_API_KEY`; Render MCP unauthorized — still confirm non-empty allowlist (or intentional empty = deny) before live BYOC |

## Compose wis2box harness (E14-04)

| Check | Status | Evidence |
|-------|--------|----------|
| Overlay file present | **PASS** | `docker-compose.wis2box.yml` (profile `wis2box`) |
| Image build context | **PASS** | `packages/dissemination/docker/wis2box-harness/` |
| Makefile targets | **PASS** | `compose-wis2box-up/down/harness` |
| CI hook script | **PASS** | `scripts/ci/run_wis2box_harness.sh` |
| CI dissemination + integration jobs | **PASS** | PR #771 run 29846488131 — Test (dissemination) + Test (integration) success |
| Not a Render service | **PASS** | ADR-030 / deploy.md explicit |

## Connectivity readiness (stage 12 rows)

| Check | Status | Evidence |
|-------|--------|----------|
| H0c CORS unit tests | **PASS** | `tests/unit/test_cors_policy.py` 6/6 (local + CI) |
| `configure_cors` on API | **PASS** | backend |
| `scripts/deploy/verify_connectivity.sh` | **PASS** | present |
| `tests/smoke/test_staging_connectivity.py` | **PASS** | present |
| H4–H5 live | **PASS (T6.6)** | `verify_connectivity.sh` H4 2/2 + H5 config.json; FE drawer still not on live bundle until #771 |
| H6′ UJ-027–030 | **PASS (code)** | T6.3 Playwright 6/6; re-run live at 13 if needed |

## Failure modes & mitigations

| # | Risk | Mitigation | Status |
|---|------|-----------|--------|
| 1 | Empty allowlist blocks all BYOC in prod | Documented fail-closed; operator must set hosts/CIDRs for demos | accepted |
| 2 | Allowlist too broad (SSRF) | ADR-029 private/metadata deny + DNS rebinding in package | mitigated |
| 3 | Destination secrets persisted | Memory-only BYOC; `kv_upload_key` only on success | mitigated |
| 4 | Treat Compose harness as live WIS2 | Close gate still requires live BYOC (Q15/Q21) | documented |
| 5 | Deploy without FE drawer | Ship FE + API same PR (#771); H4–H5 at T6.6 | mitigated |
| 6 | F8 worker auto-push | Non-goal; worker unchanged | mitigated |

## Sign-off

| Gate | Result |
|------|--------|
| T6.5 allowlist + Compose checklist | **PASS** |
| Ready for T6.6 `13-deploy-smoke` | **PARTIAL** — connectivity PASS; BYOC/allowlist/auth still blocked |
| Live BYOC close gate (Postgres + WIS2 + EDIS) | **Blocked** — see `deploy-smoke.md` |
| F19 live demo | Optional (evidence or waive) |

## Next

**Unblock T6.6** — `.env` + merge #771 + allowlist confirm + live BYOC (TC-F17-002 / TC-F18-002).
