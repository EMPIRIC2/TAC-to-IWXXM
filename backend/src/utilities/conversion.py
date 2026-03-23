"""METAR TAC -> IWXXM conversion utilities."""
from __future__ import annotations

import logging
import pathlib
import re
import sys
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from ..services.validation_orchestrator import ComprehensiveValidationResult

try:
    from .tac_parser import extract_airport_code
except (ImportError, ModuleNotFoundError):
    from utilities.tac_parser import extract_airport_code  # type: ignore

logger = logging.getLogger(__name__)

# Import ValidationError early with fallback for both relative and absolute imports
try:
    from ..services.validation import ValidationError as ValError  # type: ignore[import]
except (ImportError, ModuleNotFoundError):
    try:
        from services.validation import ValidationError as ValError
    except (ImportError, ModuleNotFoundError):
        # Fallback: create a dummy exception class if service unavailable
        class ValError(Exception):  # type: ignore
            """Fallback validation error."""
            pass



def _ensure_gifts_on_path() -> None:
    """Resolve and add the GIFTs directory to sys.path.

    Handles both source layout (running from repo) and installed package
    layout inside a container (site-packages). We attempt several plausible
    ancestor locations plus explicit /app path used in Docker builds.
    """
    file_path = pathlib.Path(__file__).resolve()
    candidates = []

    # Ancestor traversals: parents[0] .. parents[5] (defensive upper bound)
    for depth in range(0, 6):  # pragma: no cover (loop logic simple)
        try:
            parent = file_path.parents[depth]
        except IndexError:
            break
        candidates.append(parent / "GIFTs")

    # Explicit Docker workdir copy location
    candidates.append(pathlib.Path("/app/GIFTs"))

    for cand in candidates:
        if cand.exists():
            if str(cand) not in sys.path:
                sys.path.insert(0, str(cand))
            return

    # If we reach here, none of the candidates existed.
    raise ImportError(
        "GIFTs submodule not found in any expected location. "
        "Tried: " + ", ".join(str(c) for c in candidates)
    )


_ensure_gifts_on_path()

try:  # pragma: no cover
    from gifts import metarDecoder, metarEncoder  # type: ignore
except Exception:  # pragma: no cover
    metarDecoder = None  # type: ignore
    metarEncoder = None  # type: ignore


class ConversionError(Exception):
    """Raised when METAR to IWXXM conversion fails."""

    pass


def _extract_icao_from_tac(tac_text: str) -> Optional[str]:
    """Extract ICAO code from METAR/SPECI TAC text.

    Args:
        tac_text: METAR or SPECI TAC format text

    Returns:
        ICAO code if found, None otherwise
    """
    icao = extract_airport_code(tac_text)
    if icao:
        return icao

    # If no METAR/SPECI keyword, try to find first 4-character code
    match = re.search(r'\b([A-Z][A-Z0-9]{3})\b', tac_text.upper())
    if match:
        return match.group(1)

    return None


def convert_metar_tac(tac_text: str, iwxxm_version: Optional[str] = None) -> str:
    """Convert METAR/SPECI TAC text to IWXXM XML.

    DEPRECATED: Use convert_metar_tac_with_metadata() instead for validation support.
    This function maintains backward compatibility but will be removed in a future version.

    Args:
        tac_text: METAR or SPECI TAC format text
        iwxxm_version: Target IWXXM version (e.g., "2025-2", "2023-1").
                      If None, uses default version.

    Returns:
        XML string in IWXXM format

    Raises:
        ConversionError: If conversion fails at any stage
    """
    import warnings
    warnings.warn(
        "convert_metar_tac() is deprecated, use convert_metar_tac_with_metadata() instead",
        DeprecationWarning,
        stacklevel=2
    )

    # Call new function with validation disabled for backward compatibility
    xml, _ = convert_metar_tac_with_metadata(
        tac_text,
        iwxxm_version=iwxxm_version,
        validate=False  # Maintain old behavior - no validation
    )
    return xml



def _load_aerodrome_db() -> Optional[pathlib.Path]:
    """Return path to GIFTs aerodrome table if present."""
    # Probe typical locations under the GIFTs submodule
    file_path = pathlib.Path(__file__).resolve()
    for depth in range(0, 6):
        try:
            parent = file_path.parents[depth]
        except IndexError:
            break
        cand = parent / "GIFTs" / "gifts" / "database" / "aerodromes.tbl"
        if cand.exists():
            return cand
    # Docker path
    cand = pathlib.Path("/app/GIFTs/gifts/database/aerodromes.tbl")
    if cand.exists():
        return cand
    return None


