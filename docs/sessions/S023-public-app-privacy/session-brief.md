---
session_id: S023-public-app-privacy
type: feature
status: completed
branch: evolve/EV-017-public-app-privacy
started_at: 2026-07-27
completed_at: 2026-07-28
intent: "Remove end-user auth; public/stateless converter; IndexedDB local F5/F7 history; privacy-minimizing preference center + GPC (#783)"
orchestrator: 16-evolve
evolve_cycle_id: EV-017
github_issue: 783
close_decision_id: D-S023-close
pr_url: https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/790
pr_status: open
do_not_auto_merge: true
context_briefs:
  - docs/context/public-app-privacy.md
standing_docs_touched:
  - docs/feature-list.md
  - docs/spec.md
  - docs/api-contract.md
  - docs/test-plan.md
  - docs/user-journeys.md
  - docs/env-contract.md
  - docs/decisions/evolve-decisions.md
  - docs/adr/
prior_session: S022-rename-cutover
---

# Session S023 — public-app-privacy

## Intent

Make the operator product **public and unauthenticated**: remove login / JWT gates for
convert → validate → download/send, replace server-side F5/F7 session ownership with
**browser-local IndexedDB** work history, and ship a **privacy-minimizing** preference
center (Solution A — no non-essential tracking) with GPC recognition
([#783](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/783)).

## Prior session

| Item | Disposition |
|------|-------------|
| S022 / #781 | **Completed** — Empiric2 GHCR/Render live; UJ-032 PASS |
| S021 / EV-016 | **Completed** — F7.g goldens on `main` |
| Issue #783 | **Open** — auth removal + CA/US/EU cookie consent |

## Intake decisions (Phase 0 — **locked** 2026-07-27)

| ID | Decision |
|----|----------|
| E17-1 | Open `S023-public-app-privacy` → 16-evolve / **EV-017** |
| E17-2 | Architecture baseline **with tweaks** (Batch 2) |
| E17-3 | Routing **Standard** |
| E17-4 | **F21** + **F22**; deepen F5/F7 IndexedDB; deprecate operator **M4** |
| E17-5 | Legacy rows: no public API; ~30-day archive then delete |
| E17-6 | Baseline abuse controls **in this cycle** |
| E17-7 | Privacy Solution A + settings page + first-visit notice + GPC |
| E17-8 | Auth model **1** — public + local history |
| E17-9 | No non-essential tracking |
| E17-10 | Local history **before** auth teardown |
| E17-11 | UI preview deferred to **11-verify-impl** |
| AskQuestion | Unavailable — written interview waive |

## Classification

| Field | Value |
|-------|-------|
| Session type | **`feature`** |
| Orchestrator | **16-evolve** (EV-017) |
| Preset | **Standard** |
| Branch | `evolve/EV-017-public-app-privacy` |
| Fn allocation | **F21**, **F22**, F5/F7 deepen, M4 deprecate |

## Scope (Phase 0 **approved**)

### In

- Public app model + ADR; IndexedDB F5/F7 + export/import
- Strip frontend auth UX and JWT from public operator routes
- Backend `/auth/*` + operator auth teardown; retire `DISABLE_AUTH` dual path
- Baseline public API abuse controls; keep dissemination SSRF/allowlist
- Storage inventory; Privacy settings + notice; GPC; Solution A
- Corpus + E2E (retire/repurpose UJ-003; public convert journeys)
- ~30-day legacy session archive then drop; no public access to old rows

### Out

- Legal advice / formal DPIA
- Removing F8 worker service-role credentials
- Reintroducing admin role UX (#697)
- Per-US-state UI variants; CMP; analytics (Solution B/C)
- Cross-device history sync / optional accounts / anonymous server sessions (v1)

## UI reference

Deferred to **11-verify-impl** (E17-11).

## Routing plan

See [routing-plan.md](./routing-plan.md).

## Links

- Issue: [#783](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/783)
- Related: #697 (admin/BYO), F5/F7/M4, ADR-018/021/029
- Prior F5 context: [metar-work-history.md](../../context/metar-work-history.md)
- Standing: [feature-list.md](../../feature-list.md), [spec.md](../../spec.md),
  [api-contract.md](../../api-contract.md), [env-contract.md](../../env-contract.md)
