"""Cursor afterFileEdit hook: lightweight feature/component context on edits.

Cross-references edited file paths with docs/feature-list.md features.
Advisory only — always exits 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path, PurePosixPath

FEATURE_MAP: dict[str, str] = {
    "apps/backend/src/utilities/conversion": "F1 — METAR → IWXXM conversion",
    "apps/backend/src/routers/validation": "F2 — IWXXM validation",
    "apps/backend/src/services/openaip": "F3 — Airport data services",
    "apps/backend/src/services/reconciliation": "F3 — Airport data services",
    # Longer prefixes win — place F16–F19 paths before generic apps/backend|frontend.
    "apps/backend/src/routers/dissemination": "F16–F19 — Dissemination preflight/send (ADR-029)",
    "apps/backend/src/services/dissemination": "F16–F19 — Dissemination egress / writers",
    "apps/backend/src/dissemination": "F16–F19 — Dissemination module",
    "apps/frontend/src/components/Dissemination": "F16–F19 — Dissemination drawer UI",
    "apps/frontend/src/dissemination": "F16–F19 — Dissemination drawer UI",
    "apps/e2e/dissemination": "UJ-027–030 — Dissemination E2E (H6′)",
    "apps/backend": "F1–F19, M4 — Backend API (msgspec = F11; dissemination = F16–F19)",
    "apps/frontend": "F1–F19 — Frontend UI (dissemination drawer = F16–F19)",
    "apps/worker": "F8 — Near-RT ingest worker (no auto push sinks)",
    "apps/e2e": "UJ-001–030 — E2E tests (T2 / H6′)",
    "packages/tac2iwxxm": "F6, F9, F14 — tac2iwxxm convert/decode + PyPI",
    "packages/tac-validate": "F12, F15 — tac-validate PyPI + issue registry + TAC product rules",
    "packages/iwxxm-validate": "F2, F13 — iwxxm-validate Rust/XSD/Schematron + PyPI",
    "packages/dissemination": "F16–F19 — Dissemination sinks / writer-contract / SSRF (ADR-030)",
    "packages/gifts": "F1, M3 — GIFTs library (transitional)",
    "packages/auth": "M4 — Auth merged into backend",
    "packages/shared": "M1, M5 — Shared workspace package",
    "vendor": "M2, M6 — Vendor snapshot sync (read-only)",
    "docs/adr/ADR-029": "F16–F19 — Dissemination SSRF / allowlist (ADR-029)",
    "docs/adr/ADR-030": "F16–F19 — Dissemination package architecture (ADR-030)",
    "backend/src/utilities/conversion": "F1 — METAR → IWXXM (legacy path)",
    "backend/src/routers/validation": "F2 — IWXXM validation (legacy path)",
    "backend": "F1–F4, M4 — Legacy backend",
    "frontend": "F1–F4 — Legacy frontend",
    "GIFTs": "F1, M3 — Legacy GIFTs",
    "auth": "M4 — Legacy auth",
    "schemas": "M2 — Legacy schemas",
    ".github/workflows": "F14, M5, M6, F16–F19 — CI, vendor sync, PyPI, dissemination coverage/Compose",
    "Makefile": "M5, F16–F19 — Workspace tooling (+ dissemination / wis2box targets)",
    "docker-compose.yml": "M4 — Deploy topology",
    "docker-compose.wis2box.yml": "F17 — wis2box Compose/CI harness overlay (E14-04; not Render)",
    "render.yaml": "M4, F16–F19, UJ-OPS-001 — Render deploy (+ allowlist env; no wis2box service)",
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


def match_feature(rel_path: str) -> str | None:
    path_str = str(PurePosixPath(rel_path))
    best: tuple[int, str] | None = None
    for prefix, feature in FEATURE_MAP.items():
        if path_str == prefix or path_str.startswith(prefix + "/"):
            if best is None or len(prefix) > best[0]:
                best = (len(prefix), feature)
    return best[1] if best else None


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
    feature = match_feature(rel_str)

    if feature:
        context = (
            f"[feature-drift] Edit in '{rel_str}' → likely feature: {feature}. "
            "Confirm task maps to docs/feature-list.md and active execution plan."
        )
    else:
        context = (
            f"[feature-drift] Edit in '{rel_str}' — no automatic feature mapping. "
            "Verify against docs/feature-list.md (F1–F19, M1–M6)."
        )

    print(json.dumps({"additional_context": context}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
