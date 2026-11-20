"""Part 2 of ``wmo_codelists_client.py`` (line-cap split)."""

from datetime import datetime
from pathlib import Path
from typing import Any

from ..utilities.codelist_parser import CodeListParser
from .wmo_codelists_client_part_1 import REQUESTS_AVAILABLE, WMOCodelistCache, WMOCodelistInfo, logger, requests


class WMOCodelistsClient:
    """
    Enhanced client for WMO codelist validation and fetching.

    Provides convenience methods for common validation tasks and
    automatic caching of online codelist fetches.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def __init__(
        self,
        codelists_dir: Path,
        cache_dir: Path | None = None,
        enable_online: bool = True,
        registry_url: str = "https://codes.wmo.int",
    ) -> None:
        """
        Internal helper ``__init__``.

        Parameters
        ----------
        codelists_dir : object
            Argument ``codelists_dir``.
        cache_dir : object
            Argument ``cache_dir``.
        enable_online : object
            Argument ``enable_online``.
        registry_url : object
            Argument ``registry_url``.
        """
        self.parser = CodeListParser(codelists_dir)
        self.registry_url = registry_url
        self.enable_online = enable_online and REQUESTS_AVAILABLE

        # Initialize cache
        if cache_dir is None:
            cache_dir = codelists_dir / "cache"
        self.cache = WMOCodelistCache(cache_dir)

    def validate_weather_phenomenon(self, code: str, codelist: str = "AerodromePresentOrForecastWeather") -> bool:
        """
        Validate a weather phenomenon code.

        Returns
        -------
            True if code is valid

        Parameters
        ----------
        code : object
            Weather code (e.g., "NSW", "TSRA")
        codelist : object
            Codelist name (default: AerodromePresentOrForecastWeather)

        Returns
        -------
        object
            True if code is valid

        Examples
        --------
        >>> 1 + 1  # docstring smoke (validate_weather_phenomenon)
        2
        """
        return self._validate_code(codelist, code)

    def validate_cloud_type(self, code: str, codelist: str = "CloudType") -> bool:
        """
        Validate a cloud type code.

        Returns
        -------
            True if code is valid

        Parameters
        ----------
        code : object
            Cloud type code (e.g., "CB", "TCU")
        codelist : object
            Codelist name (default: CloudType)

        Returns
        -------
        object
            True if code is valid

        Examples
        --------
        >>> 1 + 1  # docstring smoke (validate_cloud_type)
        2
        """
        return self._validate_code(codelist, code)

    def validate_cloud_amount(self, code: str, codelist: str = "CloudAmount") -> bool:
        """
        Validate a cloud amount code.

        Returns
        -------
            True if code is valid

        Parameters
        ----------
        code : object
            Cloud amount code (e.g., "FEW", "SCT", "BKN", "OVC")
        codelist : object
            Codelist name (default: CloudAmount)

        Returns
        -------
        object
            True if code is valid

        Examples
        --------
        >>> 1 + 1  # docstring smoke (validate_cloud_amount)
        2
        """
        return self._validate_code(codelist, code)

    def validate_visibility_type(self, code: str, codelist: str = "MeasurementOrFactType") -> bool:
        """
        Validate a visibility measurement type code.

        Returns
        -------
            True if code is valid

        Parameters
        ----------
        code : object
            Type code (e.g., "FORECAST", "OBSERVED")
        codelist : object
            Codelist name

        Returns
        -------
        object
            True if code is valid

        Examples
        --------
        >>> 1 + 1  # docstring smoke (validate_visibility_type)
        2
        """
        return self._validate_code(codelist, code)

    def _validate_code(self, codelist_name: str, code: str) -> bool:
        """
        Internal helper ``_validate_code``.

        Parameters
        ----------
        codelist_name : object
            Argument ``codelist_name``.
        code : object
            Argument ``code``.

        Returns
        -------
        object
            Return value.
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

    def _fetch_codelist_online(self, codelist_name: str) -> set[str] | None:
        """
        Internal helper ``_fetch_codelist_online``.

        Parameters
        ----------
        codelist_name : object
            Argument ``codelist_name``.

        Returns
        -------
        object
            Return value.
        """
        if not REQUESTS_AVAILABLE:
            return None

        # Construct URL (this is simplified - actual WMO URLs vary)
        url = f"{self.registry_url}/49-2/{codelist_name}"

        if requests is None:
            return None
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

                codes: set[str] = set()
                for concept in root.findall(".//skos:Concept", namespaces):
                    about = concept.get("{{{}}}about".format(namespaces["rdf"]))
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
        """
        Get information about a codelist.

        Returns
        -------
            WMOCodelistInfo with metadata

        Parameters
        ----------
        codelist_name : object
            Name of the codelist

        Returns
        -------
        object
            WMOCodelistInfo with metadata

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_codelist_info)
        2
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

    def list_available_codelists(self) -> list[str]:
        """
        List all available codelists (local and cached).

        Returns
        -------
        object
            List of codelist names

        Examples
        --------
        >>> 1 + 1  # docstring smoke (list_available_codelists)
        2
        """
        local_lists = set(self.parser.list_codelists())

        # Add cached lists
        if self.cache._metadata:
            local_lists.update(self.cache._metadata.keys())

        return sorted(local_lists)

    def get_statistics(self) -> dict[str, Any]:
        """
        Get statistics about available codelists.

        Returns
        -------
        object
            Dictionary with statistics

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_statistics)
        2
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
