"""Every bug report keeps a regression file that still exists.

Renamed and relocated repros are listed here so a deleted test fails this check.
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

# Reports whose repro file name does not match the report slug.
_OVERRIDES = {
    "BUG-2026-06-21-logout-failed-production": (
        "tests/bugs/test_bug_2026_06_21_logout_missing_auth_header.py"
    ),
    "BUG-2026-06-22-admin-e2e-user-approvals-heading": (
        "apps/frontend/src/app/components/admin/AdminDashboard.test.tsx"
    ),
    "BUG-2026-06-22-issue-594-cor-traceability": (
        "tests/bugs/test_bug_2026_06_22_issue_594_cor_after_time.py"
    ),
    "BUG-2026-06-25-docker-db-connect-localhost-5432": (
        "tests/bugs/test_bug_2026_06_25_docker_db_connect.py"
    ),
    "BUG-2026-06-25-prod-disable-auth-work-session-502": (
        "tests/bugs/test_bug_2026_06_25_prod_auth_bypass_non_uuid.py"
    ),
    "BUG-2026-06-25-work-session-soft-delete-rls-42501": (
        "tests/bugs/test_bug_2026_06_25_work_session_soft_delete_rls.py"
    ),
    "BUG-2026-07-12-convert-bulletin-product-profile": (
        "apps/backend/tests/unit/test_bug_2026_07_12_convert_bulletin_product_profile.py"
    ),
    "BUG-2026-07-12-convert-metar-gate-blocks-f6": (
        "apps/backend/tests/unit/test_bug_2026_07_12_convert_metar_gate_blocks_f6.py"
    ),
    "BUG-2026-07-12-result-card-dismiss": (
        "apps/frontend/src/test/bug-2026-07-12-result-card-dismiss.test.tsx"
    ),
    "BUG-2026-07-12-validate-tac-convert-ignores-profile": (
        "apps/backend/tests/unit/test_bug_2026_07_12_validate_tac_convert_ignores_profile.py"
    ),
    "BUG-2026-07-15-empty-bearer-lint-tac": (
        "apps/frontend/src/test/bug-2026-07-15-empty-bearer-lint-tac.test.tsx"
    ),
    "BUG-2026-08-10-staging-work-session-uuid-nameerror": (
        "tests/bugs/test_bug_2026_08_10_staging_work_session_ssl_fix_mount.py"
    ),
    "BUG-2026-08-31-e2e-full-promote": "apps/e2e/metar-work-history.e2e.spec.ts",
    "BUG-2026-09-08-authenticated-save-failed-wrong-target": (
        "apps/frontend/src/hooks/useWorkSessionSync.test.ts"
    ),
    "BUG-2026-09-08-invalid-convert-error-log-missing": "apps/frontend/src/utils/api.test.ts",
}

# The profile editor page that dropped cached lists was removed.
_RETIRED = {
    "BUG-2026-09-05-profile-editor-retains-catalog-on-partial-reload",
    "BUG-2026-09-05-profile-editor-retains-pack-overlay-lists-on-partial-reload",
}
_RETIRED_PAGE = "apps/frontend/src/app/components/ConversionProfilePage.tsx"


def test_bug_log_each_report_has_a_repro_file() -> None:
    missing: list[str] = []
    for report in sorted((_ROOT / "docs/bug-reports").glob("BUG-*.md")):
        if report.stem in _RETIRED:
            if (_ROOT / _RETIRED_PAGE).exists():
                missing.append(f"{report.stem} returned {_RETIRED_PAGE}")
            continue
        relative = _OVERRIDES.get(
            report.stem,
            "tests/bugs/test_" + report.stem.replace("-", "_").lower() + ".py",
        )
        if not (_ROOT / relative).is_file():
            missing.append(f"{report.stem} -> {relative}")
    assert missing == []
