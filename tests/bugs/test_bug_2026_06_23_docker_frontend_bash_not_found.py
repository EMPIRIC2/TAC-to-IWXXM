"""BUG-2026-06-23: Frontend Docker production build fails on Alpine (bash not found).

CI deploy runs ``docker/build-push-action`` with ``node:20-alpine`` builder stage.
``npm run build`` invokes ``bash ../../scripts/frontend/prepare-config.sh``, which
is unavailable in the slim Alpine image (exit 127).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE = ROOT / "apps" / "frontend" / "Dockerfile"

# Match the builder stage regardless of node version / tag, e.g.
# "FROM node:20-alpine AS builder" or "FROM node:22-alpine AS builder".
_BUILDER_STAGE = re.compile(r"^FROM\s+\S+\s+AS\s+builder\b", re.IGNORECASE)
_NEXT_STAGE = re.compile(r"^FROM\s+", re.IGNORECASE)


def _builder_stage_body(text: str) -> str:
    """Return the Dockerfile lines belonging to the ``builder`` stage.

    Resilient to node version bumps and stage reordering: locates the
    ``AS builder`` stage and reads until the next ``FROM`` line (or EOF).
    """
    lines = text.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if _BUILDER_STAGE.match(line.strip()):
            start = index
            break
    assert start is not None, (
        "apps/frontend/Dockerfile has no `AS builder` stage - expected a "
        "multi-stage build that compiles the frontend bundle."
    )
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if _NEXT_STAGE.match(lines[index].strip()):
            end = index
            break
    return "\n".join(lines[start:end])


def test_frontend_docker_builder_avoids_bash_dependent_npm_run_build() -> None:
    """Builder must not call ``npm run build`` without bash (Alpine node image).

    ``npm run build`` invokes ``bash prepare-config.sh``; the slim Alpine node
    image has no bash (CI exit 127). The builder must either avoid the bash-only
    ``npm run build`` (e.g. ``pnpm exec vite build`` + inline config) or install
    bash explicitly.
    """
    body = _builder_stage_body(DOCKERFILE.read_text(encoding="utf-8"))
    uses_npm_run_build = "npm run build" in body
    installs_bash = "bash" in body and ("apk add" in body or "apt-get" in body)

    assert not uses_npm_run_build or installs_bash, (
        "apps/frontend/Dockerfile builder invokes `npm run build`, which requires bash "
        "for prepare-config.sh; the Alpine node image has no bash (CI exit 127)."
    )
