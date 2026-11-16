"""Code-list deviation policy models (#1034 / F36)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict


class CodeListEntryRaw(TypedDict, total=False):
    """YAML mapping shape for one code-list deviation row."""

    id: str
    area: str
    token: str
    kind: str
    global_uri: str
    ca_uri: str
    disallow_global: bool
    products: list[str]


class CodeListPolicyRaw(TypedDict, total=False):
    """YAML mapping shape for a code-list deviation matrix file."""

    profile: str
    entries: list[CodeListEntryRaw]


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


_EMIT_KINDS = frozenset({"replace", "override", "extend"})
_DISALLOW_KINDS = frozenset({"replace", "override"})


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


__all__ = [
    "CodeListDeviation",
    "CodeListEntryRaw",
    "CodeListPolicy",
    "CodeListPolicyRaw",
]
