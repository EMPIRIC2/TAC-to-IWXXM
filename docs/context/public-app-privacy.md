# Context — Public app + local history + privacy (#783)

> **Mode**: scoped | **Slug**: public-app-privacy | **Generated**: 2026-07-27  
> **Feature / workflow**: Remove end-user auth; IndexedDB work history; privacy preference center  
> **Status**: active | **Session**: S023 / EV-017  
> **Issue**: [#783](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/783)

## Executive Summary

Product direction: operate **without accounts**. Recommended architecture (user Phase 0
baseline, tweaks pending):

| Pillar | Choice |
|--------|--------|
| Work history | **Browser IndexedDB** (UUID per item; export/import JSON; no sync v1) |
| Operator APIs | **Public + stateless** with rate/size/timeout/SSRF/allowlist controls |
| Legacy server sessions | **No public access**; migrate/archive after period |
| Tracking | **Solution A** — no non-essential analytics/marketing |
| Consent UX | One **global** preference center + GPC; disclose IndexedDB |
| Machine auth | **F8 service-role** stays private (not operator JWT) |

Sequence: **local history before auth teardown** to avoid exposing `tac_work_sessions`.

## Resolution Log

| ID | Category | Decision |
|----|----------|----------|
| R1 | Decision | Open S023 / EV-017 for #783 (E17-1) |
| R2 | Decision | Architecture baseline with tweaks (E17-2) |
| R3 | Decision | Routing **Standard** (E17-3) |
| R4 | Decision | **F21** + **F22**; deepen F5/F7 IndexedDB; deprecate operator M4 (E17-4) |
| R5 | Decision | Legacy rows: no public API; ~30-day archive then delete (E17-5) |
| R6 | Decision | Baseline abuse controls in this cycle (E17-6) |
| R7 | Decision | Privacy Solution A + settings + notice + GPC (E17-7) |
| R8 | Decision | Auth model = public + local history (E17-8) |
| R9 | Decision | No non-essential tracking (E17-9) |
| R10 | Decision | Local history before auth teardown (E17-10) |
| R11 | Decision | UI preview → 11-verify-impl (E17-11) |

## Related corpus / context

- Prior F5 (server JWT sessions): [metar-work-history.md](metar-work-history.md) — **supersede model**
- F7 operator UI: [f7-operator-ui.md](f7-operator-ui.md)
- Auth collapse M4 / #697 admin removal
- ADR-018 (worker JWT), ADR-021/029 (dissemination memory-only credentials)

## Connectivity

H4–H5: public convert without login; Privacy settings journey; retire JWT-gated UJ-003
as primary path (or mark superseded).
