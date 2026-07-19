"""Cursor preToolUse hook: advisory check that new files map to approved components.

Reads the file path from stdin JSON, checks against docs/spec.md §Component Overview,
and returns advisory context. Never blocks — always exits 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path, PurePosixPath

# Target monorepo tree + transitional legacy paths during migration.
APPROVED_COMPONENTS: dict[str, str] = {
    "apps/backend": "Backend API — conversion, validation, auth (F1–F11, M4)",
    "apps/frontend": "Frontend UI (F1–F11, UJ-001)",
    "apps/worker": "F8 near-RT ingest poller — Background Worker (ADR-018)",
    "apps/e2e": "E2E workspace — Playwright (T2)",
    "packages/auth": "Auth library — Supabase middleware (M4)",
    "packages/tac2iwxxm": "General TAC → IWXXM converter (F6, F14)",
    "packages/tac-validate": "TAC product validation / lint (F12)",
    "packages/iwxxm-validate": "IWXXM XSD + Schematron engine (F2, F13)",
    "packages/gifts": "GIFTs — transitional until F6 cutover delete (F1, M3)",
    "packages/shared": "Shared types and utils (M1, M5)",
    "vendor": "Vendor schemas — read-only wmo-im snapshots (M2, M6)",
    "backend": "Legacy backend — migrate to apps/backend (M1)",
    "frontend": "Legacy frontend — migrate to apps/frontend (M1)",
    "GIFTs": "Legacy GIFTs — migrate to packages/gifts (M3)",
    "auth": "Legacy auth — migrate to packages/auth (M4)",
    "schemas": "Legacy schemas — migrate to vendor/schemas (M2)",
    "data/iwxxm-translation": "Legacy translation data — migrate to vendor/schemas (M2)",
    "tests": "Test suite",
    "test-data": "Golden fixtures (TC-M003)",
    "docs": "Documentation",
    ".cursor": "Cursor tooling",
    ".github": "CI/CD + PyPI publish workflows (F14, M5, M6)",
    "scripts": "Automation — vendor sync, deploy smoke",
}

INFRA_PATHS = {
    "Makefile",
    "docker-compose.yml",
    "render.yaml",
    "pyproject.toml",
    "pnpm-workspace.yaml",
    "uv.lock",
    "package.json",
    "pnpm-lock.yaml",
}


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


def match_component(rel_path: str) -> str | None:
    posix = PurePosixPath(rel_path)
    path_str = str(posix)
    if path_str in INFRA_PATHS:
        return "Monorepo infrastructure (M1, M5)"
    for prefix, component in APPROVED_COMPONENTS.items():
        if path_str == prefix or path_str.startswith(prefix + "/"):
            return component
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("{}")
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
        rel = file_path.resolve().relative_to(repo.resolve())
    except ValueError:
        print("{}")
        return 0

    rel_str = str(rel).replace("\\", "/")
    component = match_component(rel_str)

    if component:
        result = {"additional_context": f"[scope-check] File maps to: {component}"}
    else:
        result = {
            "additional_context": (
                f"[scope-check] WARNING: '{rel_str}' does not map to any approved "
                "component in docs/spec.md §Component Overview. Verify scope "
                "(F1–F14, M1–M6) or raise [Scope Drift]."
            )
        }

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
