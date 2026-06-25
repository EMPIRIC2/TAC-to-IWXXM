"""
GIFTs Adapter for Version-Aware METAR/IWXXM Conversion

Wraps the GIFTs library (gifts.metarEncoder and gifts.metarDecoder)
to support dynamic IWXXM version switching while maintaining compatibility.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def _wrap_in_bulletin(tac_text: str) -> str:
    """Wrap TAC in WMO bulletin format required by GIFTs decoder.

    GIFTs expects: SAXX99 STATION DDHHMMM<newline>METAR ...<equals>

    Args:
        tac_text: Raw METAR/SPECI text (may or may not have keyword)

    Returns:
        TAC wrapped in minimal WMO bulletin format
    """
    from datetime import UTC, datetime

    # Generate bulletin header (generic)
    now = datetime.now(UTC)
    header = f"SAXX99 KWBC {now.strftime('%d%H%M')}\n"

    # Ensure TAC starts with METAR or SPECI
    tac = tac_text.strip()
    if not tac.upper().startswith(("METAR", "SPECI")):
        tac = f"METAR {tac}"

    # End with equals sign
    if not tac.endswith("="):
        tac = f"{tac}="

    return f"{header}{tac}"


# Import GIFTs modules (workspace package packages/gifts)
try:
    from gifts import metarDecoder, metarEncoder  # type: ignore

    logger.info("GIFTs modules imported successfully")
except ImportError as e:
    logger.error(f"Failed to import GIFTs modules: {e}")
    metarDecoder = None  # type: ignore
    metarEncoder = None  # type: ignore


class GIFTsEncoder:
    """
    Wrapper around GIFTs metarEncoder with version support.

    Handles version switching by setting IWXXM_VERSION in xmlConfig
    before encoder instantiation.
    """

    def __init__(self, version: Optional[str] = None, geo_locations_db=None):
        """
        Initialize encoder for a specific IWXXM version.

        Args:
            version: IWXXM version string (e.g., "2025-2", "2023-1").
                    If None, uses GIFTs default.
            geo_locations_db: Optional dictionary-like object providing airport data.
                            Should have .get(icao) method returning "name|iata|designator|lat,lon"
        """
        if metarEncoder is None:
            raise ImportError("GIFTs metarEncoder not available")

        self.version = version
        self.geo_locations_db = geo_locations_db
        try:
            # Create encoder instance with version parameter
            # This will trigger Common.Base.__init__(version=version)
            # which calls xmlConfig.set_iwxxm_version(version)
            self._encoder = metarEncoder.Annex3(version=version)
            logger.debug(
                f"GIFTs encoder initialized for IWXXM {version or 'default'} "
                f"{'with geo_locations_db' if geo_locations_db else 'without geo_locations_db'}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize GIFTs encoder for version {version}: {e}")
            raise

    def encode(self, decoded_data: Dict[str, Any], original_tac: str) -> Any:
        """
        Encode decoded METAR data to IWXXM XML.

        Args:
            decoded_data: Dictionary from metarDecoder
            original_tac: Original TAC text for reference

        Returns:
            ElementTree root element of IWXXM XML

        Raises:
            Exception: If encoding fails
        """
        # Inject airport metadata if geo_locations_db available
        if self.geo_locations_db is not None:
            try:
                # Get ICAO code from decoded data
                ident = decoded_data.get("ident")
                icao = None

                # Handle both dict and alternative structures
                if isinstance(ident, dict):
                    icao = ident.get("str")
                elif isinstance(ident, list) and len(ident) > 0:
                    # If ident is a list, get first element's 'str' field
                    if isinstance(ident[0], dict):
                        icao = ident[0].get("str")
                    else:
                        icao = str(ident[0]) if ident[0] else None

                if icao:
                    metadata = self.geo_locations_db.get(icao)
                    if metadata:
                        # Parse metadata in format: "name|iata|designator|lat,lon"
                        parts = metadata.split("|")
                        if len(parts) == 4:
                            fullname, iataID, alternateID, position = parts

                            # Inject into decoded data maintaining correct field order for XML
                            # GIFTs encodes dict fields in iteration order, so we must preserve/establish correct order
                            # Expected order: str, name, alternate, iataID, position, [other fields]
                            # Handle both dict and list structures
                            if isinstance(ident, dict):
                                # Save original dict to preserve all fields
                                original_ident = ident.copy()

                                # Rebuild ident with correct field order
                                ident.clear()

                                # 1. Core identification field first (ICAO code - must remain first)
                                if "str" in original_ident:
                                    ident["str"] = original_ident["str"]

                                # 2. Airport metadata in canonical order
                                # Note: alternate becomes <designator>, iataID becomes <designatorIATA>
                                if len(fullname) > 0:
                                    ident["name"] = fullname
                                if len(alternateID) > 0:
                                    ident["alternate"] = alternateID
                                if len(iataID) > 0:
                                    ident["iataID"] = iataID
                                if len(position) > 0:
                                    ident["position"] = position

                                # 3. Restore any other fields that were in original (e.g., index, ts, etc.)
                                for key, value in original_ident.items():
                                    if key not in ident:  # Don't overwrite fields we already set
                                        ident[key] = value

                                logger.debug(f"Injected airport metadata for {icao}, field order: {list(ident.keys())}")

                            elif isinstance(ident, list) and len(ident) > 0 and isinstance(ident[0], dict):
                                # For list structure, apply same logic to first element
                                original_ident = ident[0].copy()
                                ident[0].clear()

                                if "str" in original_ident:
                                    ident[0]["str"] = original_ident["str"]

                                if len(fullname) > 0:
                                    ident[0]["name"] = fullname
                                if len(alternateID) > 0:
                                    ident[0]["alternate"] = alternateID
                                if len(iataID) > 0:
                                    ident[0]["iataID"] = iataID
                                if len(position) > 0:
                                    ident[0]["position"] = position

                                for key, value in original_ident.items():
                                    if key not in ident[0]:
                                        ident[0][key] = value

                                logger.debug(
                                    f"Injected airport metadata for {icao} (list), field order: {list(ident[0].keys())}"
                                )
                    else:
                        logger.debug(f"No metadata found for {icao}")
            except Exception as e:
                logger.warning(f"Failed to inject airport metadata: {e}")

        try:
            xml_root = self._encoder(decoded_data, original_tac)
            return xml_root
        except Exception as e:
            logger.error(f"Encoding failed for version {self.version}: {e}")
            raise


class GIFTsDecoder:
    """
    Wrapper around GIFTs metarDecoder with version support.

    Version parameter accepted for consistency, though TAC decoding
    is version-independent (version matters only for encoding).
    """

    def __init__(self, version: Optional[str] = None):
        """
        Initialize decoder.

        Args:
            version: IWXXM version (accepted for interface consistency,
                    not used by TAC decoder since TAC format is version-agnostic)
        """
        if metarDecoder is None:
            raise ImportError("GIFTs metarDecoder not available")

        self.version = version
        try:
            # Instantiate decoder (version parameter optional for compatibility)
            self._decoder = metarDecoder.Annex3()
            logger.debug("GIFTs decoder initialized")
        except Exception as e:
            logger.error(f"Failed to initialize GIFTs decoder: {e}")
            raise

    def decode(self, tac_text: str) -> Dict[str, Any]:
        """
        Decode METAR/SPECI TAC text to dictionary.

        Args:
            tac_text: METAR or SPECI TAC format string (with or without WMO header)

        Returns:
            Dictionary with decoded elements

        Raises:
            Exception: If decoding fails
        """
        try:
            # GIFTs requires WMO bulletin format
            bulletin = _wrap_in_bulletin(tac_text)
            decoded = self._decoder(bulletin)
            return decoded
        except Exception as e:
            logger.error(f"Decoding failed: {e}")
            raise


_encoder_cache: Dict[tuple, GIFTsEncoder] = {}
_decoder_instance: Optional[GIFTsDecoder] = None


def get_encoder(version: Optional[str] = None, geo_locations_db=None) -> GIFTsEncoder:
    """
    Get or create an encoder for the specified version.

    Encoders are cached per version+geo_locations_db combination to avoid repeated initialization.

    Args:
        version: IWXXM version string
        geo_locations_db: Optional airport location database (dictionary-like with .get(icao))

    Returns:
        GIFTsEncoder instance for the version
    """
    # Create cache key (version, geo_locations_db id)
    # We use id() for the DB since different instances with same data should get different encoders
    cache_key = (version, id(geo_locations_db) if geo_locations_db else None)

    if cache_key not in _encoder_cache:
        _encoder_cache[cache_key] = GIFTsEncoder(version=version, geo_locations_db=geo_locations_db)
        logger.debug(f"Cached encoder for version {version} with geo_locations_db")
    return _encoder_cache[cache_key]


def get_decoder(version: Optional[str] = None) -> GIFTsDecoder:
    """
    Get singleton decoder instance.

    Args:
        version: IWXXM version (accepted for consistency, not used by decoder)

    Returns:
        GIFTsDecoder instance
    """
    global _decoder_instance
    if _decoder_instance is None:
        _decoder_instance = GIFTsDecoder(version=version)
        logger.debug("Initialized singleton decoder")
    return _decoder_instance


def convert_tac_to_iwxxm(tac_text: str, version: Optional[str] = None, geo_locations_db=None) -> Any:
    """
    Convert METAR/SPECI TAC text to IWXXM XML for a specific version.

    Args:
        tac_text: METAR or SPECI TAC format string
        version: Target IWXXM version (e.g., "2025-2", "2023-1")
                If None, uses GIFTs default
        geo_locations_db: Optional airport location database

    Returns:
        ElementTree root element of IWXXM XML

    Raises:
        Exception: If conversion fails
    """
    from datetime import UTC, datetime

    decoder = get_decoder(version)
    encoder = get_encoder(version, geo_locations_db=geo_locations_db)

    decoded = decoder.decode(tac_text)

    # Add translator metadata if required
    # The encoder expects these fields when TRANSLATOR=True in xmlConfig
    try:
        from gifts.common import xmlConfig as des

        if des.TRANSLATOR:
            # Add bulletin ID (simplified - just use station + timestamp)
            if "ident" in decoded and "str" in decoded["ident"]:
                decoded["translatedBulletinID"] = f"MT{decoded['ident']['str']}{datetime.now(UTC).strftime('%d%H%M')}"

            # Add bulletin reception time (use translation time if not provided)
            if "translatedBulletinReceptionTime" not in decoded:
                decoded["translatedBulletinReceptionTime"] = decoded.get(
                    "translationTime", datetime.now(UTC).isoformat().replace("+00:00", "Z")
                )
    except (ImportError, AttributeError):
        pass

    xml_root = encoder.encode(decoded, tac_text)

    return xml_root


def clear_encoder_cache():
    """Clear cached encoder instances (useful for testing)."""
    global _encoder_cache
    _encoder_cache.clear()
    logger.debug("Cleared encoder cache")


def reset_decoder():
    """Reset decoder instance (useful for testing)."""
    global _decoder_instance
    _decoder_instance = None
    logger.debug("Reset decoder instance")