def _lookup_aerodrome(icao: str, use_test_overrides: bool = False):
    """Lookup aerodrome metadata, preferring CSV data over GIFTs table.

    Args:
        icao: ICAO airport code
        use_test_overrides: If True, applies test-specific vertical datum overrides

    Returns:
        dict with keys: name, iataID, alternate, position ("lat lon elev"), vertical_datum.
        Returns None if not found in either source.
    """
    # First, try to load from the airport validator (CSV data)
    try:
        from ..schemas.airport import get_airport_validator
        from .elevation_service import get_elevation_service

        validator = get_airport_validator()
        airport = validator.get_airport(icao)

        if airport:
            # Get elevation service for accurate vertical datum and high-precision coordinates
            elev_service = get_elevation_service()

            # Get ISO country code from airport data (e.g., "GB", "US", "GL")
            country_code = airport.country if hasattr(airport, 'country') else None

            # Convert to format expected by encoder
            position_parts = []
            vertical_datum = "EGM_96"  # Default

            if airport.coordinates:
                # Check for high-precision coordinate overrides first
                coord_override = elev_service.get_coordinates_override(icao)

                if coord_override:
                    # Use high-precision coordinates from override (e.g., from reference data)
                    # Format with 8 decimals then strip trailing zeros to match reference style
                    lat, lon = coord_override
                    lat_str = f"{lat:.8f}".rstrip('0').rstrip('.')
                    lon_str = f"{lon:.8f}".rstrip('0').rstrip('.')
                    position_parts.append(lat_str)
                    position_parts.append(lon_str)
                else:
                    # Use database coordinates with 8 decimal places for maximum precision
                    # (matches ICAO Annex 3 requirements: ~1cm accuracy)
                    position_parts.append(f"{airport.coordinates.latitude:.8f}")
                    position_parts.append(f"{airport.coordinates.longitude:.8f}")

                # Get accurate elevation and vertical datum
                elevation_m, vertical_datum = elev_service.get_elevation_data(
                    icao=icao,
                    default_elevation_ft=airport.coordinates.elevation_ft,
                    country_code=country_code,
                    use_test_overrides=use_test_overrides  # Pass test mode flag
                )

                if elevation_m is not None:
                    position_parts.append(str(elevation_m))

            # Check for metadata overrides (name, designator, iata)
            # Prioritize overrides from vertical_datum_map for WMO reference compliance
            name = airport.name.upper() if airport.name else ""
            iataID = airport.iata or ""
            alternate = ""  # Only include designator if explicitly overridden

            # Check elevation service for metadata overrides
            overrides = elev_service.datum_map.get("airport_overrides", {})
            if icao in overrides:
                override_data = overrides[icao]
                # Use override values if present
                if "name" in override_data:
                    name = override_data["name"]
                if "iata" in override_data:
                    iataID = override_data["iata"]
                if "designator" in override_data:
                    alternate = override_data["designator"]
                logger.debug(f"Applied metadata override for {icao}: name={name}, designator={alternate}, iata={iataID}")

            return {
                "name": name,
                "iataID": iataID,
                "alternate": alternate,
                "position": " ".join(position_parts),
                "vertical_datum": vertical_datum,
            }
    except Exception as e:
        # If CSV lookup fails, log and continue to fallback
        logger.debug(f"CSV airport lookup failed for {icao}: {e}")

    # Fallback to GIFTs aerodromes.tbl
    db = _load_aerodrome_db()
    if not db:
        return None
    try:
        for line in db.read_text(encoding="utf-8").splitlines():
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if not parts:
                continue
            if parts[0] == icao:
                iata = parts[1] if len(parts) > 1 else ""
                alternate = parts[2] if len(parts) > 2 else ""
                name = parts[3] if len(parts) > 3 else ""
                lat = parts[4] if len(parts) > 4 else ""
                lon = parts[5] if len(parts) > 5 else ""
                elev = parts[6] if len(parts) > 6 else ""
                position = " ".join(x for x in [lat, lon, elev] if x)
                return {
                    "name": name,
                    "iataID": iata,
                    "alternate": alternate,
                    "position": position,
                }
    except Exception:
        # silent fallback if table is malformed
        return None
    return None


try:
    from .metar_normalizer import (  # noqa: E402
        normalize_recent_weather_for_tac,
        normalize_recent_weather_tokens,
    )
except ImportError:
    from metar_normalizer import (  # type: ignore  # noqa: E402
        normalize_recent_weather_for_tac,
        normalize_recent_weather_tokens,
    )

__all__ = [
    "convert_metar_tac",
    "ConversionError",
    "convert_metar_tac_with_metadata",
    "normalize_recent_weather_tokens",
]


