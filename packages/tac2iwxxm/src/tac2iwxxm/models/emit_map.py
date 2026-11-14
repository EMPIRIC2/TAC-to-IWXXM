"""Emit-map catalog models."""

from __future__ import annotations

from dataclasses import dataclass


class EmitMapError(ValueError):
    """
    Emit map document is invalid or no map matches the convert request.

    Attributes
    ----------
    args : tuple
        Arguments passed to the exception constructor.
    """


@dataclass(frozen=True, slots=True)
class EmitMap:
    """
    One emit-map catalog entry.

    Attributes
    ----------
    id : str
        ID.
    profiles : tuple[str, ...]
        Profiles.
    products : tuple[str, ...]
        Products.
    iwxxm_versions : tuple[str, ...] | None
        IWXXM versions.
    kind : str
        Kind.
    plugin : str
        Plugin.
    source_path : str
        Source path.
    pass_product : bool
        When ``True``, the plugin is called with ``product``. Default ``True``.
    """

    id: str
    profiles: tuple[str, ...]
    products: tuple[str, ...]
    iwxxm_versions: tuple[str, ...] | None
    kind: str
    plugin: str
    source_path: str
    pass_product: bool = True


__all__ = ["EmitMap", "EmitMapError"]
