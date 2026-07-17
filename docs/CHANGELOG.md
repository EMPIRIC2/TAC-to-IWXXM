# Changelog

All notable user-facing and deployable changes for METAR to IWXXM.

## 2026-07-17 — S013 EV-009 (F9 live decode + F10 preview UX)

### Added
- **F9**: Value-aware TAC decode explanations for all seven products + deterministic
  plain-language `summary` on `POST /api/v1/decode-tac`; live "Plain language" block in the
  workbench decode panel (UJ-020).
- **F10**: Side-by-side IWXXM preview pane (`IwxxmPreviewPane`) with Soft-preview / Passed
  badge; `MISSING_TERMINATOR` downgraded to `info` with one-click "Add `=`" quick fix
  (UJ-021; ADR-025).

### Changed
- Decode/lint contracts additive-only (`summary`, `info` severity + `fixes[]` already present).
- No new endpoints, env vars, CORS origins, or DB migrations.

### Deploy
- PR [#723](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/723) merged; Render API +
  frontend-v4-web redeployed 2026-07-17. Smoke: H1/H0c/H3/H4/H5 + H6′ UJ-020/021 **PASS**
  (`docs/sessions/S013-live-decode-preview-ux/reports/deploy-smoke.md`).

## Unreleased — S008 EV-006 (F6 cutover + F8 worker)

### Added
- **F6 `tac2iwxxm`**: seven-product annex3 convert (AIRMET, METAR, SIGMET, SPECI, TAF, VAA, TCA)
  plus `iwxxm_us` for METAR/SPECI/TAF (thin SIGMET/AIRMET US namespace).
- **F8 `apps/worker`**: Render Background Worker poller → lint → convert → validate →
  Supabase `iwxxm_ingest_results` / `iwxxm_ingest_quarantine` (ADR-018).
- Live gates: H7 bulletin smoke (`make test-live-bulletin`), H3 convert/lint smoke,
  worker ingest table probe (T7.2–T7.4).

### Changed
- **`/api/v1/convert`** cutover from `packages/gifts` to `tac2iwxxm`; health field
  `tac2iwxxm_available` replaces `gifts_available` (PRs #706–#708; deploy pending on `main`).
- Template: `static+api` → **`static+api+worker`**.

### Removed
- `packages/gifts` (hard cutover).

### Deploy notes
- Apply `supabase/migrations/20260712000009_iwxxm_ingest_store_quarantine.sql` before enabling
  the worker (applied on staging project `ktvxijislbtgqapllmuk`).
- Worker service: `metar-to-iwxxm-worker` (Render Background Worker, docker-from-git).
- Staging API still reports `gifts_available` until cutover image lands on `main-latest`.
