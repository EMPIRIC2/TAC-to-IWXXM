#!/usr/bin/env python3
"""Advisory guard for PyPI publish workflows and version tags (F12–F14).

Fires on:
- afterFileEdit / preToolUse Write for publish-related workflow paths
- beforeShellExecution / preToolUse Shell for ``git tag`` commands

Never blocks — always exits 0. Returns additional_context when relevant.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path, PurePosixPath

TAG_RE = re.compile(
    r"git\s+tag\b.*\b(tac-validate-v|iwxxm-validate-v|tac2iwxxm-v|v?\d+\.\d+)",
    re.IGNORECASE,
)
ANY_GIT_TAG_RE = re.compile(r"git\s+tag\b", re.IGNORECASE)

PUBLISH_PATH_HINTS = (
    "publish",
    "pypi",
    "release",
    "trusted-publish",
)

PACKAGE_TAG_HINT = (
    "Expected tags: tac-validate-v*, iwxxm-validate-v*, tac2iwxxm-v* "
    "(e.g. tac-validate-v0.1.0). OIDC trusted publishing only — no long-lived "
    "PYPI_API_TOKEN when OIDC is configured. Run skill pypi-release-checklist."
)


def find_repo_root(start: Path) -> Path | None:
    """Prefer monorepo git root over nested package pyproject.toml."""
    p = start if start.is_dir() else start.parent
    git_root: Path | None = None
    for candidate in [p, *p.parents]:
        if (candidate / ".git").exists():
            git_root = candidate
            break
    if git_root is not None:
        return git_root
    for candidate in [p, *p.parents]:
        if (candidate / "pnpm-workspace.yaml").is_file() or (
            candidate / "pyproject.toml"
        ).is_file():
            return candidate
    return None


def is_publish_workflow(rel: str) -> bool:
    posix = str(PurePosixPath(rel)).lower()
    if not posix.startswith(".github/workflows/"):
        return False
    return any(h in posix for h in PUBLISH_PATH_HINTS) or posix.endswith(
        ("publish.yml", "publish.yaml", "pypi.yml", "pypi.yaml")
    )


def context_for_file(rel: str) -> str | None:
    if is_publish_workflow(rel):
        return (
            f"[pypi-release-guard] Editing '{rel}' — F12–F14 publish path. "
            f"{PACKAGE_TAG_HINT}"
        )
    if rel.startswith("packages/") and rel.endswith("pyproject.toml"):
        pkg = rel.split("/")[1] if "/" in rel else ""
        if pkg in {"tac2iwxxm", "tac-validate", "iwxxm-validate"}:
            return (
                f"[pypi-release-guard] Editing '{rel}' (PyPI package metadata). "
                "Keep name/version aligned with F12–F14; cite-only Annex text in wheels; "
                "run skill pypi-release-checklist before tagging."
            )
    return None


def context_for_shell(command: str) -> str | None:
    if not command or not ANY_GIT_TAG_RE.search(command):
        return None
    if TAG_RE.search(command):
        return f"[pypi-release-guard] Version tag command detected. {PACKAGE_TAG_HINT}"
    return (
        "[pypi-release-guard] git tag detected. For PyPI packages use "
        "tac-validate-v* / iwxxm-validate-v* / tac2iwxxm-v* only (F14). "
        "Run skill pypi-release-checklist before pushing tags."
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("{}")
        return 0

    command = payload.get("command") or payload.get("commandLine") or ""
    shell_ctx = context_for_shell(str(command))
    if shell_ctx:
        print(json.dumps({"additional_context": shell_ctx}))
        return 0

    raw = payload.get("filePath") or payload.get("file_path") or ""
    if not raw:
        print("{}")
        return 0

    file_path = Path(raw)
    repo = find_repo_root(file_path)
    if repo is None:
        print("{}")
        return 0

    try:
        rel = str(file_path.resolve().relative_to(repo.resolve())).replace("\\", "/")
    except ValueError:
        print("{}")
        return 0

    file_ctx = context_for_file(rel)
    if file_ctx:
        print(json.dumps({"additional_context": file_ctx}))
    else:
        print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
