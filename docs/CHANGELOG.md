# Changelog

All notable user-facing and deployable changes for METAR to IWXXM.

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
