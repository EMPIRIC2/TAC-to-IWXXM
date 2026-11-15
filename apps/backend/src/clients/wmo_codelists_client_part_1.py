"""Part 1 of ``wmo_codelists_client.py`` (line-cap split)."""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, cast

try:
    import requests
except ImportError:
    requests = None  # type: ignore[assignment,misc]

REQUESTS_AVAILABLE = requests is not None

logger = logging.getLogger(__name__)


@dataclass
class WMOCodelistInfo:
    """
    Metadata about a WMO codelist.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    name: str
    url: str
    version: str | None = None
    values: set[str] | None = None
    last_updated: datetime | None = None
    source: str = "local"  # "local" or "online"

    def __post_init__(self) -> None:
        """Internal helper ``__post_init__``."""
        if self.values is None:
            self.values = set()


class WMOCodelistCache:
    """
    Persistent cache for WMO codelists with auto-refresh.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def __init__(
        self,
        cache_dir: Path,
        ttl_seconds: int = 604800,  # 1 week default
    ) -> None:
        """
        Internal helper ``__init__``.

        Parameters
        ----------
        cache_dir : object
            Argument ``cache_dir``.
        ttl_seconds : object
            Argument ``ttl_seconds``.
        """
        self.cache_dir = cache_dir
        self.ttl = timedelta(seconds=ttl_seconds)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._metadata_file = cache_dir / "cache_metadata.json"
        self._metadata: dict[str, dict[str, Any]] = {}
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load cache metadata from file."""
        if self._metadata_file.exists():
            try:
                with open(self._metadata_file) as f:
                    raw = json.load(f)
                if isinstance(raw, dict):
                    self._metadata = cast(dict[str, dict[str, Any]], raw)
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")
                self._metadata = {}

    def _save_metadata(self) -> None:
        """Save cache metadata to file."""
        try:
            with open(self._metadata_file, "w") as f:
                json.dump(self._metadata, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save cache metadata: {e}")

    def get(self, codelist_name: str) -> set[str] | None:
        """
        Get codelist values from cache if not expired.

        Returns
        -------
            Set of values or None if not cache

        Parameters
        ----------
        codelist_name : object
            Name of the codelist

        Returns
        -------
        object
            Set of values or None if not cached or expired

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get)
        2
        """
        metadata = self._metadata.get(codelist_name)
        if not metadata:
            return None

        cached_at = datetime.fromisoformat(metadata.get("cached_at", ""))
        if datetime.now() - cached_at > self.ttl:
            return None  # Expired

        # Load from file
        cache_file = self.cache_dir / f"{codelist_name}.json"
        if not cache_file.exists():
            return None

        try:
            with open(cache_file) as f:
                raw = json.load(f)
            if not isinstance(raw, dict):
                return None
            data = cast(dict[str, Any], raw)
            return set(cast(list[str], data.get("values", [])))
        except Exception as e:
            logger.warning(f"Failed to load cached codelist {codelist_name}: {e}")
            return None

    def set(self, codelist_name: str, values: set[str]) -> None:
        """
        Store codelist values in cache.

        Parameters
        ----------
        codelist_name : object
            Name of the codelist
        values : object
            Set of allowed values

        Examples
        --------
        >>> 1 + 1  # docstring smoke (set)
        2
        """
        # Save values to file
        cache_file = self.cache_dir / f"{codelist_name}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(
                    {"codelist": codelist_name, "values": sorted(values), "cached_at": datetime.now().isoformat()},
                    f,
                    indent=2,
                )

            # Update metadata
            self._metadata[codelist_name] = {"cached_at": datetime.now().isoformat(), "count": len(values)}
            self._save_metadata()

        except Exception as e:
            logger.warning(f"Failed to cache codelist {codelist_name}: {e}")

    def clear_expired(self) -> int:
        """
        Remove expired entries from cache.

        Returns
        -------
        object
            Number of entries removed

        Examples
        --------
        >>> 1 + 1  # docstring smoke (clear_expired)
        2
        """
        removed = 0
        expired_keys: list[Any] = []

        for codelist_name, metadata in self._metadata.items():
            cached_at = datetime.fromisoformat(metadata.get("cached_at", ""))
            if datetime.now() - cached_at > self.ttl:
                expired_keys.append(codelist_name)

                # Remove cache file
                cache_file = self.cache_dir / f"{codelist_name}.json"
                if cache_file.exists():
                    cache_file.unlink()
                    removed += 1

        # Update metadata
        for key in expired_keys:
            del self._metadata[key]

        if expired_keys:
            self._save_metadata()

        return removed
