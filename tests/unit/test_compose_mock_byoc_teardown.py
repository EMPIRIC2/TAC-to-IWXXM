"""EV-039 / AC4 - compose-mock-byoc teardown must remove containers and volumes.

T1.1 (S047): contract that ``compose-mock-byoc-down`` uses ``down -v --remove-orphans``
on an isolated compose project so orphans cannot linger and backend/frontend stay up.

[Corpus: product §F16] [Corpus: tests] [Corpus: tech-spec]
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = ROOT / "Makefile"

BYOC_CONTAINER_PREFIX = "metar-iwxxm-byoc-"
BYOC_PROJECT = "metar-iwxxm-mock-byoc"


def _makefile_recipe(makefile: str, target: str) -> str:
    """Return recipe lines for a Makefile target (tab-indented body)."""
    pattern = re.compile(rf"^{re.escape(target)}:(.*)$", re.M)
    match = pattern.search(makefile)
    assert match is not None, f"missing Makefile target {target}"
    start = match.end()
    lines = [match.group(1)]
    for line in makefile[start:].splitlines()[1:]:
        if (
            not line.startswith("\t")
            and line.strip()
            and not line.startswith("#")
            and re.match(r"^[A-Za-z0-9_.-]+:", line)
        ):
            break
        if (
            line.startswith("\t")
            or line.endswith("\\")
            or (lines and lines[-1].endswith("\\"))
        ):
            lines.append(line)
        elif not line.strip():
            continue
        else:
            break
    return "\n".join(lines)


def _makefile_var(makefile: str, name: str) -> str:
    """Return a simple Makefile variable body (joined ``\\`` continuations)."""
    pattern = re.compile(rf"^{re.escape(name)}\s*:=\s*(.*)$", re.M)
    match = pattern.search(makefile)
    assert match is not None, f"missing Makefile var {name}"
    parts = [match.group(1).rstrip()]
    idx = makefile.count("\n", 0, match.end())
    lines = makefile.splitlines()
    while parts[-1].endswith("\\"):
        parts[-1] = parts[-1][:-1].rstrip()
        idx += 1
        if idx >= len(lines):
            break
        parts.append(lines[idx].strip())
    return " ".join(parts)


def test_compose_mock_byoc_down_uses_down_v_remove_orphans() -> None:
    """AC4 / S02.M1: teardown must be ``down -v --remove-orphans``, not stop+rm only."""
    makefile = MAKEFILE.read_text(encoding="utf-8")
    recipe = _makefile_recipe(makefile, "compose-mock-byoc-down")
    flat = " ".join(recipe.split())
    byoc = _makefile_var(makefile, "BYOC_COMPOSE")
    project = _makefile_var(makefile, "BYOC_COMPOSE_PROJECT").strip()

    assert "$(BYOC_COMPOSE)" in flat or "BYOC_COMPOSE" in flat
    assert "down" in flat, "compose-mock-byoc-down must invoke compose down"
    assert re.search(r"\bdown\b.*(-v|--volumes)", flat) or re.search(
        r"(-v|--volumes).*\bdown\b", flat
    ), "compose-mock-byoc-down must pass -v / --volumes"
    assert "--remove-orphans" in flat, (
        "compose-mock-byoc-down must pass --remove-orphans"
    )
    assert "rm -f" not in flat, (
        "compose-mock-byoc-down should not rely on stop+rm -f (use down -v)"
    )
    assert project == BYOC_PROJECT
    assert "-p $(BYOC_COMPOSE_PROJECT)" in byoc or f"-p {BYOC_PROJECT}" in byoc
    assert "docker-compose.mock-byoc.yml" in byoc
    assert "--profile mock-byoc" in byoc


def test_compose_mock_byoc_up_uses_same_project_as_down() -> None:
    """up/down must share compose project name so teardown finds the stack."""
    makefile = MAKEFILE.read_text(encoding="utf-8")
    up = _makefile_recipe(makefile, "compose-mock-byoc-up")
    down = _makefile_recipe(makefile, "compose-mock-byoc-down")
    project = _makefile_var(makefile, "BYOC_COMPOSE_PROJECT")
    assert project.strip() == BYOC_PROJECT
    assert "$(BYOC_COMPOSE)" in up
    assert "$(BYOC_COMPOSE)" in down


def test_byoc_container_name_prefix_documented() -> None:
    """Orphan assert name prefix matches Compose container_name values."""
    overlay = (ROOT / "docker-compose.mock-byoc.yml").read_text(encoding="utf-8")
    names = re.findall(r"container_name:\s*(\S+)", overlay)
    assert names, "expected container_name entries in mock-byoc overlay"
    for name in names:
        assert name.startswith(BYOC_CONTAINER_PREFIX), (
            f"{name} must use prefix {BYOC_CONTAINER_PREFIX} for orphan asserts"
        )
