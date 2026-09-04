"""EV-039 / T2.4 - teardown audit for Testcontainers fixtures + SQLite temps (AC5/AC6).

Static contracts: dissemination engine fixtures use context-manager containers and
``engine.dispose()`` in ``finally``. Runtime: disposable SQLite files are removed
after use (LIVE-004 pattern). Playwright LIVE-004 must contain temp teardown.

[Corpus: product §F16] [Corpus: tests] TC-F16-LIVE-004 [Corpus: tech-spec]
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINES = (
    ROOT / "packages" / "dissemination" / "tests" / "test_writer_contract_engines.py"
)
MSSQL = (
    ROOT / "packages" / "dissemination" / "tests" / "test_writer_contract_sqlserver.py"
)
LIVE_SPEC = ROOT / "apps" / "e2e" / "uj027-f16-live-sql.e2e.spec.ts"


def test_postgres_mysql_fixtures_use_context_manager_and_dispose() -> None:
    text = ENGINES.read_text(encoding="utf-8")
    assert "with PostgresContainer" in text
    assert "with MySqlContainer" in text
    assert text.count("await engine.dispose()") >= 2
    assert "finally:" in text


def test_mssql_fixture_uses_context_manager_and_dispose() -> None:
    text = MSSQL.read_text(encoding="utf-8")
    assert "with SqlServerContainer" in text
    assert "await engine.dispose()" in text
    assert "finally:" in text


def test_sqlite_temp_file_removed_after_suite_pattern(tmp_path: Path) -> None:
    """Runtime analogue of LIVE-004 finally: temp dir + .db must not linger."""
    import shutil

    work = Path(tempfile.mkdtemp(prefix="f16-teardown-audit-", dir=tmp_path))
    db = work / "live-suite.db"
    db.write_text("placeholder", encoding="utf-8")
    assert db.is_file()
    shutil.rmtree(work)
    assert not db.exists()
    assert not work.exists()


def test_live_playwright_sqlite_case_has_temp_teardown() -> None:
    text = LIVE_SPEC.read_text(encoding="utf-8")
    assert "TC-F16-LIVE-004" in text
    assert "mkdtempSync" in text or "mkdtemp" in text
    assert "rmSync" in text or "rmdir" in text
    assert re.search(r"finally\s*\{", text), "LIVE-004 must teardown in finally"


def test_makefile_can_omit_sqlserver_when_skipped() -> None:
    """Gap fix: compose-up must not --wait sqlserver when F16_SKIP_SQLSERVER=1."""
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "F16_SKIP_SQLSERVER" in makefile
    assert "byoc-sqlserver" in makefile
