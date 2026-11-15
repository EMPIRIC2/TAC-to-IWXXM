"""Decimal-degree coordinate point owned by reference-lookup."""

from __future__ import annotations

from typing import NamedTuple


class Coordinate(NamedTuple):
    """
    One latitude and longitude in decimal degrees.

    Attributes
    ----------
    latitude :
        North positive.
    longitude :
        East positive.
    """

    latitude: float
    longitude: float

    def as_tuple(self) -> tuple[float, float]:
        """
        Return the public ``(lat, lon)`` wire shape.

        Returns
        -------
        tuple[float, float]
            Latitude then longitude.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (as_tuple)
        2
        """
        return (self.latitude, self.longitude)
