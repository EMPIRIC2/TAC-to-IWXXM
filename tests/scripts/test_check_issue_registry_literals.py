"""Coverage for scripts/ci/check_issue_registry_literals.py."""

from __future__ import annotations

from pathlib import Path

import pytest
import scripts.ci.check_issue_registry_literals as guard


@pytest.mark.unit
def test_should_scan_filters_paths() -> None:
    assert guard._should_scan(
        Path("packages/tac-validate/src/tac_validate/rules/metar.py")
    )
    assert not guard._should_scan(
        Path("packages/tac-validate/src/tac_validate/issue_registry.py")
    )
    assert not guard._should_scan(Path("packages/tac-validate/tests/test_x.py"))
    assert not guard._should_scan(Path("apps/backend/foo.py"))


@pytest.mark.unit
def test_main_warn_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ISSUE_REGISTRY_GUARD_STRICT", raising=False)
    rule = tmp_path / "packages/tac-validate/src/tac_validate/rules/bad.py"
    rule.parent.mkdir(parents=True)
    rule.write_text('severity = "error"\n', encoding="utf-8")
    assert guard.main(["prog", str(rule)]) == 0


@pytest.mark.unit
def test_main_strict_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ISSUE_REGISTRY_GUARD_STRICT", "1")
    rule = tmp_path / "packages/tac-validate/src/tac_validate/rules/bad.py"
    rule.parent.mkdir(parents=True)
    rule.write_text("severity: 'warning'\n", encoding="utf-8")
    assert guard.main(["prog", str(rule)]) == 1


@pytest.mark.unit
def test_main_skips_unreadable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ISSUE_REGISTRY_GUARD_STRICT", "1")
    missing = tmp_path / "packages/tac-validate/src/tac_validate/rules/missing.py"
    assert guard.main(["prog", str(missing)]) == 0


@pytest.mark.unit
def test_main_skips_non_scan_file(tmp_path: Path) -> None:
    other = tmp_path / "apps/backend/main.py"
    other.parent.mkdir(parents=True)
    other.write_text('severity = "error"\n', encoding="utf-8")
    assert guard.main(["prog", str(other)]) == 0


@pytest.mark.unit
def test_main_oserror_on_read(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rule = tmp_path / "packages/tac-validate/src/tac_validate/rules/bad.py"
    rule.parent.mkdir(parents=True)
    rule.write_text('severity = "error"\n', encoding="utf-8")

    original = Path.read_text

    def guarded(self: Path, *args, **kwargs):
        if self.as_posix() == rule.as_posix():
            raise OSError("denied")
        return original(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded)
    assert guard.main(["prog", str(rule)]) == 0


@pytest.mark.unit
def test_main_clean_file_no_literals(tmp_path: Path) -> None:
    rule = tmp_path / "packages/tac-validate/src/tac_validate/rules/clean.py"
    rule.parent.mkdir(parents=True)
    rule.write_text(
        "from tac_validate.registry import get_severity\n", encoding="utf-8"
    )
    assert guard.main(["prog", str(rule)]) == 0


@pytest.mark.unit
def test_main_many_hits_truncated_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("ISSUE_REGISTRY_GUARD_STRICT", raising=False)
    rule = tmp_path / "packages/tac-validate/src/tac_validate/rules/many.py"
    rule.parent.mkdir(parents=True)
    rule.write_text(
        "\n".join(f'severity = "error"  # {i}' for i in range(25)), encoding="utf-8"
    )
    assert guard.main(["prog", str(rule)]) == 0
    out = capsys.readouterr().out
    assert "+5 more" in out
