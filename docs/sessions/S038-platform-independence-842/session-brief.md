---
session_id: S038-platform-independence-842
type: feature
status: in_progress
branch: evolve/EV-031-platform-independence-842
started_at: 2026-08-03
intent: "Epic #842 platform independence — strip remaining Supabase (#830) and schedule/plan Render→DOKS hosting (#712) with IaC in-cycle."
orchestrator: 16-evolve
evolve_cycle_id: EV-031
github_issues:
  - 842
  - 830
  - 712
prior_session: S037-quality-residuals-831
context_briefs:
  - docs/context/platform-independence-842.md
standing_docs_touched: []  # filled after 01/04
feature_ids: [F30, F31]
feature_note: "D-S038-fn — F30 platform Auth/DB/DOKS + F31 hybrid sessions; deepen F5/F7/F8/F21/F22/M4"
ask_question: written interview — D-S038-open=3,1,1,1; doks=3; f8=1; route=1; auth=1+long-term; sessions=1+guest-notice+privacy; 830=1; fn=1,1,1
ui_preview: accepted — non-deployed local Vite http://127.0.0.1:5173/ (not staging/production)
open_commit: d286bfb
---

# Session S038 — platform-independence-842

## Intent

Reduce platform lock-in under epic [#842](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/842):

| Order | Issue | Focus |
|------:|-------|--------|
| 1 | [#830](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/830) | **Amend:** strip Supabase **data** plane; keep Supabase **Auth only** |
| 2 | [#712](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/712) | **Full production** Render → DOKS cutover (`D-S038-doks-depth`=3) |
| — | Product | Reintroduce login for **long-term** work storage; guests = local only + loss notice + privacy |

## Prior session

| Item | Disposition |
|------|-------------|
| S037 / EV-030 | **Completed** — #831/#829/#820 closed; PR #832 |

## Scope (Phase 0 locked)

| ID | Decision |
|----|----------|
| `D-S038-open` | **3,1,1,1** — full epic + IaC; general; Standard; local UI |
| `D-S038-doks-depth` | **3** — prod cutover; Render decommission after soak |
| `D-S038-f8` | **1** — F8 on **DigitalOcean Postgres** |
| `D-S038-route` | **1** — Standard approved |
| `D-S038-auth-model` | **1** — Reintroduce operator **Supabase Auth**; purpose = **long-term storage** (amend/supersede F21 public-only) |
| `D-S038-session-store` | **1** — Logged-in: work sessions on **DO Postgres** (user id from Supabase). Guests: **local/IndexedDB only** + UI notice they will lose progress if not logged in; must integrate with **F22 privacy / cookie preferences** |
| `D-S038-830-amend` | **1** — Rewrite #830 acceptance: Auth-kept, data-plane stripped |

### Topology

```
Guest (no login)  → IndexedDB / local only + loss notice (honor privacy prefs)
Logged-in         → Supabase Auth JWT → API verifies Auth → DO Postgres work sessions
F8 worker         → DATABASE_URL → DigitalOcean Postgres (no Supabase DB)
Deployables       → DOKS (API + worker + static); Render retired after soak
Supabase          → Auth + JWT verification ONLY (no app tables / PostgREST product data)
```

### In

1. Amend #830; keep Supabase Auth; move all product DB to DO Postgres
2. Hybrid sessions UI (guest local + notice; auth for long-term); privacy-preference interplay
3. Reintroduce auth library / `/auth/*` as needed (ADR-031 supersession)
4. DOKS IaC + production cutover + Render decommission runbook
5. F8 writers → DO Postgres; corpus/ADR/deploy/smoke updates

### Out

- Convert/validate engine rewrites
- Supabase hosted Postgres / PostgREST for product data
- Long-lived dual production hosts after soak

## Routing

**Preset:** Standard — see [routing-plan.md](routing-plan.md).

## UI preview

**Accepted** — [http://127.0.0.1:5173/](http://127.0.0.1:5173/) (non-deployed).

## Progress

- **00-context** completed · **Fn** `D-S038-fn` = 1,1,1 · open commit `d286bfb`
- **16-evolve** Phase 1 → **01-requirements** (delta)
- **01-requirements**: Feature List, Spec, UJ-045..048, Test Plan, config/env, API, deploy,
  deps, ADR-033, migration note drafted (`D-S038-tp` = 1,1,1)
- **Next**: Confirm lean doc pass / gaps → Gate A → **02-verify-plan**
