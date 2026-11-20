"""IssueSpec registry definition model."""

# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

import msgspec


class IssueSpec(msgspec.Struct, frozen=True):
    """
    One registered lint issue definition.

    Parameters
    ----------
    code : str
        Stable SCREAMING_SNAKE public id.
    severity : str
        Default ``error``, ``warning``, or ``info``.
    message_template : str
        Human message; may include ``str.format`` placeholders (e.g. ``{product}``).
    product : str or None
        Optional product tag for catalog filtering (``None`` = shared / multi-product).
    tags : tuple[str, ...]
        Optional catalog / FE tags (not part of the public code string).
    """

    code: str
    severity: str
    message_template: str
    product: str | None = None
    tags: tuple[str, ...] = ()


__all__ = ["IssueSpec"]
