# E2E Behavior Report — S011 M6 / T6.2 (10-e2e)

> **Generated**: 2026-07-14  
> **Skill**: 10-e2e (delta — EV-008 / F7 focus TC-F7-001–006)  
> **Session**: S011-f7-operator-ui / EV-008  
> **Branch**: `evolve/S011-f7-operator-ui`  
> **Mechanism**: mixed (API/TestClient + Vitest; Playwright T2 skipped on host)

## Summary

| # | Journey / TC | Mechanism | Tier | Status | Notes |
|---|--------------|-----------|------|--------|-------|
| 1 | UJ-013 / TC-F7-001 Workbench shell | Vitest + Playwright spec present | T0 / T2 | T0 PASS; T2 SKIPPED | Spec: `apps/e2e/f7-live-workbench.e2e.spec.ts` |
| 2 | UJ-015 / TC-F7-002 Decode-tac | pytest API + package decode | T0 | PASS | 52-case F7 focus batch includes decode matrix |
| 3 | UJ-016 / TC-F7-003 Failed-TAC + preview | pytest + Vitest cues | T0 | PASS | `test_tc_f7_003_*`, FailedTacCue / SoftPreviewControl |
| 4 | UJ-017 / TC-F7-004 Live workbench | Vitest + Playwright spec | T0 / T2 | T0 PASS; T2 SKIPPED | Debounce/Abort covered in FE tests (T4.4) |
| 5 | UJ-018 / TC-F7-005 Unified sessions | pytest | T0 | PASS | `test_tc_f7_005_unified_sessions.py` |
| 6 | UJ-019 / TC-F7-006 Admin removed | pytest API + Playwright negative | T0 / T2 | T0 PASS; T2 SKIPPED | Spec: `admin-navigation.e2e.spec.ts` |

| Tier | Result |
|------|--------|
| **T0** (in-process / Vitest / TestClient) | **PASS** — TC-F7-001–006 covered at API/unit/component level |
| **T1** (compose integration) | **SKIPPED** — ports 18000/18001 + Docker disk (same as T6.1) |
| **T2 connectivity** (H4–H5) | **DEFERRED** — T6.4 |
| **T2 Playwright browser** | **SKIPPED** — would `AUTO_KILL` vecinita listeners on 18000/18001; disk 100% used |
| **T3 live** | **Not run** — evolve tip not deployed; reserved for 13/15 |

**Overall: pass_with_advisories** (T0 green; browser/compose deferred with host-env evidence)

## T0 evidence — F7 pytest focus

```bash
uv run pytest \
  tests/unit/test_cors_policy.py \
  apps/backend/tests/unit/test_tc_f7_002_decode_tac_unit.py \
  apps/backend/tests/unit/test_tc_f7_003_convert_preview_unit.py \
  apps/backend/tests/unit/test_tc_f7_005_unified_sessions.py \
  apps/backend/tests/unit/test_admin_routes_removed.py \
  packages/tac2iwxxm/tests/test_decode_tac.py \
  -v --no-cov
# → 52 passed
```

Additional T0 from full QA unit run: backend 1162, FE 590 (includes FileConverter soft-preview / Failed-TAC live paths).

### Journey details (T0)

#### TC-F7-002 Decode-tac
- Multipart route, product required, 7-product well-formed, golden METAR/SPECI/TAF segments — PASS

#### TC-F7-003 Soft-preview
- `preview=true` → 200 + `failed_spans` + XML; hard fail when preview off; JSON/file paths — PASS

#### TC-F7-005 Sessions
- Non-METAR Draft GET; My METARs excludes TAF; workbench lists all; migrate SQL product defaults — PASS

#### TC-F7-006 Admin gone
- Product `/admin/*` → 404 — PASS

#### TC-F7-001 / 004 (component)
- Vitest FileConverter / workbench console / live IWXXM default off; Failed-TAC cue — PASS  
- Playwright specs exist but not executed on this host

## Playwright skip rationale (blocking host, not product)

| Evidence | Detail |
|----------|--------|
| Listeners | `vecinita-agent-dev` → `:18000`, `vecinita-embedding-dev` → `:18001` |
| Disk | `/` 97G/97G, ~686MB free — Docker compose unreliable |
| Config | `apps/e2e/playwright.config.ts` webServer uses `AUTO_KILL_PORTS=true` — would disrupt vecinita |

**Waiver for T6.2:** browser T2 re-run in CI on PR tip and/or T6.4 after ports/disk free. Do **not** mark product E2E FAIL.

## Stale admin E2E modules (for 11)

| Spec | Issue |
|------|-------|
| `auth.e2e.spec.ts` | Still asserts admin dashboard login |
| `workflow-theme-persistence.e2e.spec.ts` | Selects `admin` view |
| `00-preflight.e2e.spec.ts` | Admin credential framing |

TC-F7-006 negative spec is correct; full-suite Playwright still needs retirement of above before green all-e2e.

## Mapping check

| UJ | Feature | Spec | T0 module | Playwright |
|----|---------|------|-----------|------------|
| UJ-013 | F7 | TC-F7-001 | FE FileConverter / f7 vitest paths | `f7-live-workbench.e2e.spec.ts`, `f7-ui-api-connections.e2e.spec.ts` |
| UJ-015 | F7 | TC-F7-002 | `test_tc_f7_002_*`, `test_decode_tac.py`, `test_f7_ui_connection_integration.py` | `f7-ui-api-connections.e2e.spec.ts` |
| UJ-016 | F7 | TC-F7-003 | `test_tc_f7_003_*`, FailedTacCue tests, `test_f7_ui_connection_integration.py` | `f7-ui-api-connections.e2e.spec.ts` |
| UJ-017 | F7 | TC-F7-004 | FE live debounce tests | `f7-live-workbench.e2e.spec.ts`, `f7-ui-api-connections.e2e.spec.ts` |
| UJ-018 | F7 | TC-F7-005 | `test_tc_f7_005_*`, `test_f7_ui_connection_integration.py` | `f7-ui-api-connections.e2e.spec.ts` |
| UJ-019 | F7 | TC-F7-006 | `test_admin_routes_removed.py` | `admin-navigation.e2e.spec.ts` |

## Handoff to 11-verify-impl

- Accept T0 PASS as gate for F7 acceptance review; track Playwright/CI as advisory until T6.4.  
- Confirm QA-001 committed before evolve→main.  
- Optionally schedule stale-admin e2e cleanup before full `make tests:e2e`.
