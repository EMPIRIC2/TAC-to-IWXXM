"""BUG-2026-06-23: Frontend Docker production build fails on Alpine (bash not found).

CI deploy runs ``docker/build-push-action`` with ``node:20-alpine`` builder stage.
``npm run build`` invokes ``bash ../../scripts/frontend/prepare-config.sh``, which
is unavailable in the slim Alpine image (exit 127).
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE = ROOT / "apps" / "frontend" / "Dockerfile"


def _builder_stage_body(text: str) -> str:
    start = text.index("FROM node:20-alpine AS builder")
    end = text.index("# Production stage")
    return text[start:end]


def test_frontend_docker_builder_avoids_bash_dependent_npm_run_build() -> None:
    """Builder must not call npm run build without bash (Alpine node image)."""
    body = _builder_stage_body(DOCKERFILE.read_text(encoding="utf-8"))
    uses_npm_run_build = "npm run build" in body
    installs_bash = "bash" in body and ("apk add" in body or "apt-get" in body)

    assert not uses_npm_run_build or installs_bash, (
        "apps/frontend/Dockerfile builder invokes `npm run build`, which requires bash "
        "for prepare-config.sh; node:20-alpine has no bash (CI exit 127)."
    )
