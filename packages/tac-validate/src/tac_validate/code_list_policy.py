"""TAC-side code-list deviation helpers (#1034).

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC]
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import cast

import yaml

from tac_validate.models import Issue
from tac_validate.profiles import PROFILE_CA_ECCC

_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_REPO_ROOT = _PACKAGE_ROOT.parents[1]
_MATRIX = "config/profiles/semantic/CA_ECCC.code-list-deviations.yaml"


def _repo_root() -> Path:
    candidate = _DEFAULT_REPO_ROOT
    if (candidate / "config" / "profiles").is_dir():
        return candidate
    for parent in Path(__file__).resolve().parents:
        if (parent / "config" / "profiles").is_dir():
            return parent
    return candidate


@lru_cache(maxsize=1)
def national_replace_tokens() -> frozenset[str]:
    """Return tokens that require a national code under ``CA_ECCC``."""
    path = _repo_root() / _MATRIX
    if not path.is_file():
        return frozenset()
    loaded_raw: object = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded_raw, dict):
        return frozenset()
    loaded = cast(dict[str, object], loaded_raw)
    raw = loaded.get("entries")
    tokens: set[str] = set()
    if isinstance(raw, list):
        for item in cast(list[object], raw):
            if not isinstance(item, dict):
                continue
            entry = cast(dict[str, object], item)
            if str(entry.get("kind") or "").lower() != "replace":
                continue
            token = str(entry.get("token") or "").strip().upper()
            if token and token != "*":
                tokens.add(token)
    return frozenset(tokens)


def check_global_only_tokens(
    tokens: list[str],
    *,
    profile: str,
    product: str = "TAF",
) -> list[Issue]:
    """Fail closed when CA-required tokens are treated as global-only under ``ca_eccc``."""
    if profile.strip().lower().replace("-", "_") != PROFILE_CA_ECCC:
        return []
    required = national_replace_tokens()
    issues: list[Issue] = []
    seen: set[str] = set()
    for raw in tokens:
        token = raw.strip().upper()
        if token not in required or token in seen:
            continue
        seen.add(token)
        issues.append(
            Issue(
                severity="error",
                code="CA_CODE_LIST_NATIONAL_REQUIRED",
                message=(
                    f"{product} token {token} requires a Canadian code-list URI "
                    "under ca_eccc (global WMO-only encoding is disallowed)"
                ),
            )
        )
    return issues


__all__ = ["check_global_only_tokens", "national_replace_tokens"]
