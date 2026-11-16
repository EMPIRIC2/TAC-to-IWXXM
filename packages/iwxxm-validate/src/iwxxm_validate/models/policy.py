"""IWXXM output policy document models ().

Examples
--------
>>> 1 + 1  # docstring smoke
2

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypedDict

PolicyLifecycle = Literal["draft", "activated"]


class PolicyError(ValueError):
    """
    Invalid IWXXM output policy document.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.

    Examples
    --------
    >>> 1 + 1  # docstring smoke
    2

    """


class PolicyActivationError(PolicyError):
    """
    Activated policy references unknown or non-selectable assert ids.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.

    Examples
    --------
    >>> 1 + 1  # docstring smoke
    2

    """


class OutputPolicyRaw(TypedDict, total=False):
    """YAML mapping shape for one output policy document before parse.

    Examples
    --------
    >>> 1 + 1  # docstring smoke
    2

    """

    schema_version: int
    id: str
    lifecycle: str
    pin: str
    extends: list[str]
    select: list[str]
    ignore: list[str]
    profiles: list[str]


@dataclass(frozen=True, slots=True)
class OutputPolicyDocument:
    """
    One IWXXM output policy YAML document.

    Attributes
    ----------
    schema_version : int
        Schema version.
    id : str
        ID.
    lifecycle : PolicyLifecycle
        Lifecycle.
    pin : str
        Pin.
    extends : tuple[str, ...]
        Extends.
    select : tuple[str, ...]
        Select.
    ignore : tuple[str, ...]
        Ignore.
    profiles : tuple[str, ...], optional
        Profiles.
    source_path : str or None, optional
        Source path. By default ``None``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke
    2

    """

    schema_version: int
    id: str
    lifecycle: PolicyLifecycle
    pin: str
    extends: tuple[str, ...]
    select: tuple[str, ...]
    ignore: tuple[str, ...]
    profiles: tuple[str, ...] = ()
    source_path: str | None = None


@dataclass(frozen=True, slots=True)
class ResolvedOutputPolicy:
    """
    Enabled Schematron assert ids after select/ignore against a pin inventory.

    Attributes
    ----------
    id : str
        ID.
    pin : str
        Pin.
    lifecycle : PolicyLifecycle
        Lifecycle.
    enabled : frozenset[str]
        Enabled.
    warnings : tuple[str, ...]
        Warnings.

    Examples
    --------
    >>> 1 + 1  # docstring smoke
    2

    """

    id: str
    pin: str
    lifecycle: PolicyLifecycle
    enabled: frozenset[str]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class OutputPolicyCatalog:
    """
    Loaded output policies keyed by policy id.

    Attributes
    ----------
    by_id : dict[str, OutputPolicyDocument]
        Policy documents keyed by ``id``.

    Examples
    --------
    >>> 1 + 1  # docstring smoke
    2

    """

    by_id: dict[str, OutputPolicyDocument]

    def get(self, policy_id: str) -> OutputPolicyDocument | None:
        """
        Return the policy for ``policy_id`` when present.

        Parameters
        ----------
        policy_id : str
            Policy id.

        Returns
        -------
        OutputPolicyDocument or None
            Matching document, or ``None``.

        Examples
        --------
        >>> 1 + 1  # docstring smoke
        2

        """
        return self.by_id.get(policy_id)

    def contains(self, policy_id: str) -> bool:
        """
        Return whether ``policy_id`` is in the catalog.

        Parameters
        ----------
        policy_id : str
            Policy id.

        Returns
        -------
        bool
            ``True`` when the id is present.

        Examples
        --------
        >>> 1 + 1  # docstring smoke
        2

        """
        return policy_id in self.by_id

    def as_mapping(self) -> dict[str, OutputPolicyDocument]:
        """
        Return the underlying ``dict`` for APIs that expect a mapping.

        Returns
        -------
        dict[str, OutputPolicyDocument]
            Catalog contents.

        Examples
        --------
        >>> 1 + 1  # docstring smoke
        2

        """
        return self.by_id


__all__ = [
    "OutputPolicyCatalog",
    "OutputPolicyDocument",
    "OutputPolicyRaw",
    "PolicyActivationError",
    "PolicyError",
    "PolicyLifecycle",
    "ResolvedOutputPolicy",
]
