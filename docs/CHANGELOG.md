# Changelog

All notable user-facing and deployable changes for TAC to IWXXM.

## 2026-09-04 — Production release (pending promote)

### Added
- **Conversion profiles** — Operator editor for rule packs and signed overlays (HMAC), catalog
  inspector, and convert with selected overlay (`overlay_id`). Journey UJ-072 / F7.w.
- **Dissemination ops** — Shell UI and JWT API for plans, audit, SQL mapping, and gateway health
  (EV-936 / UJ-071).

### Changed
- API Docker image bundles `docs/domain/profiles` so the ConversionProfile catalog serves in DOKS.
- DOKS Deploy rollout pins the `alembic-upgrade` initContainer to the same backend tag as `api`.
- Staging/prod `github-actions-deploy` Role can patch Secrets and create Jobs (ops).

### Packages
- No publishable package semver bumps this promote (`tac2iwxxm` / `tac-validate` /
  `iwxxm-validate` remain **0.3.0** / **0.2.0** / **0.2.0** — coverage/tooling-only diffs).

### Deploy
- Promote PR: (open `stage` → `main`).
- After merge + tip CI green: tag `v2026.09.04-deploy` to roll production.
- Prod prerequisites: Alembic `20260903_0003` (+ earlier profile rule-pack revision if missing);
  set `PROFILE_OVERLAY_HMAC_SECRET` on prod `metar-api-secrets`.

## 2026-08-21 — Production release

Operator-facing improvements validated on staging, now promoting to production.

### Added
- **Quality metrics** — Browse official WMO IWXXM examples with match, residual, lint, and
  validate summaries (`/quality`), plus shareable detail pages with collapsible XML diffs.
- **Validation Issues Catalog** — New shell tab listing lint and IWXXM validation issues with
  plain-language descriptions, issue type, severity, and verified source links; supports
  sort/filter by category.
- **Readable IWXXM validate output** — Item-by-item decode rows on Validate IWXXM (aligned with
  other products), including optional segment/summary fields from the API.
- **AHL bulletin handling** — Decode and convert Traditional Alphanumeric Code bulletins that
  carry WMO abbreviated headings, with clear errors for malformed headings.
- **Workbench layout polish** — Product Type and Profile bars stay on one row at laptop widths
  with aligned controls.
- **Apex redirect** — `tac-to-iwxxm.com` / `www` permanently redirect to the operator app host
  (staging short host mirrors the same pattern).

### Changed
- Quality metrics compare XML with **W3C canonicalization** (fewer false diffs); IWXXM **2025-2**
  Schematron runs; schema-import warnings for 2025-2 addressed; diffs pretty-print for reading.
- Stricter **stage → production** gate: full unit suites, lint, typecheck, and full Playwright
  E2E (not smoke-only) required on the promote PR.
- Operator-facing UI, OpenAPI text, and client error messages stay free of internal planning
  jargon.

### Packages
- `tac2iwxxm` **0.2.4 → 0.3.0** (AHL-aware decode — minor: additive bulletin capability)
- `tac-validate` **0.1.3 → 0.2.0** (AHL helpers + catalog metadata — minor: new public APIs)
- `iwxxm-validate` **0.1.2 → 0.2.0** (C14N helpers + 2025-2 Schematron path — minor: new public APIs)

