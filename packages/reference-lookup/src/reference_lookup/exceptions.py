"""Lookup failures for the public OurAirports coordinate source."""

from __future__ import annotations


class SourceUnavailable(Exception):
    """
    The public coordinate source could not answer this id.

    Attributes
    ----------
    args :
        Ident or error text passed to the exception.
    """
