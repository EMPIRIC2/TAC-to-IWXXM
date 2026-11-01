"""Unit tests for scripts/ci/check_file_budget.py (ADR-056 / EV-file-budget-complexity)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from tests.scripts.conftest import load_script


@pytest.fixture
def budget() -> Any:
    """Load the file-budget checker module under test."""
    return load_script("ci/check_file_budget.py", "check_file_budget_under_test")


@pytest.mark.unit
def test_load_allowlist_missing(
    budget: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing allowlist file yields an empty set."""
    monkeypatch.setattr(budget, "ALLOWLIST_PATH", tmp_path / "missing.txt")
    assert budget.load_allowlist() == set()


@pytest.mark.unit
def test_load_allowlist_strips_comments(
    budget: Any, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Comments and blanks are ignored; paths normalize to POSIX."""
    path = tmp_path / "allow.txt"
    path.write_text(
        "# hdr\n\napps/a.py  # 900\npackages\\b.ts\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(budget, "ALLOWLIST_PATH", path)
    assert budget.load_allowlist() == {"apps/a.py", "packages/b.ts"}


@pytest.mark.unit
def test_is_excluded_generated_and_ui(budget: Any, tmp_path: Path) -> None:
    """Generated OpenAPI, iwxxm_xsd, and shadcn ui paths are excluded."""
    root = tmp_path
    (root / "apps/frontend/src/generated").mkdir(parents=True)
    openapi = root / "apps/frontend/src/generated/openapi.d.ts"
    openapi.write_text("x\n", encoding="utf-8")
    assert budget.is_excluded(openapi, root)

    xsd = root / "packages/shared/src/metar_shared/iwxxm_xsd/v1/foo.py"
    xsd.parent.mkdir(parents=True)
    xsd.write_text("x\n", encoding="utf-8")
    assert budget.is_excluded(xsd, root)

    ui = root / "apps/frontend/src/app/components/ui/sidebar.tsx"
    ui.parent.mkdir(parents=True)
    ui.write_text("x\n", encoding="utf-8")
    assert budget.is_excluded(ui, root)


@pytest.mark.unit
def test_count_physical_lines(budget: Any, tmp_path: Path) -> None:
    """Physical line count matches newline semantics used by the budget."""
    p = tmp_path / "f.py"
    p.write_bytes(b"a\nb\nc")
    assert budget.count_physical_lines(p) == 3
    p.write_bytes(b"a\nb\nc\n")
    assert budget.count_physical_lines(p) == 3
    empty = tmp_path / "empty.py"
    empty.write_bytes(b"")
    assert budget.count_physical_lines(empty) == 0


@pytest.mark.unit
def test_is_excluded_outside_root(budget: Any, tmp_path: Path) -> None:
    """Paths outside the scan root are treated as excluded."""
    outside = Path("/tmp/not-under-root/foo.py")
    assert budget.is_excluded(outside, tmp_path) is True


@pytest.mark.unit
def test_check_budget_fails_non_allowlisted_oversize(
    budget: Any, tmp_path: Path
) -> None:
    """Non-allowlisted oversize sources fail; allowlisted and excluded pass."""
    root = tmp_path
    src = root / "apps/backend/src/big.py"
    src.parent.mkdir(parents=True)
    src.write_text("\n".join(f"x{i}" for i in range(510)) + "\n", encoding="utf-8")

    ok = root / "apps/backend/src/small.py"
    ok.write_text("ok\n", encoding="utf-8")

    ui = root / "apps/frontend/src/app/components/ui/big.tsx"
    ui.parent.mkdir(parents=True)
    ui.write_text("\n".join(f"y{i}" for i in range(600)) + "\n", encoding="utf-8")

    violations = budget.check_budget(root=root, allowlist=set(), budget=500)
    assert any("apps/backend/src/big.py" in v for v in violations)
    assert not any("small.py" in v for v in violations)
    assert not any("components/ui" in v for v in violations)

    violations2 = budget.check_budget(
        root=root, allowlist={"apps/backend/src/big.py"}, budget=500
    )
    assert not any("big.py" in v for v in violations2)


@pytest.mark.unit
def test_check_budget_missing_allowlist_path(budget: Any, tmp_path: Path) -> None:
    """Allowlist entries that do not exist on disk are violations."""
    violations = budget.check_budget(
        root=tmp_path,
        allowlist={"apps/nope.py"},
        budget=500,
    )
    assert any("missing" in v for v in violations)


@pytest.mark.unit
def test_main_ok_and_bootstrap(
    budget: Any,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """CLI exits 0 when clean; bootstrap prints oversize rows."""
    root = tmp_path
    (root / "apps").mkdir()
    (root / "packages").mkdir()
    monkeypatch.setattr(budget, "ROOT", root)
    monkeypatch.setattr(budget, "ALLOWLIST_PATH", root / "allow.txt")
    (root / "allow.txt").write_text("", encoding="utf-8")
    assert budget.main([]) == 0
    assert "file budget OK" in capsys.readouterr().out

    big = root / "apps/huge.py"
    big.write_text("\n".join("z" for _ in range(520)) + "\n", encoding="utf-8")
    assert budget.main(["--bootstrap"]) == 0
    out = capsys.readouterr().out
    assert "apps/huge.py" in out

    assert budget.main([]) == 1
