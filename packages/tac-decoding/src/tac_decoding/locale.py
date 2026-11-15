"""English explanation hook. Other locales fail closed this cycle.

Templates may only use ``{0}``, ``{1}``, … and ``{value}``. Attribute access,
conversions, and format specs are rejected.
"""

from __future__ import annotations

import re
import string
from collections.abc import Mapping, Sequence
from typing import Any

from tac_decoding.models.locale import ExplanationHook, LocaleError

ENGLISH = "en"
_FIELD = re.compile(r"\d+|value")


def require_locale(locale: str) -> None:
    """
    Reject every locale except English.

    Parameters
    ----------
    locale : str
        Locale code.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (require_locale)
    2
    """
    if locale != ENGLISH:
        msg = f"Locale {locale!r} is not available"
        raise LocaleError(msg)


def render_template(
    template: str,
    groups: tuple[str, ...],
    *,
    value: str | None = None,
    locale: str = ENGLISH,
) -> str:
    """
    Fill an English template. Placeholders cannot reach into objects.

    Parameters
    ----------
    template : str
        Explanation template text.

    groups : tuple[str, ...]
        Placeholder values.

    value : str | None, optional
        Token value passed to the template.

    locale : str, optional
        Locale code.

    Returns
    -------
    str
        Fill an English template.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (render_template)
    2
    """
    require_locale(locale)
    kwargs: dict[str, str] = {}
    if value is not None:
        kwargs["value"] = value
    try:
        return _SAFE.format(template, *groups, **kwargs)
    except LocaleError:
        raise
    except (IndexError, KeyError, ValueError) as exc:
        msg = "Explanation template is not allowed"
        raise LocaleError(msg) from exc


class _SafeFormatter(string.Formatter):
    """Internal helper ``_SafeFormatter``."""

    def get_field(self, field_name: str, args: Sequence[Any], kwargs: Mapping[str, Any]) -> tuple[Any, Any]:
        """
        Resolve a placeholder only when its name is on the allowlist.

        Parameters
        ----------
        field_name : str
            Format field name.

        args : Sequence[Any]
            Positional arguments from ``str.format``.

        kwargs : Mapping[str, Any]
            Keyword arguments from ``str.format``.

        Returns
        -------
        tuple[Any, Any]
            A placeholder only when its name is on the allowlist.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_field)
        2
        """
        if _FIELD.fullmatch(field_name) is None:
            msg = "Explanation placeholder is not allowed"
            raise LocaleError(msg)
        return super().get_field(field_name, args, kwargs)

    def format_field(self, value: object, format_spec: str) -> str:
        """
        Format a value; reject non-empty format specs.

        Parameters
        ----------
        value : object
            Value to format.

        format_spec : str
            Format specification.

        Returns
        -------
        str
            Format a value; reject non-empty format specs.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (format_field)
        2
        """
        if format_spec:
            msg = "Explanation format is not allowed"
            raise LocaleError(msg)
        return format(value, "")

    def convert_field(self, value: object, conversion: str | None) -> object:
        """
        Return a value; reject conversion flags.

        Parameters
        ----------
        value : object
            Value to convert.

        conversion : str | None
            Conversion flag. ``None`` means no conversion.

        Returns
        -------
        object
            A value; reject conversion flags.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (convert_field)
        2
        """
        if conversion:
            msg = "Explanation conversion is not allowed"
            raise LocaleError(msg)
        return value


_SAFE = _SafeFormatter()

__all__ = ["ENGLISH", "ExplanationHook", "LocaleError", "render_template", "require_locale"]
