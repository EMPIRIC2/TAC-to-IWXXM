# Changelog

All notable user-facing and deployable changes for METAR to IWXXM.

## 2026-07-19 — S014 EV-010 (F11 msgspec HTTP + F12–F14 packages)

### Added
- **F11**: msgspec response encode on high-churn convert/validate/lint/decode routes (ADR-026);
  Rust `iwxxm-validate` SDK path; xsdata `iwxxm_xsd` models (ADR-027).
- **F12–F14**: Publishable `tac-validate` / `iwxxm-validate` / `tac2iwxxm[+validate]` packaging
  + PyPI OIDC workflow (matrix) — first live tag blocked until Trusted Publisher ×3 configured.

### Changed
- Backend HTTP response path for operator convert/validate; FE OpenAPI/client types aligned.
- **F13**: `iwxxm-validate` Rust caches compiled XSD/Schematron (process-wide) so hot-path
  validate meets E10-35 hard 0.85× vs lxml (T6.6).
- No new CORS origins, env knobs, or DB migrations this cycle.

### Deploy
- PR [#726](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/726) merged (`c73e0ad`);
  Render API + frontend-v4-web redeployed 2026-07-19. Smoke: H0ci/H1/H0c/H3/H4/H5 + H6′ UJ-022
  **PASS** (`docs/sessions/S014-package-publish-validation/reports/deploy-smoke.md`).

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
