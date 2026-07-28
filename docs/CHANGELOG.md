# Changelog

All notable user-facing and deployable changes for METAR to IWXXM.

## 2026-07-28 — S023 EV-017 (F21 public app + F22 privacy)

### Added
- **F21**: Public unauthenticated converter — no operator login/JWT; Auth routes 404.
- **F7.h**: Work history in browser IndexedDB (local Draft/WIP/Finished); no `/api/v1/work-sessions`.
- **F22**: Privacy notice + settings (Solution A) + Global Privacy Control honor; IndexedDB
  disclosure; preferences in localStorage only.
- Abuse controls: public + dissemination rate limits (`slowapi`); request body size cap.

### Changed
- Deleted `packages/auth`; retired `DISABLE_AUTH` / `api.disableAuth` dual path.
- Live E2E / H6: no `E2E_USER_*` login fixture (`TC-F21-auth-gone`).
- Deploy + env-contract rewritten for public API + F8 worker secrets only ([deploy.md](deploy.md),
  [env-contract.md](env-contract.md)); ADR-031 Accepted (supersedes ADR-020 for operator history).

### Deploy
- Cutover PRs [#786](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/786) /
  [#787](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/787) / [#788](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/788).
- Live smoke COMPLETE (H0c–H5 + Playwright F21/F22 5/5). API Auth leftovers removed
  (`SUPABASE_URL` / `SUPABASE_SECRET_KEY`); worker service-role retained. Redeploy
  `dep-d9kii12jobas73fl4bi0`.

## 2026-07-27 — S021 EV-016 (F7.g workbench golden examples)

### Added
- **F7.g**: Pre-loaded golden examples in FileConverter (TAC / AHL / happy-path IWXXM),
  demo labeling, Vitest TC-F7-008 / UJ-032 (T0).

### Changed
- F7 remains **Planned**; F7.g deepen merged via PR
  [#782](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/782) (`c49f22b`); #780 closed.

### Deploy
- CI pushed `ghcr.io/empiric2/tac-to-iwxxm/*:20260727004311-c49f22b`; **live Render not
  updated** (still joseph GHCR paths). Live H4–H5 / UJ-032 **waived** to
  [#781](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/781)
  (`docs/sessions/S021-golden-examples-ui/reports/deploy-smoke.md`).

## 2026-07-22 — S020 EV-015 (F20 TAF + SPECI quality bar)

### Added
- **F20**: TAF + SPECI quality bar (F15 sequel) — registry deepen, accept/negative fixtures,
  Annex-3 / IWXXM-US goldens, FE catalog TAF tag filters, API catalog `product=taf|speci`.

### Changed
- Feature-list F20 → **Done**; deepens F6.b / F6.c / F12.

### Deploy
- PR [#778](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/778) merged `eae8bdc`;
  Render API+FE `…-eae8bdc`; H1–H5 + catalog taf/speci live smoke PASS
  (`docs/sessions/S020-aerodrome-quality/reports/deploy-smoke.md`).

## 2026-07-21 — S019 EV-014 (Dissemination epic F16–F19)

### Added
- **F16–F19**: Operator dissemination drawer (Convert&Send / Upload) with backend-mediated
  `POST /api/v1/dissemination/preflight` + `/send`; multi-DB writer-contract (Postgres, MySQL,
  SQL Server, SQLite); WIS2 + EDIS sinks; AMHS/SWIM/AFS staging stubs (`packages/dissemination`).
- SSRF egress allowlist (`DISSEMINATION_EGRESS_ALLOWLIST`, ADR-029); Compose wis2box CI harness.
- Playwright UJ-027–030 + `make test-mock-byoc-smoke` close-gate evidence.

### Changed
- Feature-list F16–F19 → **Done**; Q15/Q21 close gate amended to mock/harness BYOC for EV-014
  (`D-S019-EV014-Q15-mock-waive`). Live destination demos deferred (optional follow-up).
- ADR-021 amended (destination secrets memory-only); ADR-030 package/API cut.

### Deploy
- PRs [#771](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/771) /
  [#772](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/772) merged; API + frontend
  drawer live. Smoke: H0c/H1/H4/H5 + mock BYOC
  (`docs/sessions/S019-dissemination-upload/reports/deploy-smoke.md`).
- Live Render allowlist left empty (fail-closed) until operator sets exact BYOC hosts.

## 2026-07-20 — S016 EV-012 (Manual TAC Input modes validation / #730)

### Added
- Playwright **TC-F7-007** (UJ-025): Manual TAC Input modes T1–T6 (TAC / AHL / COLLECT,
  auto-switch, `.gz` COLLECT, read-only finished session).

### Changed
- Workbench: toast on convert-time AHL/COLLECT auto-switch; classify COLLECT after gzip inflate.
- Specs: UJ-025 + TC-F7-007; F7 remains **Planned**; COLLECT stays **501** (ADR-024).

### Deploy
- PR [#746](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/746) merged (`37be5f8`);
  Render API + frontend-v4-web redeployed 2026-07-20. Smoke: H0ci/H0c/H3/H4/H5 + AHL + COLLECT
  501 + live workbench **PASS** (`docs/sessions/S016-manual-tac-input-modes/reports/deploy-smoke.md`).

## 2026-07-20 — S015 EV-011 (F15 METAR lint registry + #732 quality)

### Added
- **F15**: Maintainable `tac-validate` issue registry (`IssueSpec` / SCREAMING_SNAKE codes +
  `info`|`warning`|`error`); docs/JSON catalog with CI drift gates; R1–R8 METAR/SPECI accept +
  negative fixtures; `GET /api/v1/lint-issue-catalog` + workbench catalog tooltips/panel (ADR-028).
- Convert goldens: expanded Annex-3 / IWXXM-US METAR/SPECI (AUTO/CAVOK/COR adjacency) + R6/R7 tests.

### Changed
- Deepened **F6** / **F12** METAR/SPECI lint and convert fidelity; coverage-matrix R1–R8 closed.
- No new CORS origins, env knobs, or DB migrations this cycle.

### Deploy
- PR [#742](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/742) merged (`b405a96`);
  Render API + frontend-v4-web redeployed 2026-07-20. Smoke: H0ci/H1/H0c/H3/H4/H5 + F15 catalog
  **PASS** (`docs/sessions/S015-metar-lint-quality/reports/deploy-smoke.md`).
- PyPI `tac-validate-v0.1.1` deferred (follow-up).

## 2026-07-19 — S014 EV-010 (F11 msgspec HTTP + F12–F14 packages)

### Added
- **F11**: msgspec response encode on high-churn convert/validate/lint/decode routes (ADR-026);
  Rust `iwxxm-validate` SDK path; xsdata `iwxxm_xsd` models (ADR-027).
- **F12–F14**: Publishable `tac-validate` / `iwxxm-validate` / `tac2iwxxm[+validate]` packaging
  + PyPI OIDC workflow (matrix); **0.1.0** live on PyPI (token bootstrap; OIDC for later tags).

### Changed
- Backend HTTP response path for operator convert/validate; FE OpenAPI/client types aligned.
- **F13**: `iwxxm-validate` Rust caches compiled XSD/Schematron (process-wide) so hot-path
  validate meets E10-35 hard 0.85× vs lxml (T6.6).
- No new CORS origins, env knobs, or DB migrations this cycle.

### Deploy
- PR [#726](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/726) merged (`c73e0ad`);
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
- PR [#723](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/723) merged; Render API +
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