### Deploy
- Promote PR: [#1022](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1022) (`stage` → `main`).
- After merge + tip CI green: tag `v2026.08.21-deploy` to roll production.
- Staging tip before release prep: `61b2ccae` (Staging smoke green).
- Optional PyPI tags after checklist: `tac2iwxxm-v0.3.0`, `tac-validate-v0.2.0`,
  `iwxxm-validate-v0.2.0`.

### Provenance

| Topic | Tracking |
|-------|----------|
| Quality metrics tab / detail / C14N / 2025-2 | [#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836), [#988](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/988), [#982](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/982), [#980](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/980), [#979](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/979), [#987](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/987), [#989](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/989) |
| Apex → app redirect | [#948](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/948) |
| Strip internal refs from operator/API copy | [#951](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/951) |
| Pre-promote UX epic (decode, AHL, layout, catalog, CI gate) | [#1009](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1009), [#1010](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1010), [#1011](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1011), [#1012](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1012), [#1013](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1013), [#1014](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1014), [#1015](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1015), [#1016](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1016) |
| Validation Issues Catalog deepen | [#1017](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1017), [#1020](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/1020) |

## 2026-08-10 — Promote EV-048..EV-053 (`stage` → `main`)

### Added
- **EV-050 / F12–F15 / F20 / F23 / F24 / F28**: Offline WMO codes membership harvest +
  `tac-validate` Validated dual-profile lint (annex3 vs iwxxm_us); fixture matrix for
  RE*/cloud/phenomena/SpaceWx membership.
- **EV-051 / F30**: Tag-driven prod Deploy — `main` push runs full CI only; prod rolls on
  `vYYYY.MM.DD-deploy` (or `workflow_dispatch`).
- **EV-052 / F29 / M5 / F21**: Optional Sentry (API/FE/worker); Upstash-backed slowapi;
  openapi-typescript FE types + `openapi:check`; coverage inventory + ≥95 lines/stmts/funcs
  gates; quality sticky PR comment (product × profile).
- **EV-053 / M5**: Vitest **branches** ≥95 (FileConverter re-included); closes EV-052 branch
  waiver (#968).

### Changed
- **EV-048 / F7 / F21**: Strip internal doc refs (Corpus/ADR/EV/TC ids) from operator UI,
  OpenAPI descriptions, and client-visible error copy.
- **BUG-2026-08-10**: Remove DOKS ConfigMap mount over `work_session_service.py` (stale
  overlay caused staging `NameError: UUID` on work-sessions).

### Packages
- `tac-validate` **0.1.2 → 0.1.3** (WMO membership Validated + dual-profile).
- `tac2iwxxm` remains **0.2.4**.
- `iwxxm-validate` remains **0.1.2**.

### Deploy
- Promote PR `stage` → `main` (this release).
- Post-merge: tag `v2026.08.10-deploy`; optional PyPI `tac-validate-v0.1.3` after checklist.

## 2026-08-09 — Promote EV-043..EV-047 (`stage` → `main`)

### Added
- **F30 / EV-044**: Dedicated staging DOKS cluster + Postgres; dual-cluster promote path
  (Staging smoke + Staging gate); staging LB pin for Host-header probes.
- **EV-045**: Rust crates CI + maturin matrix for `tac2iwxxm` / `iwxxm-validate`;
  `make rust-check`.
- **EV-047 / M5**: Slim husky (`lint-fast` / `test-unit-fast`); Converter perf CI hard gate
  + committed baselines; Python package + per-file coverage ≥95% (incl. auth/worker).
- **EV-047 / F7**: Operator one-pager, handbook, and in-app Help (UJ-054).
- **Process**: Release-on-promote guidance (semver + CHANGELOG on `stage`, deploy/PyPI tags
  after merge) — ADR-034 amend; Staging-gate advisory reminder.

### Changed
- **EV-046 / F15**: `tac-validate` catalog attribution prefers stable source URL
  (`codes.wmo.int` present → cite → cover).
- **EV-043**: Staging worker default replicas `0` on single-node staging.

### Packages
- `tac-validate` **0.1.1 → 0.1.2** (URL-first attribution).
- `tac2iwxxm` remains **0.2.4** (tests/CI only this window).
- `iwxxm-validate` remains **0.1.2** (Rust clippy/format only).

### Deploy
- Promote PR [#947](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/947) (`stage` → `main`).
- Post-merge: tag `v2026.08.09-deploy`; PyPI tag `tac-validate-v0.1.2` after checklist.

## 2026-08-06 — S047 EV-039 (F16 live local SQL e2e + teardown)

### Added
- **F16 deepen**: Compose mock-byoc Postgres/MySQL/SQL Server + SQLite file path; Playwright
  `TC-F16-LIVE-*` live BYOC upload; async write assert; teardown across integration/e2e/local.
- FE dependency pin: `js-yaml` ≥4.3.1.

### Docs
- Test-plan / journeys / tech-spec harness recipe for live SQL; feature-list §F16 EV-039 ACs.

### Deploy
- PR [#891](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/891) MERGED @ `fea30aba`; post-merge
  CD [31130303373](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31130303373); historical
  CLI tag `20260806224839-7df9f8f` during GHA outage; H0c/H1/H4–H5 re-verified 2026-08-08.
- Report: [evolve-report-EV-039.md](evolve-report-EV-039.md).

## 2026-08-07 — S050 EV-042 (Hide destinations + F33 mass ingest + work queue)

### Added
- **F33**: Secure mass folder/zip ingest (`POST /api/v1/ingest/mass`) with caps, sniff,
  zip-bomb guards, dedicated body limit; signed-in only.
- **F7**: Work-queue keyboard + batch convert controls for operator throughput.

### Changed
- **F16–F19**: Operator destinations UI hidden (`destinationsEnabled=false`), including
  Convert&Send, Disseminate, and Upload to Database. Restore tracked in [#898](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/898).

### Deploy
- Live: [#899](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/899) @ `e3d1c7c8`; DOKS CD
  [31197264636](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31197264636); H0c/H1/H4–H5
  (mass) + UJ-051..053 6/6 PASS (`D-S050-13=1`).
- Report: [deploy-smoke.md](sessions/S050-remove-db-tools-operator-throughput/reports/deploy-smoke.md).

## 2026-08-06 — S048 EV-040 (Workbench lint UX + examples + prefs)

### Changed
- **F10**: Lint console lists each issue on its own line (no `+N more` truncation).
- **F7**: Convert keeps manual TAC input; **New TAC** label; action buttons above selects.
- **F7**: User preferences slimmed to display name + output extension.
- **F7.g**: Official AHL + WMO METAR A3-1 bulletin and IWXXM Collect NIL examples.
- **F15**: Lint catalog / API / FE show WMO–ICAO–IWXXM source attribution; RVR `U|D`
  tendency + AHL YYGGgg false positives fixed.

### Docs
- feature-list / api-contract / test-plan / evolve-decisions §EV-040.

## 2026-08-06 — S046 EV-038 (Epic #846 corpus residuals #849–#861)

### Added
- **F4 / F7**: IWXXM release-line SoT export → FE Latest/Previous picker (UJ-050 / #854).
- **F2 / F6 / F32**: VONA vertical-extent encode; VA-EGGX → `wmoPass`; SWXA A7-4/A7-5 samples.
- CI: codelist URI drift + iwxxm-us compat smoke workflows.

### Docs
- Release-line adoptability / coverage matrix residuals closed under epic #846.

### Deploy
- Live: [#890](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/890) @ `619a7ac3`; DOKS
  `20260806144346-619a7ac`; H1–H5 + UJ-050 PASS.
- Report: [evolve-summary.md](sessions/S046-iwxxm-corpus-residuals/reports/evolve-summary.md).

## 2026-08-05 — S040 EV-032 close (IWXXM corpus / F32 VONA)

### Added
- **F32**: VONA TAC lint → convert → XSD+SCH; FE Examples `vona_a7_1` (`wmoPass`); API
  `product=vona` (PR #848).
- **#835**: TC SIGMET A6-2-TC ADR-032 equality promoted to `wmoPass`.

### Docs
- Release-line adoptability / staff guide (#808/#847); #846 corpus children filed (epic remains open).

### Deploy
- Initial DOKS smoke @ `20260804214648-dfecba4`; re-verified on `20260805115809-d3f4bb9`.
- Report: [evolve-summary.md](sessions/S040-iwxxm-corpus-quality/reports/evolve-summary.md).

## 2026-08-05 — S042 EV-034 (F30 CD deepen — DOKS auto-rollout)

### Added
- **F30 AC7 / TC-F30-007**: `main` Deploy rolls DOKS `metar-api` / `metar-frontend` /
  `metar-worker` to the immutable `TIMESTAMP-SHA` GHCR tag via
  `scripts/deploy/doks_rollout_images.sh` and Actions secret `KUBE_CONFIG`.

### Fixed
- Deploy reject DigitalOcean `doctl` exec-auth kubeconfigs (runners lack `doctl`) — PR #868.

### Deploy
- Live proof: CI [31003268652](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/31003268652);
  tag `20260805115809-d3f4bb9`; `/health` 200.
- Reports: [evolve-summary.md](sessions/S042-doks-cd-rollout/reports/evolve-summary.md),
  [deploy-smoke.md](sessions/S042-doks-cd-rollout/reports/deploy-smoke.md).

## Unreleased — S038 EV-031 (#842 / #830 / #712 platform independence)

### Added
- **F30**: DigitalOcean Postgres product DB (`DATABASE_URL`); DOKS API + static FE + F8
  worker IaC; Alembic under `apps/backend/` (CI/deploy idempotent `upgrade head`).
- **F31**: Hybrid work sessions — guest IndexedDB + persistent loss-of-progress notice;
  optional Supabase Auth → DO Postgres `/api/v1/work-sessions*`; auto-upload on login.
- Provisional DOKS live harness (Host-header / no `/etc/hosts`):
  `make test-live-e2e-doks-provisional`, `test-live-connectivity-doks-provisional`,
  `test-live-topology-doks-provisional`.

### Changed
- Supabase = **Auth only** (JWKS-only verify); no product PostgREST / Supabase DB writers
  on default path ([ADR-033](adr/ADR-033-platform-independence-auth-do-doks.md)).
- F21 Amended — public convert retained; Auth restored for long-term storage.
- F8 worker store/quarantine → SQLAlchemy / `DATABASE_URL` (ADR-018 amend).

### Deploy
- Provisional cutover under `D-S038-t63-waive` (LB `168.144.12.70` + placeholder Hosts).
- H4–H5 + Playwright F31 + TC-EV031 topology PASS on provisional DOKS (T7.1–T7.3).
- **13-deploy-smoke** re-verify: Host-header 5/5, H0c/H4/H5, topology 3/3, pods Running,
  Render `/health` **503** — [deploy-smoke.md](sessions/S038-platform-independence-842/reports/deploy-smoke.md).
- **T6.5 / TC-F30-005**: Render API + FE + worker **suspended** (`D-S038-t65-waive` —
  soak waived day 0/7); historical URLs in
  [ops/render-decommission-archive.md](ops/render-decommission-archive.md);
  `config/prod.json` + CI Deploy retargeted to DOKS / GHCR-only (no Render hooks).
- Real public DNS + HTTPS still residual (`D-S038-t63-waive`).
- Reports: [evolve-summary.md](sessions/S038-platform-independence-842/reports/evolve-summary.md),
  [deploy-report.md](sessions/S038-platform-independence-842/reports/deploy-report.md),
  [t6.5-render-decommission.md](sessions/S038-platform-independence-842/reports/t6.5-render-decommission.md).

## 2026-08-03 — S037 EV-030 (#831 / #829 / #820 quality residuals)

### Added
- **F29**: Parameterized lint/convert/validate rule matrices under `tests/quality_matrices/`
  (METAR/SPECI pilot + inventory gate + PR smoke).

### Changed
- #829 TC SIGMET lint deepen; Examples unlock `sigmet-A6-2-TC` as **`wmoReference`**
  (equality residual → [#835](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/835)).
- #820 VAA/TCA structured `LABEL:` + AHL decode; official peers empty residuals.
- `tac2iwxxm` **0.2.4**.

### Deploy
- PR [#832](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/832) merged (`8bd111c`).
- Live smoke PASS (H0c–H5 + FE A6-2-TC seed). CI deploy hook 500 → Render REST redeploy.
  API `dep-d9ob293l550s73a65rfg` · FE `dep-d9ob2brm8hqs73fu8k2g` (`…:20260803151459-8bd111c`).
  Report: [deploy-smoke.md](sessions/S037-quality-residuals-831/reports/deploy-smoke.md).

## 2026-08-02 — S036 EV-029 (#823 eight-family AHL + F28 SWXA)

### Added
- **F28**: SWXA quality bar — registry lint, `product=swxa` API, convert →
  `iwxxm:SpaceWeatherAdvisory`, XSD+SCH, Examples unlock `spacewx-A7-3` (`wmoReference`).
- Eight-family AHL / `reportStatus` / product-order / report-state matrix smokes
  (TC-EV029-001..008).

### Changed
- Deepen F6 / F12 / F15 / F20 / F23 (incl. TC SIGMET #738) / F24 / F26 / F27 AHL and
  quality packs; `tac2iwxxm` **0.2.3**.

### Deploy
- PR [#828](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/828) merged (`4e6577a`).
- Live smoke PASS (H0c–H5 + SWXA catalog/convert + FE Examples seed).
  API `dep-d9ntlclbedkc73fvcuvg` · FE `dep-d9ntlde1egvs738ph9h0`.
  Report: [deploy-smoke.md](sessions/S036-eight-family-ahl-rules-823/reports/deploy-smoke.md).

## 2026-07-31 — S034 EV-027 (#815 official WMO decode residual matrix)

### Added
- **F25 / F9 / F7.g deepen**: Official WMO TAC peer inventory locked to catalog ∪
  `FIXTURE_GAPS`; parametrized decode residual matrix CI (happy-path → empty or
  allowlisted residuals with standing-doc intent + child issue).

### Changed
- Decode fixes for cheap residuals (RVR / CNL / VA SIGMET geometry); VAA/TCA G4
  allowlisted with child [#820](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/820).

### Deploy
- PR [#821](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/821) merged (`ad36aa0`);
  #815 closed. 13 / TC-EV027-005 waived (no FE deploy this cycle).

## 2026-07-31 — S033 EV-026 (#809 VA multi-location equality)

### Changed
- **F23 / F6 / F7**: WMO `sigmet-multi-location-VA` encoder matches vendor under annex3
  defaults (ADR-032 `canonicalize_xml` equality): calendar/ATS–MWO stamps, ring order +
  2dp coords, phenomenonTime xlink reuse.
- Examples catalog `sigmet_multi_location_va` promoted **wmoReference → wmoPass** (UJ-041).

### Deploy
- PR [#817](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/817) merged (`101f555`).
- Live smoke COMPLETE (H0c–H5 + catalog passer + VA SIGMET convert).
  API `dep-d9miestbedkc73dr3j9g` · FE `dep-d9mietnqj5pc73d3c8a0`.
  Report: [deploy-smoke.md](sessions/S033-va-multi-location-equality/reports/deploy-smoke.md).

## 2026-07-30 — S027 EV-021 (F26 VAA + F27 TCA quality)

### Added
- **F26**: VAA quality bar — registry lint, WMO `va-advisory-A7-2` golden convert,
  XSD+SCH, workbench Examples unlock (`iwxxm:VolcanicAshAdvisory`).
- **F27**: TCA quality bar — same bar for `tc-advisory-A2-2` /
  `iwxxm:TropicalCycloneAdvisory`.
- Combined `wmo-quality.yml` pack extended for VAA+TCA (S02.L1).

### Changed
- Convert path keeps multi-line VAA/TCA TAC whole (no line-split shredding).
- Examples catalog incremental unlock for VAA/TCA WMO passers (S02.M2).

### Deploy
- PR [#794](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/794) merged (`df56d1f`).
- Live smoke COMPLETE (H0c–H5 + VAA/TCA catalog/lint/convert).
  API `dep-d9lmsdflk1mc739232ug` · FE `dep-d9lmsefqj5pc739d3it0`.
  Report: [deploy-smoke.md](sessions/S027-vaa-quality/reports/deploy-smoke.md).

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
