"""Profile code-list deviation policy (playbook §6 / #1034).

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC]
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import cast

import yaml

from iwxxm_validate.models.code_list import (
    CodeListDeviation,
    CodeListEntryRaw,
    CodeListPolicy,
    CodeListPolicyRaw,
)

_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_REPO_ROOT = _PACKAGE_ROOT.parents[1]
_PROFILES_DIR = "config/profiles/semantic"


def _repo_root() -> Path:
    """
    Resolve the repository root that holds ``config/profiles``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (_repo_root)
    2

    Returns
    -------
    Path
        Repo root path.
    """
    candidate = _DEFAULT_REPO_ROOT
    if (candidate / "config" / "profiles").is_dir():
        return candidate
    for parent in Path(__file__).resolve().parents:
        if (parent / "config" / "profiles").is_dir():
            return parent
    return candidate


def deviations_path(profile: str) -> Path:
    """
    Return path to the deviation matrix YAML for ``profile``.

    Parameters
    ----------
    profile : str
        Semantic profile id.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (deviations_path)
    2

    Returns
    -------
    Path
        Absolute path to ``{PROFILE}.code-list-deviations.yaml``.
    """
    return _repo_root() / _PROFILES_DIR / f"{profile.upper()}.code-list-deviations.yaml"


def _parse_entry(raw: CodeListEntryRaw | dict[str, object]) -> CodeListDeviation:
    """
    Build one ``CodeListDeviation`` from a YAML mapping.

    Parameters
    ----------
    raw : CodeListEntryRaw or dict[str, object]
        One matrix entry.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (_parse_entry)
    2

    Returns
    -------
    CodeListDeviation
        Normalized deviation row.
    """
    products_raw = raw.get("products")
    products: tuple[str, ...] = ()
    if isinstance(products_raw, list):
        products = tuple(str(p).upper() for p in cast(list[object], products_raw))
    global_uri = raw.get("global_uri")
    ca_uri = raw.get("ca_uri")
    return CodeListDeviation(
        id=str(raw.get("id") or ""),
        area=str(raw.get("area") or "").strip().lower(),
        token=str(raw.get("token") or "").strip(),
        kind=str(raw.get("kind") or "none").strip().lower(),
        global_uri=str(global_uri).rstrip("/") if global_uri else None,
        ca_uri=str(ca_uri).rstrip("/") if ca_uri else None,
        disallow_global=bool(raw.get("disallow_global")),
        products=products,
    )


@lru_cache(maxsize=8)
def load_code_list_policy(profile: str) -> CodeListPolicy:
    """
    Load the deviation matrix for a semantic profile id (empty OK for thin packs).

    Parameters
    ----------
    profile : str
        Semantic profile id.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (load_code_list_policy)
    2

    Returns
    -------
    CodeListPolicy
        Parsed policy (empty entries when the matrix file is missing).
    """
    path = deviations_path(profile)
    if not path.is_file():
        return CodeListPolicy(profile=profile.upper(), entries=())
    loaded_raw: object = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded_raw, dict):
        return CodeListPolicy(profile=profile.upper(), entries=())
    loaded = cast(CodeListPolicyRaw, cast(dict[str, object], loaded_raw))
    raw_entries = loaded.get("entries")
    entries: tuple[CodeListDeviation, ...] = ()
    if isinstance(raw_entries, list):
        entries = tuple(
            _parse_entry(cast(CodeListEntryRaw, item))
            for item in cast(list[object], raw_entries)
            if isinstance(item, dict)
        )
    profile_name = str(loaded.get("profile") or profile).upper()
    return CodeListPolicy(profile=profile_name, entries=entries)


__all__ = [
    "CodeListDeviation",
    "CodeListPolicy",
    "deviations_path",
    "load_code_list_policy",
]
