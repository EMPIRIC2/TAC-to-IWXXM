"""Ident → coordinate rows index (replaces a nested ``dict`` of lists)."""

from __future__ import annotations

from reference_lookup.models.coordinate import Coordinate


class IdentIndex:
    """
    Map each uppercase ident to the coordinate rows that share it.

    More than one row for an ident is ambiguous at lookup time.

    Attributes
    ----------
    _by_ident :
        Ident to ordered coordinate rows.
    """

    def __init__(self) -> None:
        """Create an empty index."""
        self._by_ident: dict[str, list[Coordinate]] = {}

    def add(self, ident: str, point: Coordinate) -> None:
        """
        Append one coordinate for ``ident``.

        Parameters
        ----------
        ident : str
            Uppercase navaid or airport identifier.

        point : Coordinate
            Parsed decimal-degree point.
        """
        self._by_ident.setdefault(ident, []).append(point)

    def rows_for(self, ident: str) -> list[Coordinate]:
        """
        Return every coordinate stored for ``ident``.

        Parameters
        ----------
        ident : str
            Uppercase identifier.

        Returns
        -------
        list[Coordinate]
            Matching rows, or an empty list when the ident is absent.
        """
        return list(self._by_ident.get(ident, []))

    def unique_point(self, ident: str) -> Coordinate | None:
        """
        Return the single coordinate for ``ident``, or ``None`` when missing or ambiguous.

        Parameters
        ----------
        ident : str
            Uppercase identifier.

        Returns
        -------
        Coordinate | None
            The only row, or ``None`` when the count is not exactly one.
        """
        rows = self._by_ident.get(ident, [])
        if len(rows) != 1:
            return None
        return rows[0]

    def __contains__(self, ident: str) -> bool:
        """
        Return whether ``ident`` has at least one row.

        Parameters
        ----------
        ident : str
            Uppercase identifier.

        Returns
        -------
        bool
            True when the ident is present.
        """
        return ident in self._by_ident

    def __len__(self) -> int:
        """
        Return the number of distinct idents.

        Returns
        -------
        int
            Ident count.
        """
        return len(self._by_ident)
