"""CA_ECCC code-list deviation resolve helpers (#1034).

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC]
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_REPO_ROOT = _PACKAGE_ROOT.parents[1]
_MATRIX = "config/profiles/semantic/CA_ECCC.code-list-deviations.yaml"
_EMIT_KINDS = frozenset({"replace", "override", "extend"})


def _repo_root() -> Path:
    candidate = _DEFAULT_REPO_ROOT
    if (candidate / "config" / "profiles").is_dir():
        return candidate
    for parent in Path(__file__).resolve().parents:
        if (parent / "config" / "profiles").is_dir():
            return parent
    return candidate


@lru_cache(maxsize=1)
def _entries() -> tuple[dict[str, Any], ...]:
    path = _repo_root() / _MATRIX
    if not path.is_file():
        return ()
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw = loaded.get("entries") or []
    return tuple(item for item in raw if isinstance(item, dict)) if isinstance(raw, list) else ()


def resolve_national_href(*, area: str, token: str) -> str | None:
    """Return national ``ca_uri`` when policy requires it for ``area``/``token``."""
    area_l = area.strip().lower()
    token_u = token.strip().upper()
    for entry in _entries():
        if str(entry.get("area") or "").lower() != area_l:
            continue
        if str(entry.get("token") or "").upper() != token_u:
            continue
        kind = str(entry.get("kind") or "none").lower()
        ca_uri = entry.get("ca_uri")
        if kind in _EMIT_KINDS and ca_uri:
            return str(ca_uri).rstrip("/")
    return None


__all__ = ["resolve_national_href"]
