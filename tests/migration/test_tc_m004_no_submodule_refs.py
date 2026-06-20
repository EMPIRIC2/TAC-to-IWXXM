"""TC-M004: No Submodule References — test-plan.md §TC-M004, T11.1 gate."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

WORKFLOW_DIR = ROOT / ".github" / "workflows"
SCRIPTS_DIR = ROOT / "scripts"

STANDING_DOC_PATHS = (
    ROOT / "README.md",
    ROOT / "docs" / "spec.md",
    ROOT / "docs" / "deploy.md",
    ROOT / "docs" / "DEVELOPMENT.md",
)

SUBMODULE_COMMAND_PATTERN = re.compile(r"git\s+submodule", re.IGNORECASE)
GIT_MODULES_PATH_PATTERN = re.compile(r"\.git/modules")


def _scan_text(path: Path, pattern: re.Pattern[str]) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []
    return [f"{path.relative_to(ROOT)}:{idx}" for idx, line in enumerate(text.splitlines(), 1) if pattern.search(line)]


@pytest.mark.migration
class TestTcM004NoSubmoduleReferences:
    """Big-bang PR removes all submodule machinery (ADR-003)."""

    def test_gitmodules_file_absent(self) -> None:
        gitmodules = ROOT / ".gitmodules"
        assert not gitmodules.exists(), (
            "TC-M004 requires .gitmodules absent; complete T11.1 submodule removal"
        )

    def test_ci_workflows_contain_no_submodule_commands(self) -> None:
        hits: list[str] = []
        for workflow in sorted(WORKFLOW_DIR.glob("*.yml")):
            hits.extend(_scan_text(workflow, SUBMODULE_COMMAND_PATTERN))
        assert not hits, "CI workflows must not reference git submodule:\n" + "\n".join(hits)

    def test_scripts_contain_no_submodule_commands(self) -> None:
        hits: list[str] = []
        if SCRIPTS_DIR.is_dir():
            for path in sorted(SCRIPTS_DIR.rglob("*")):
                if path.suffix in {".py", ".sh", ".md"} and path.is_file():
                    hits.extend(_scan_text(path, SUBMODULE_COMMAND_PATTERN))
                    hits.extend(_scan_text(path, GIT_MODULES_PATH_PATTERN))
        assert not hits, "scripts/ must not reference submodules:\n" + "\n".join(hits)

    @pytest.mark.parametrize("doc_path", STANDING_DOC_PATHS, ids=lambda p: p.name)
    def test_standing_docs_contain_no_submodule_instructions(self, doc_path: Path) -> None:
        if not doc_path.is_file():
            pytest.skip(f"missing doc: {doc_path}")
        hits = _scan_text(doc_path, SUBMODULE_COMMAND_PATTERN)
        assert not hits, f"{doc_path.relative_to(ROOT)} must not instruct git submodule:\n" + "\n".join(hits)
