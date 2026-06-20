"""Client for WMO codelist validation and fetching.

Extends existing CodeListParser with convenience methods and caching.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from ..utilities.codelist_parser import CodeListParser

logger = logging.getLogger(__name__)


@dataclass
class WMOCodelistInfo:
    """Metadata about a WMO codelist."""

    name: str
    url: str
    version: Optional[str] = None
    values: Set[str] = None
    last_updated: Optional[datetime] = None
    source: str = "local"  # "local" or "online"

    def __post_init__(self):
        if self.values is None:
            self.values = set()


class WMOCodelistCache:
    """Persistent cache for WMO codelists with auto-refresh."""

    def __init__(
        self,
        cache_dir: Path,
        ttl_seconds: int = 604800,  # 1 week default
    ):
        """Initialize cache.

        Args:
            cache_dir: Directory to store cached data
            ttl_seconds: Time to live for cached entries (default 1 week)
        """
        self.cache_dir = cache_dir
        self.ttl = timedelta(seconds=ttl_seconds)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self._metadata_file = cache_dir / "cache_metadata.json"
        self._metadata: Dict[str, dict] = {}
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load cache metadata from file."""
        if self._metadata_file.exists():
            try:
                with open(self._metadata_file, "r") as f:
                    data = json.load(f)
                    self._metadata = data
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

    def get(self, codelist_name: str) -> Optional[Set[str]]:
        """Get codelist values from cache if not expired.

        Args:
            codelist_name: Name of the codelist

        Returns:
            Set of values or None if not cached or expired
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
            with open(cache_file, "r") as f:
                data = json.load(f)
                return set(data.get("values", []))
        except Exception as e:
            logger.warning(f"Failed to load cached codelist {codelist_name}: {e}")
            return None

    def set(self, codelist_name: str, values: Set[str]) -> None:
        """Store codelist values in cache.

        Args:
            codelist_name: Name of the codelist
            values: Set of allowed values
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
        """Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        removed = 0
        expired_keys = []

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


class WMOCodelistsClient:
    """Enhanced client for WMO codelist validation and fetching.

    Provides convenience methods for common validation tasks and
    automatic caching of online codelist fetches.
    """

    def __init__(
        self,
        codelists_dir: Path,
        cache_dir: Optional[Path] = None,
        enable_online: bool = True,
        registry_url: str = "https://codes.wmo.int",
    ):
        """Initialize WMO codelists client.

        Args:
            codelists_dir: Path to local RDF codelists directory
            cache_dir: Path to cache directory (default: codelists_dir/cache)
            enable_online: Enable online validation for missing codelists
            registry_url: Base URL for WMO registry
        """
        self.parser = CodeListParser(codelists_dir)
        self.registry_url = registry_url
        self.enable_online = enable_online and REQUESTS_AVAILABLE

        # Initialize cache
        if cache_dir is None:
            cache_dir = codelists_dir / "cache"
        self.cache = WMOCodelistCache(cache_dir)

    def validate_weather_phenomenon(self, code: str, codelist: str = "AerodromePresentOrForecastWeather") -> bool:
        """Validate a weather phenomenon code.

        Args:
            code: Weather code (e.g., "NSW", "TSRA")
            codelist: Codelist name (default: AerodromePresentOrForecastWeather)

        Returns:
            True if code is valid
        """
        return self._validate_code(codelist, code)

    def validate_cloud_type(self, code: str, codelist: str = "CloudType") -> bool:
        """Validate a cloud type code.

        Args:
            code: Cloud type code (e.g., "CB", "TCU")
            codelist: Codelist name (default: CloudType)

        Returns:
            True if code is valid
        """
        return self._validate_code(codelist, code)

    def validate_cloud_amount(self, code: str, codelist: str = "CloudAmount") -> bool:
        """Validate a cloud amount code.

        Args:
            code: Cloud amount code (e.g., "FEW", "SCT", "BKN", "OVC")
            codelist: Codelist name (default: CloudAmount)

        Returns:
            True if code is valid
        """
        return self._validate_code(codelist, code)

    def validate_visibility_type(self, code: str, codelist: str = "MeasurementOrFactType") -> bool:
        """Validate a visibility measurement type code.

        Args:
            code: Type code (e.g., "FORECAST", "OBSERVED")
            codelist: Codelist name

        Returns:
            True if code is valid
        """
        return self._validate_code(codelist, code)

    def _validate_code(self, codelist_name: str, code: str) -> bool:
        """Internal code validation with cache fallback.

        Args:
            codelist_name: Name of the codelist
            code: Code value to validate

        Returns:
            True if code is valid
        """
        # Try local parser first
        if self.parser.validate_code(codelist_name, code):
            return True

        # Try cache
        cached_values = self.cache.get(codelist_name)
        if cached_values:
            return code in cached_values

        # Try online if enabled
        if self.enable_online:
            values = self._fetch_codelist_online(codelist_name)
            if values:
                self.cache.set(codelist_name, values)
                return code in values

        # Unknown - log warning
        logger.warning(
            f"Could not validate code '{code}' against codelist '{codelist_name}' "
            f"(not found locally, in cache, or online)"
        )
        return False

    def _fetch_codelist_online(self, codelist_name: str) -> Optional[Set[str]]:
        """Fetch codelist from online WMO registry.

        Args:
            codelist_name: Name of the codelist

        Returns:
            Set of codes or None if fetch failed
        """
        if not REQUESTS_AVAILABLE:
            return None

        # Construct URL (this is simplified - actual WMO URLs vary)
        url = f"{self.registry_url}/49-2/{codelist_name}"

        try:
            response = requests.get(url, timeout=10, headers={"Accept": "application/rdf+xml"})

            if response.status_code == 200:
                # Parse RDF response
                # This is a simplified implementation - full RDF parsing needed
                import xml.etree.ElementTree as ET

                root = ET.fromstring(response.content)
                namespaces = {
                    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                    "skos": "http://www.w3.org/2004/02/skos/core#",
                }

                codes = set()
                for concept in root.findall(".//skos:Concept", namespaces):
                    about = concept.get("{%s}about" % namespaces["rdf"])
                    if about:
                        code = about.split("/")[-1]
                        codes.add(code)

                if codes:
                    logger.info(f"Fetched {len(codes)} codes for {codelist_name} from online registry")
                    return codes

            else:
                logger.warning(f"Failed to fetch codelist {codelist_name}: HTTP {response.status_code}")

        except Exception as e:
            logger.warning(f"Error fetching codelist {codelist_name} from {url}: {e}")

        return None

    def get_codelist_info(self, codelist_name: str) -> WMOCodelistInfo:
        """Get information about a codelist.

        Args:
            codelist_name: Name of the codelist

        Returns:
            WMOCodelistInfo with metadata
        """
        # Try local first
        local_codes = self.parser.get_codes(codelist_name)
        if local_codes:
            return WMOCodelistInfo(
                name=codelist_name, url=f"{self.registry_url}/49-2/{codelist_name}", values=local_codes, source="local"
            )

        # Try cache
        cached_codes = self.cache.get(codelist_name)
        if cached_codes:
            return WMOCodelistInfo(
                name=codelist_name, url=f"{self.registry_url}/49-2/{codelist_name}", values=cached_codes, source="cache"
            )

        # Try online
        if self.enable_online:
            online_codes = self._fetch_codelist_online(codelist_name)
            if online_codes:
                self.cache.set(codelist_name, online_codes)
                return WMOCodelistInfo(
                    name=codelist_name,
                    url=f"{self.registry_url}/49-2/{codelist_name}",
                    values=online_codes,
                    last_updated=datetime.now(),
                    source="online",
                )

        # Not found
        return WMOCodelistInfo(name=codelist_name, url=f"{self.registry_url}/49-2/{codelist_name}", source="unknown")

    def list_available_codelists(self) -> List[str]:
        """List all available codelists (local and cached).

        Returns:
            List of codelist names
        """
        local_lists = set(self.parser.list_codelists())

        # Add cached lists
        if self.cache._metadata:
            local_lists.update(self.cache._metadata.keys())

        return sorted(local_lists)

    def get_statistics(self) -> Dict[str, any]:
        """Get statistics about available codelists.

        Returns:
            Dictionary with statistics
        """
        local_lists = self.parser.list_codelists()
        cached_lists = list(self.cache._metadata.keys())

        return {
            "local_codelists": len(local_lists),
            "cached_codelists": len(cached_lists),
            "total_unique": len(set(local_lists + cached_lists)),
            "online_enabled": self.enable_online,
            "registry_url": self.registry_url,
        }
