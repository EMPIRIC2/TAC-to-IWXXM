# Documentation Archive

This folder contains outdated, historical, or superseded documentation that is kept for historical reference and project tracking only.

## Archive Structure

### `/ARCHIVE/phase2/`
Phase 2 project completion documentation (initial phase of the metar-to-IWXXM project).

**Contents:**
- `PHASE2_COMPLETION_REPORT.md` - Phase 2 final report
- `PHASE2_FINAL_SUMMARY.md` - Phase 2 deliverables summary
- `PHASE2_QUICKSTART.md` - Phase 2 setup and usage guide
- `PHASE2_STATISTICS_IMPLEMENTATION.md` - Phase 2 metrics and statistics

### `/ARCHIVE/sprint-reports/`
Sprint cycle documentation tracking project progress and sprint completions.

**Contents:**
- `SPRINT_STATUS_REPORT.md` - Sprint status report
- `SPRINT_3_COMPLETION_SUMMARY.md` - Sprint 3 summary
- `SPRINT_3_FINAL_REPORT.md` - Sprint 3 final report
- `SPRINT2_COMPLETE.txt` - Sprint 2 completion notice
- `SPRINT2_IMPLEMENTATION_SUMMARY.md` - Sprint 2 implementation details
- `SPRINT2_QUICK_START.md` - Sprint 2 quick reference
- `SPRINT2_TEST_FIXES.md` - Sprint 2 test improvements

### `/ARCHIVE/sessions/`
Development session tracking and project status snapshots.

**Contents:**
- `SESSION_SUMMARY.md` - Development session summary
- `PROJECT_PROGRESS_VISUAL.txt` - Visual project progress tracking
- `PROJECT_STATUS.md` - Project status snapshots

### `/ARCHIVE/backend/` (Added Feb 16, 2026)
Backend development artifacts, analysis scripts, and historical test reports.

**Contents:**
- `phase-completions/` - Phase 2/3 completion docs, test summaries
- `test-reports/` - Historical test failure reports and analyses
- `diagnostics/` - Diagnostic scripts and implementation tracking
- `analysis-scripts/` - One-off analysis and debugging utilities
- See [backend/README.md](backend/README.md) for detailed contents

### `/ARCHIVE/old-root-docs/` (Added Feb 16, 2026)
Previously scattered documentation from project root, consolidated from `.archived-docs/`.

**Contents:**
- API status and versioning documentation
- Configuration structure guides
- Implementation summaries and completion notes
- Testing and CI/CD guides
- Verification checklists

### `/ARCHIVE/ROOT_CLEANUP_RECOMMENDATIONS.md` (Added Feb 16, 2026)
The cleanup recommendations document that guided the February 2026 archive reorganization.

### `/ARCHIVE/scripts/db-debug-fixes/` (Added Feb 16, 2026)
Historical database debugging, fixing, and diagnostic scripts from `/scripts/`.

**Contents:**
- Admin user approval fixes and debugging scripts
- RLS (Row Level Security) emergency fixes and policy corrections
- Trigger management and debugging utilities
- Database audit and diagnostic scripts
- See [scripts/db-debug-fixes/README.md](scripts/db-debug-fixes/README.md) for detailed contents

**Note**: Active scripts remain in `/scripts/` organized into `launchers/`, `db-setup/`, and `utilities/` subdirectories.

### `/ARCHIVE/pre-monorepo-deploy/` (Added 2026-06-20)

Three-service Render layout, separate auth deployable, submodule clone instructions, and
Loki/Prometheus/Grafana observability docs — superseded by monorepo migration (M11, T11.3).

**Successor docs:** [deploy.md](../deploy.md), [DEVELOPMENT.md](../DEVELOPMENT.md),
[staging-secrets-matrix.md](../staging-secrets-matrix.md), [ADR-002](../adr/ADR-002-auth-merged-into-backend.md).

See [pre-monorepo-deploy/README.md](pre-monorepo-deploy/README.md) for the file index.

## Superseded Architecture Docs

**SUPABASE_AUTH_IMPLEMENTATION.md** (in SUBABASE_AUTH_IMPLEMENTATION.md)
- **Reason**: Direct Supabase integration (pre-middleware)
- **Successor**: [DEVELOPMENT.md](../DEVELOPMENT.md), [ADR-002](../adr/ADR-002-auth-merged-into-backend.md)

**SUPABASE_AUTH_QUICKSTART.md**
- **Reason**: Quick start for direct Supabase integration
- **Successor**: [DEVELOPMENT.md](../DEVELOPMENT.md)

**AUTH_MIDDLEWARE_ARCHITECTURE.md** (moved to `pre-monorepo-deploy/`)
- **Reason**: Separate auth proxy service (three deployables)
- **Successor**: Auth merged into `apps/backend` per ADR-002

## Active Documentation

- **api-contract.md** — REST API reference
- **deploy.md** — Render deployment and connectivity runbook
- **DEVELOPMENT.md** — Local setup and testing
- **SUPABASE_INTEGRATION.md** — Database connection and pooling
- **SUPABASE_EMAIL_TEMPLATES.md** — Email template configuration

## For New Developers

Start with [DEVELOPMENT.md](../DEVELOPMENT.md) for setup and [deploy.md](../deploy.md) for
production deployment.