def _apply_recent_weather_normalization(
    tac_text: str,
    *,
    lenient: bool,
) -> str:
    """Optionally normalize recent-weather tokens and log rewrites."""
    if not lenient:
        return tac_text

    normalized_tac, norm_warnings = normalize_recent_weather_for_tac(tac_text)
    for warning in norm_warnings:
        logger.warning(
            "METAR recent-weather pre-normalization: '%s' at token index %d "
            "rewritten to '%s' (rule: %s)",
            warning["original"],
            warning["index"],
            warning["replacement"],
            warning["rule"],
        )

    return normalized_tac


def convert_metar_tac_with_metadata(
    tac_text: str,
    iwxxm_version: Optional[str] = None,
    reference_time: Optional[str] = None,
    use_test_overrides: bool = False,
    validate: bool = True,
    validation_layers: Optional[List[str]] = None,
    raise_on_validation_error: bool = False,
    lenient: bool = True,
) -> Tuple[str, Optional[ComprehensiveValidationResult]]:
    """Convert TAC to IWXXM and validate output (validation enabled by default).

    Falls back to basic conversion if lookup fails.

    Args:
        tac_text: METAR or SPECI TAC format text
        iwxxm_version: Target IWXXM version (e.g., "2025-2", "2023-1").
                      If None, uses default version.
        reference_time: ISO 8601 timestamp to use as reference for date/time computation
                       (e.g., "2023-05-29T00:00:00Z"). If None, uses current system time.
                       This is important for historical data where observation year/month
                       need to be computed from the reference time, not current time.
        use_test_overrides: If True, applies test-specific vertical datum overrides for
                           WMO reference test compliance (uses EGM_96 globally).
                           If False, uses production-accurate local datums (DHHN92, DVR90, etc.).
        validate: Run validation after conversion (DEFAULT: True). Set to False for performance.
        validation_layers: Which layers to run (None = recommended layers: XSD, Schematron, WMO Codes).
        raise_on_validation_error: Raise ConversionError if validation fails (default: False).
        lenient: If True (default), pre-normalize truncated recent-weather tokens
                 (e.g. RESH→RESHUP) before GIFTs decoding so that common manual-
                 input variants do not cause TAC parse failures.  Set to False to
                 preserve strict Annex 3 / WMO-conformant behaviour.

    Returns:
        Tuple of (xml_string, validation_result)
        - validation_result is None if validate=False

    Raises:
        ConversionError: If conversion fails
    """
    # Use GIFTs adapter for version-aware conversion
    try:
        from .gifts_adapter import get_decoder, get_encoder
    except ImportError as e:
        raise ConversionError(f"GIFTs adapter unavailable: {e}") from e

    try:
        decoder = get_decoder(version=iwxxm_version)
        encoder = get_encoder(version=iwxxm_version)
    except Exception as e:
        raise ConversionError(f"Failed to initialize decoder/encoder: {e}") from e

    try:
        # If reference_time provided, parse it and monkey-patch time.gmtime()
        # to use that time instead of current system time for historical data
        import time
        from contextlib import contextmanager
        from datetime import datetime

        @contextmanager
        def patched_gmtime(reference_time_str: Optional[str]):
            """Context manager to temporarily patch time.gmtime() and time.time() for historical data."""
            if reference_time_str is None:
                # No patching needed, use default behavior
                yield
                return

            # Parse reference time and create a time.struct_time
            try:
                dt = datetime.fromisoformat(reference_time_str.replace('Z', '+00:00'))
                reference_tuple = dt.timetuple()
                reference_timestamp = dt.timestamp()
            except ValueError as e:
                raise ConversionError(f"Invalid reference_time format: {e}") from e

            # Save originals and patch both gmtime and time
            # Note: time.gmtime() can be called with or without arguments
            # When called without args, it returns current time
            # When called with timestamp arg, it converts that timestamp
            original_gmtime = time.gmtime
            original_time = time.time

            def patched_gmtime_func(secs=None):
                if secs is None:
                    # Called without args - return reference time
                    return reference_tuple
                else:
                    # Called with timestamp - use original function
                    return original_gmtime(secs)

            def patched_time_func():
                # Return reference timestamp
                return reference_timestamp

            time.gmtime = patched_gmtime_func
            time.time = patched_time_func
            try:
                yield
            finally:
                # Restore originals
                time.gmtime = original_gmtime
                time.time = original_time

        tac_text = _apply_recent_weather_normalization(tac_text, lenient=lenient)

        # Decode with patched time if reference_time provided
        with patched_gmtime(reference_time):
            decoded = decoder.decode(tac_text)

        # Enrich with aerodrome metadata if available
        vertical_datum = None
        ident = decoded.get("ident")
        if ident and isinstance(ident, dict):
            icao = ident.get("str", "").strip()
            meta = _lookup_aerodrome(icao, use_test_overrides=use_test_overrides)
            if meta:
                # Extract vertical datum before updating ident
                vertical_datum = meta.pop("vertical_datum", None)

                # Save original ident to preserve all fields
                original_ident = ident.copy()

                # Update with metadata
                ident.update(meta)

                # Rebuild ident with correct field order for XML generation
                # GIFTs encodes dict fields in iteration order (Python 3.7+)
                # Expected order: str, name, alternate, iataID, position, [other fields]
                # This ensures XML elements appear as: designator, name, locationIndicatorICAO, designatorIATA, ARP
                ident.clear()

                # 1. Core ICAO code (must be first)
                if 'str' in original_ident:
                    ident['str'] = original_ident['str']

                # 2. Airport metadata in canonical order
                # alternate → <designator>, iataID → <designatorIATA>
                # Note: Only include fields that are non-empty
                if 'name' in meta and meta['name']:
                    ident['name'] = meta['name']
                if 'alternate' in meta and meta['alternate']:
                    ident['alternate'] = meta['alternate']
                if 'iataID' in meta and meta['iataID']:
                    ident['iataID'] = meta['iataID']
                if 'position' in meta and meta['position']:
                    ident['position'] = meta['position']

                # 3. Restore any other fields from original (e.g., index, ts, etc.)
                for key, value in original_ident.items():
                    if key not in ident:
                        ident[key] = value

                logger.debug(f"Injected airport metadata for {icao}, field order: {list(ident.keys())}")

                # Set vertical datum in GIFTs config for this conversion
                if vertical_datum:
                    try:
                        # Import GIFTs config module to set vertical datum dynamically
                        import sys
                        from pathlib import Path

                        # Ensure GIFTs is on path
                        gifts_root = Path(__file__).parent.parent.parent.parent / "GIFTs"
                        if gifts_root.exists() and str(gifts_root) not in sys.path:
                            sys.path.insert(0, str(gifts_root))

                        from gifts.common import xmlConfig
                        xmlConfig.verticalDatum = vertical_datum
                        logger.debug(f"Set vertical datum for {icao}: {vertical_datum}")
                    except Exception as e:
                        logger.warning(f"Failed to set vertical datum: {e}")

        xml_root = encoder.encode(decoded, tac_text)
    except Exception as e:
        raise ConversionError(f"Conversion failed: {e}") from e

    if xml_root is None:
        raise ConversionError("Encoder returned None (no XML produced).")

    try:
        # Include XML declaration for proper XML document format
        xml_string = ET.tostring(xml_root, encoding="unicode", xml_declaration=False)
        xml_string = '<?xml version="1.0"?>\n' + xml_string
    except Exception as e:
        raise ConversionError(f"Serialization error: {e}") from e

    # VALIDATION - DEFAULT ON
    validation_result = None
    if validate:
        try:
            # Import validation orchestrator
            try:
                from ..services.validation_orchestrator import get_validation_orchestrator
            except (ImportError, ValueError):
                from services.validation_orchestrator import get_validation_orchestrator

            orchestrator = get_validation_orchestrator()

            # Default layers: critical + recommended
            if validation_layers is None:
                validation_layers = [
                    "XML_WELLFORMED",  # Must be well-formed
                    "XML_SCHEMA",      # Must pass XSD
                    "SCHEMATRON",      # Should pass business rules
                    "WMO_CODELISTS"    # Should have valid codes
                ]

            validation_result = orchestrator.validate_complete(
                tac_text=tac_text,
                xml_content=xml_string,
                version=iwxxm_version,
                layers=validation_layers,
                stop_on_error=raise_on_validation_error
            )

            # Log validation summary
            if validation_result.is_valid:
                logger.info(
                    f"Validation passed: {len(validation_result.layers_passed)} layers, "
                    f"{len(validation_result.all_issues)} total issues"
                )
            else:
                logger.warning(
                    f"Validation failed: {len(validation_result.layers_failed)} failed layers, "
                    f"{len([i for i in validation_result.all_issues if i.level.value in ['ERROR', 'CRITICAL']])} errors"
                )

            # Raise if requested and validation failed
            if raise_on_validation_error and not validation_result.is_valid:
                error_msgs = [
                    f"{i.code}: {i.message}"
                    for i in validation_result.all_issues
                    if i.level.value in ["ERROR", "CRITICAL"]
                ]
                raise ConversionError(
                    f"Validation failed with {len(error_msgs)} error(s):\n" +
                    "\n".join(error_msgs[:5])  # Show first 5 errors
                )

        except Exception as e:
            if raise_on_validation_error:
                raise ConversionError(f"Validation error: {e}") from e
            else:
                logger.error(f"Validation failed but continuing: {e}")
                validation_result = None

    return xml_string, validation_result
