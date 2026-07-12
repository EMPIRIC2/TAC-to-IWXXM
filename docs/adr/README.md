# Architecture Decision Records

## Index

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](ADR-001-vendor-snapshots-for-iwxxm.md) | Vendor snapshots for authoritative iwxxm schemas | Accepted |
| [ADR-002](ADR-002-auth-merged-into-backend.md) | Merge auth microservice into backend API | Accepted |
| [ADR-003](ADR-003-big-bang-monorepo-migration.md) | Big-bang monorepo migration | Accepted |
| [ADR-004](ADR-004-manual-gifts-sync.md) | Manual GIFTs upstream merges | Deprecated (ADR-014) |
| [ADR-005](ADR-005-runtime-toolchain-pins.md) | Runtime and toolchain pins (Python 3.12, Node 22) | Accepted |
| [ADR-006](ADR-006-render-topology-simplification.md) | Render topology simplification (static frontend, no observability pservs) | Accepted |
| [ADR-007](ADR-007-universal-coverage-gate.md) | Universal 95% coverage gate | Accepted |
| [ADR-008](ADR-008-f3-airport-ui-exposure.md) | F3 airport UI exposure | Accepted |
| [ADR-009](ADR-009-live-test-harness.md) | Live test harness (manual H3–H6, LIVE_* env) | Accepted |
| [ADR-010](ADR-010-supabase-keys-config-split.md) | Supabase publishable/secret keys and runtime config split | Accepted |
| [ADR-011](ADR-011-work-sessions-data-access.md) | Work sessions data access via Supabase JWT client | Accepted |
| [ADR-012](ADR-012-metar-work-sessions-retention.md) | METAR work session retention and pg_cron jobs | Accepted |
| [ADR-013](ADR-013-tac2iwxxm-package-architecture.md) | New `tac2iwxxm` package, IWXXM-US vendor pin, FAA five v1 | Partially superseded (ADR-014) |
| [ADR-014](ADR-014-tac2iwxxm-rust-gifts-removal.md) | Rust/PyO3, F6 +VAA/TCA, delete gifts on cutover | Accepted |
| [ADR-015](ADR-015-validate-packages-bulletin-api-f7-f8.md) | Validate packages, bulletin API, deferred F7/F8, H7 | Accepted (F8 deferral amended by ADR-018) |
| [ADR-016](ADR-016-msgspec-subsecond-perf.md) | msgspec in packages, pydantic at HTTP, sub-second benches | Accepted |
| [ADR-017](ADR-017-pyo3-cutover-gate.md) | PyO3 required before F6 cutover (amends ADR-014) | Accepted |
| [ADR-018](ADR-018-f8-worker-template.md) | F8 Render worker + template static+api+worker (amends ADR-015) | Accepted |

## Process

ADRs are created during requirements and tech planning when a decision affects multiple
components or is difficult to reverse. Status: Proposed → Accepted → Deprecated.
