"""Profile code-list deviation policy (playbook §6 / #1034).

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC]
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Final, cast

import yaml

_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_REPO_ROOT = _PACKAGE_ROOT.parents[1]
_PROFILES_DIR = "config/profiles/semantic"
_EMIT_KINDS: Final = frozenset({"replace", "override", "extend"})
_DISALLOW_KINDS: Final = frozenset({"replace", "override"})


@dataclass(frozen=True, slots=True)
class CodeListDeviation:
    """
    One global→national code-list deviation row.

    Attributes
    ----------
    id : str
        Stable deviation id from the matrix YAML.
    area : str
        Code-list area key (lower-case).
    token : str
        TAC / code token this row applies to.
    kind : str
        Deviation kind (``replace``, ``override``, ``extend``, or ``none``).
    global_uri : str or None
        Disallowed or replaced global URI when set.
    ca_uri : str or None
        National URI to emit when set.
    disallow_global : bool
        When true, the global URI must not appear under this profile.
    products : tuple[str, ...]
        Product codes this row applies to (empty means all).
    """

    id: str
    area: str
    token: str
    kind: str
    global_uri: str | None
    ca_uri: str | None
    disallow_global: bool
    products: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CodeListPolicy:
    """
    Loaded ``code_list_policy`` matrix for one semantic profile.

    Attributes
    ----------
    profile : str
        Semantic profile id (upper-case).
    entries : tuple[CodeListDeviation, ...]
        Parsed deviation rows.
    """

    profile: str
    entries: tuple[CodeListDeviation, ...]

    def disallowed_global_uris(self) -> frozenset[str]:
        """
        Return global URIs that must not appear under this profile.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (disallowed_global_uris)
        2

        Returns
        -------
        frozenset[str]
            Global URIs marked ``disallow_global`` for replace/override kinds.
        """
        return frozenset(
            entry.global_uri
            for entry in self.entries
            if entry.disallow_global and entry.global_uri and entry.kind in _DISALLOW_KINDS
        )

    def resolve_ca_uri(self, *, area: str, token: str) -> str | None:
        """
        Return national URI for ``area``/``token`` when policy requires it.

        Parameters
        ----------
        area : str
            Code-list area key.
        token : str
            TAC / code token.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (resolve_ca_uri)
        2

        Returns
        -------
        str or None
            National ``ca_uri`` when an emit kind matches, otherwise ``None``.
        """
        token_u = token.strip().upper()
        area_l = area.strip().lower()
        for entry in self.entries:
            if entry.area == area_l and entry.token.upper() == token_u and entry.kind in _EMIT_KINDS and entry.ca_uri:
                return entry.ca_uri
        return None


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


def _parse_entry(raw: dict[str, object]) -> CodeListDeviation:
    """
    Build one ``CodeListDeviation`` from a YAML mapping.

    Parameters
    ----------
    raw : dict[str, object]
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
    loaded = cast(dict[str, object], loaded_raw)
    raw_entries = loaded.get("entries")
    entries: tuple[CodeListDeviation, ...] = ()
    if isinstance(raw_entries, list):
        entries = tuple(
            _parse_entry(cast(dict[str, object], item))
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
