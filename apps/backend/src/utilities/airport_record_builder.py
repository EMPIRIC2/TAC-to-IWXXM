"""
Build complete airport records by merging data from multiple sources.

Source hierarchy:
1. OpenAIP (primary - most accurate)
2. vertical_datum_map.json (special overrides for known issues)
3. airports.json (legacy fallback)
"""

import json
import logging
from pathlib import Path
from typing import Any, cast

logger = logging.getLogger(__name__)


class AirportRecordBuilder:
    """Builder for complete airport records from multiple sources."""

    def __init__(self) -> None:
        """Initialize builder and load all data sources."""
        # Try to find the data directory
        base_path = Path(__file__).parent

        # Try relative path first
        self.data_dir = base_path.parent / "data"
        if not self.data_dir.exists():
            # Try absolute path from workspace root
            self.data_dir = Path(__file__).parent.parent.parent / "src" / "data"

        if not self.data_dir.exists():
            logger.warning(f"Data directory not found at {self.data_dir}")

        self._vertical_datum_map = self._load_json("vertical_datum_map.json")
        self._airports_json = self._load_json("airports.json")

    def _load_json(self, filename: str) -> dict[str, Any]:
        """Load JSON data file."""
        file_path = self.data_dir / filename
        if not file_path.exists():
            logger.warning(f"Data file not found: {filename}")
            return {}

        try:
            with open(file_path) as f:
                raw = json.load(f)
            if filename == "airports.json" and isinstance(raw, list):
                airports_list = cast(list[dict[str, Any]], raw)
                return {str(item.get("icao")): item for item in airports_list if item.get("icao")}
            if isinstance(raw, dict):
                return cast(dict[str, Any], raw)
            return {}
        except Exception as e:
            logger.error(f"Failed to load {filename}: {e}")
            return {}

    def build_record(
        self,
        icao: str,
        openaip_data: dict[str, Any] | None = None,
        airport_validator: object | None = None,
    ) -> dict[str, Any]:
        """
        Build a complete airport record.

        Merges data in priority order:
        1. vertical_datum_map.json (highest priority - hand-curated overrides)
        2. openaip_data (OpenAIP API/cache)
        3. airports.json (legacy fallback)

        Args:
            icao: 4-letter ICAO airport code
            openaip_data: Airport data from OpenAIP service (optional)
            airport_validator: AirportValidator instance for additional lookups

        Returns:
            Complete airport record with fields:
            - name: Airport name
            - iata: 3-letter IATA code
            - designator: Airport designator/alternate code
            - coordinates: {latitude, longitude}
            - elevation_m: Elevation in meters
            - status: 'active', 'closed', or 'unknown'
            - closure_year: Optional year airport closed
            - source: Description of where data came from
            - _override: bool indicating if data was overridden from defaults
        """
        icao = icao.upper().strip()
        record: dict[str, Any] = {
            "icao": icao,
            "name": None,
            "iata": None,
            "designator": None,
            "coordinates": None,
            "elevation_m": None,
            "status": "unknown",
            "closure_year": None,
            "source": "unknown",
            "_override": False,
            "_sources_tried": [],
        }

        # 1. Check vertical_datum_map (highest priority)
        # Look under "airport_overrides" key for ICAO-specific overrides
        airport_overrides = self._vertical_datum_map.get("airport_overrides", {})
        has_override = False
        if override := airport_overrides.get(icao):
            logger.info(f"Found {icao} in vertical_datum_map (override)")
            record.update(self._extract_fields(override))
            record["source"] = override.get("source", "vertical_datum_map.json")
            record["_override"] = True
            has_override = True

            # If override has complete data (name, iata, deignator, coordinates), return immediately
            if all([record.get("name"), record.get("iata"), record.get("designator"), record.get("coordinates")]):
                record["_sources_tried"].append("vertical_datum_map")
                return record

        record["_sources_tried"].append("vertical_datum_map")

        # 2. Try OpenAIP data
        if openaip_data:
            logger.info(f"Found {icao} in OpenAIP data")
            # Merge fields, but don't overwrite existing override values
            for key, value in self._extract_fields(openaip_data).items():
                if record.get(key) is None:
                    record[key] = value
            if not has_override:
                record["source"] = "OpenAIP"
            record["_sources_tried"].append("OpenAIP")
            # Check if we now have complete data
            if all([record.get("name"), record.get("iata"), record.get("designator"), record.get("coordinates")]):
                return record

        record["_sources_tried"].append("OpenAIP")

        # 3. Try airports.json (legacy)
        if airports_entry := self._airports_json.get(icao):
            logger.info(f"Found {icao} in airports.json (fallback)")
            # Merge fields, but don't overwrite existing override values
            for key, value in self._extract_fields(airports_entry).items():
                if record.get(key) is None:
                    record[key] = value
            if not has_override:
                record["source"] = "airports.json (legacy)"
            record["_sources_tried"].append("airports.json")
            return record

        record["_sources_tried"].append("airports.json")

        # 4. Try airport validator if available
        if airport_validator:
            try:
                get_airport_info = getattr(airport_validator, "get_airport_info", None)
                validator_record: dict[str, Any] | None = None
                if get_airport_info is not None:
                    validator_record = cast(
                        dict[str, Any] | None,
                        get_airport_info(icao),
                    )
                if validator_record:
                    logger.info(f"Found {icao} in airport validator")
                    record.update(self._extract_fields(validator_record))
                    record["source"] = "AirportValidator"
                    record["_sources_tried"].append("AirportValidator")
                    return record
            except Exception as e:
                logger.debug(f"Airport validator lookup failed: {e}")

            record["_sources_tried"].append("AirportValidator")

        logger.warning(f"Airport {icao} not found in any data source")
        return record

    def _extract_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        """Extract relevant fields from airport data."""
        extracted: dict[str, Any] = {}

        # Name
        if name := data.get("name"):
            extracted["name"] = name

        # IATA code
        if iata := data.get("iata") or data.get("iataCode"):
            extracted["iata"] = iata

        # Designator (alternate code, often same as IATA)
        if designator := data.get("designator") or data.get("altIdentifier"):
            extracted["designator"] = designator
        elif iata:
            # Use IATA as fallback for designator
            extracted["designator"] = iata

        # Coordinates
        coords = None
        if coord_dict := data.get("coordinates"):
            if isinstance(coord_dict, dict) and all(k in coord_dict for k in ["latitude", "longitude"]):
                coords = cast(dict[str, Any], coord_dict)
        elif "latitude" in data and "longitude" in data:
            coords = {"latitude": data["latitude"], "longitude": data["longitude"]}

        if coords:
            extracted["coordinates"] = coords

        # Elevation
        if elev := data.get("elevation_m") or data.get("elevation"):
            extracted["elevation_m"] = float(elev) if elev else None

        # Status and closure info
        if status := data.get("status"):
            extracted["status"] = status

        if closure_year := data.get("closure_year"):
            extracted["closure_year"] = closure_year

        return extracted

    def get_gifts_format(self, record: dict[str, Any]) -> str:
        """
        Convert airport record to GIFTs geoLocationsDB format.

        Format: "name|iata|designator|latitude,longitude"
        Example: "FORNEBU AIRPORT|FBU|FBU|59.89580,10.6172"

        Args:
            record: Airport record from build_record()

        Returns:
            GIFTs format string or empty string if incomplete
        """
        if not all([record.get("name"), record.get("iata"), record.get("designator"), record.get("coordinates")]):
            logger.warning(f"Incomplete airport record for {record['icao']}: cannot generate GIFTs format")
            return ""

        coords = record["coordinates"]
        lat = coords.get("latitude")
        lon = coords.get("longitude")

        if lat is None or lon is None:
            logger.warning(f"Missing coordinates for {record['icao']}")
            return ""

        return f"{record['name']}|{record['iata']}|{record['designator']}|{lat},{lon}"
