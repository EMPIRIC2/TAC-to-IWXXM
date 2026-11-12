"""Shared prefix-map utilities for advisory Cursor hooks.

[Corpus: cross-repo-tooling] [Corpus: hook-contract]

Loads project-local JSON maps from `.cursor/hooks/config/`. Advisory only — hooks exit 0.
"""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any


def find_repo_root(start: Path) -> Path | None:
    """Prefer git root; fall back to monorepo markers."""
    p = start if start.is_dir() else start.parent
    for candidate in [p, *p.parents]:
        if (candidate / ".git").exists():
            return candidate
    for candidate in [p, *p.parents]:
        if (candidate / "pnpm-workspace.yaml").is_file() or (
            candidate / "pyproject.toml"
        ).is_file():
            return candidate
    return None


def load_hook_config(config_path: Path) -> tuple[dict[str, str], dict[str, Any]]:
    """Return (prefix_map, options) from config JSON."""
    if not config_path.is_file():
        return {}, {}
    data: Any = json.loads(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}, {}
    options: dict[str, Any] = dict(data.get("options") or {})
    prefix_map: dict[str, str] = {}
    if isinstance(data.get("prefixes"), list):
        for item in data["prefixes"]:
            if isinstance(item, dict) and "prefix" in item and "label" in item:
                prefix_map[str(item["prefix"])] = str(item["label"])
    else:
        skip = {"prefixes", "options", "exact_paths"}
        prefix_map = {str(k): str(v) for k, v in data.items() if k not in skip}
    if isinstance(data.get("exact_paths"), dict):
        for path, label in data["exact_paths"].items():
            prefix_map[str(path)] = str(label)
    return prefix_map, options


def load_prefix_map(config_path: Path) -> dict[str, str]:
    """Load prefix → label map only (backward compatible)."""
    prefix_map, _ = load_hook_config(config_path)
    return prefix_map


def path_matches_prefix(path_str: str, prefix: str) -> bool:
    """Match exact path or directory prefix (tolerates trailing slash on prefix)."""
    norm = prefix.rstrip("/")
    return path_str == norm or path_str == prefix or path_str.startswith(prefix) or (
        path_str.startswith(norm + "/")
    )


def match_longest_prefix(rel_path: str, prefix_map: dict[str, str]) -> str | None:
    path_str = str(PurePosixPath(rel_path))
    best: tuple[int, str] | None = None
    for prefix, label in prefix_map.items():
        if path_matches_prefix(path_str, prefix):
            if best is None or len(prefix.rstrip("/")) > best[0]:
                best = (len(prefix.rstrip("/")), label)
    return best[1] if best else None


def resolve_config(repo: Path, filename: str) -> Path:
    return repo / ".cursor" / "hooks" / "config" / filename


def suffix_allowed(file_path: Path, options: dict[str, Any]) -> bool:
    suffixes = options.get("file_suffixes")
    if not suffixes:
        return True
    return file_path.suffix in suffixes
