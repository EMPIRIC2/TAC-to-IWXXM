"""
ICAO OPMET Data Exchange compliance configuration.

Implements Translation Centre settings and ICAO region mappings
as per user decisions for the METAR to IWXXM Translation Centre.
"""

import os
from typing import Dict

# =============================================================================
# Translation Centre Identification (ICAO Doc 10003, Section 7)
# =============================================================================
# Note: Translation Centre details are configured via environment variables.
# Not currently operating as an official ICAO Translation Centre.

TRANSLATION_CENTRE_NAME = os.getenv("TRANSLATION_CENTRE_NAME", None)

TRANSLATION_CENTRE_DESIGNATOR = os.getenv("TRANSLATION_CENTRE_DESIGNATOR", None)

# ICAO Location Indicator (4-letter code)
ICAO_LOCATION_INDICATOR = os.getenv("ICAO_LOCATION_INDICATOR", None)

# Service online date
SERVICE_ONLINE_SINCE = os.getenv("SERVICE_ONLINE_SINCE", None)

# Technical contact (configure via environment variable if needed)
TECHNICAL_CONTACT_EMAIL = os.getenv("TECHNICAL_CONTACT_EMAIL", None)


# =============================================================================
# ICAO Regional Offices Mapping (User Decision 3)
# =============================================================================

# Maps airport ICAO prefixes to ICAO regional offices
# Based on ICAO Doc 7910 - Location Indicators
ICAO_REGION_MAP: Dict[str, str] = {
    # Africa-Indian Ocean (AFI)
    "FB": "AFI",
    "FC": "AFI",
    "FD": "AFI",
    "FE": "AFI",
    "FG": "AFI",
    "FH": "AFI",
    "FI": "AFI",
    "FJ": "AFI",
    "FK": "AFI",
    "FL": "AFI",
    "FM": "AFI",
    "FN": "AFI",
    "FO": "AFI",
    "FP": "AFI",
    "FQ": "AFI",
    "FS": "AFI",
    "FT": "AFI",
    "FV": "AFI",
    "FW": "AFI",
    "FX": "AFI",
    "FY": "AFI",
    "FZ": "AFI",
    "GO": "AFI",
    "GQ": "AFI",
    "GU": "AFI",
    "GV": "AFI",
    "GM": "AFI",
    "HA": "AFI",
    "HB": "AFI",
    "HC": "AFI",
    "HD": "AFI",
    "HE": "AFI",
    "HH": "AFI",
    "HK": "AFI",
    "HL": "AFI",
    "HR": "AFI",
    "HS": "AFI",
    "HT": "AFI",
    "HU": "AFI",
    # Asia Pacific (APAC)
    "AG": "APAC",
    "AN": "APAC",
    "AY": "APAC",
    "BI": "APAC",
    "BK": "APAC",
    "NG": "APAC",
    "NI": "APAC",
    "NL": "APAC",
    "NS": "APAC",
    "NT": "APAC",
    "NV": "APAC",
    "NW": "APAC",
    "NZ": "APAC",
    "OB": "APAC",
    "PG": "APAC",
    "PH": "APAC",
    "PJ": "APAC",
    "PK": "APAC",
    "PL": "APAC",
    "PM": "APAC",
    "PT": "APAC",
    "PW": "APAC",
    "RC": "APAC",
    "RJ": "APAC",
    "RK": "APAC",
    "RO": "APAC",
    "RP": "APAC",
    "VA": "APAC",
    "VC": "APAC",
    "VD": "APAC",
    "VE": "APAC",
    "VG": "APAC",
    "VH": "APAC",
    "VI": "APAC",
    "VL": "APAC",
    "VM": "APAC",
    "VN": "APAC",
    "VO": "APAC",
    "VQ": "APAC",
    "VR": "APAC",
    "VT": "APAC",
    "VV": "APAC",
    "VY": "APAC",
    "WA": "APAC",
    "WB": "APAC",
    "WI": "APAC",
    "WM": "APAC",
    "WP": "APAC",
    "WR": "APAC",
    "WS": "APAC",
    "ZB": "APAC",
    "ZG": "APAC",
    "ZH": "APAC",
    "ZJ": "APAC",
    "ZK": "APAC",
    "ZL": "APAC",
    "ZM": "APAC",
    "ZP": "APAC",
    "ZS": "APAC",
    "ZU": "APAC",
    "ZW": "APAC",
    "ZY": "APAC",
    # European (EUR)
    "EB": "EUR",
    "ED": "EUR",
    "EE": "EUR",
    "EF": "EUR",
    "EG": "EUR",
    "EH": "EUR",
    "EI": "EUR",
    "EK": "EUR",
    "EL": "EUR",
    "EN": "EUR",
    "EP": "EUR",
    "ES": "EUR",
    "ET": "EUR",
    "EV": "EUR",
    "EY": "EUR",
    "LA": "EUR",
    "LB": "EUR",
    "LC": "EUR",
    "LD": "EUR",
    "LE": "EUR",
    "LF": "EUR",
    "LG": "EUR",
    "LH": "EUR",
    "LI": "EUR",
    "LJ": "EUR",
    "LK": "EUR",
    "LL": "EUR",
    "LM": "EUR",
    "LN": "EUR",
    "LO": "EUR",
    "LP": "EUR",
    "LQ": "EUR",
    "LR": "EUR",
    "LS": "EUR",
    "LT": "EUR",
    "LU": "EUR",
    "LV": "EUR",
    "LW": "EUR",
    "LX": "EUR",
    "LY": "EUR",
    "LZ": "EUR",
    "UB": "EUR",
    "UC": "EUR",
    "UD": "EUR",
    "UE": "EUR",
    "UG": "EUR",
    "UH": "EUR",
    "UI": "EUR",
    "UK": "EUR",
    "UL": "EUR",
    "UM": "EUR",
    "UN": "EUR",
    "UO": "EUR",
    "UR": "EUR",
    "US": "EUR",
    "UT": "EUR",
    "UU": "EUR",
    "UW": "EUR",
    # Middle East (MID)
    "DA": "MID",
    "DB": "MID",
    "DF": "MID",
    "DG": "MID",
    "DI": "MID",
    "DN": "MID",
    "DT": "MID",
    "DX": "MID",
    "GA": "MID",
    "GE": "MID",
    "LR": "MID",  # Some overlap
    "OA": "MID",  # Afghanistan often in MID
    "OE": "MID",
    "OI": "MID",
    "OJ": "MID",
    "OK": "MID",
    "OL": "MID",
    "OM": "MID",
    "OO": "MID",
    "OP": "MID",
    "OR": "MID",
    "OS": "MID",
    "OT": "MID",
    "OY": "MID",
    # North American (NAM)
    "BG": "NAM",
    "C": "NAM",  # All C-prefix (Canada)
    "K": "NAM",  # All K-prefix (Continental USA)
    "M": "NAM",  # All M-prefix (Central America)
    "PA": "NAM",
    "PF": "NAM",
    "PH": "NAM",
    "PJ": "NAM",
    "PL": "NAM",
    "PM": "NAM",
    "PO": "NAM",
    "PP": "NAM",
    "PT": "NAM",
    "PW": "NAM",
    "TI": "NAM",
    "TJ": "NAM",
    "TK": "NAM",
    "TL": "NAM",
    "TN": "NAM",
    "TT": "NAM",
    "TX": "NAM",
    # South American (SAM)
    "SA": "SAM",
    "SB": "SAM",
    "SC": "SAM",
    "SD": "SAM",
    "SE": "SAM",
    "SF": "SAM",
    "SG": "SAM",
    "SI": "SAM",
    "SJ": "SAM",
    "SK": "SAM",
    "SL": "SAM",
    "SM": "SAM",
    "SN": "SAM",
    "SO": "SAM",
    "SP": "SAM",
    "SS": "SAM",
    "SU": "SAM",
    "SV": "SAM",
    "SW": "SAM",
    "SY": "SAM",
}


def get_icao_region(airport_code: str) -> str:
    """
    Determine ICAO region from airport code.

    Args:
        airport_code: 4-letter ICAO airport identifier

    Returns:
        ICAO region code (AFI, APAC, EUR, MID, NAM, SAM, NAT, WAFR, ESAF)

    Raises:
        ValueError: If airport code format is invalid

    Note:
        - Returns "NAM" for all K-prefix (USA continental)
        - Returns "NAM" for all C-prefix (Canada)
        - Returns "NAM" for all M-prefix (Central America)
        - Returns "APAC" for unmapped Pacific islands
        - Returns "EUR" for unmapped European codes
    """
    if not airport_code or len(airport_code) != 4:
        raise ValueError(f"Invalid ICAO airport code: {airport_code}")

    airport_code = airport_code.upper()

    # Single-letter prefix handling (K, C, M)
    first_letter = airport_code[0]
    if first_letter in ["K", "C", "M"]:
        return "NAM"

    # Two-letter prefix lookup
    two_letter_prefix = airport_code[:2]
    if two_letter_prefix in ICAO_REGION_MAP:
        return ICAO_REGION_MAP[two_letter_prefix]

    # Fallback for unmapped codes (rare edge cases)
    # Use first letter heuristics
    if first_letter in ["E", "L", "U"]:
        return "EUR"  # European range
    elif first_letter in ["V", "W", "Z", "R", "P", "N"]:
        return "APAC"  # Asia-Pacific range
    elif first_letter in ["S"]:
        return "SAM"  # South American range
    elif first_letter in ["F", "G", "H"]:
        return "AFI"  # African range
    elif first_letter in ["O", "D"]:
        return "MID"  # Middle East range
    else:
        # Unknown region - default to NAM for safety
        return "NAM"


# =============================================================================
# Statistics Configuration (User Decision 1: Indefinite Retention)
# =============================================================================

# Enable statistics collection
ENABLE_STATISTICS = os.getenv("ENABLE_STATISTICS", "true").lower() == "true"

# Database table for translation records
STATISTICS_TABLE = "translation_statistics"

# Data retention policy (indefinite as per user decision 1)
STATISTICS_RETENTION_DAYS = None  # None = indefinite retention

# Aggregation intervals for pre-computed statistics
STATISTICS_AGGREGATION_INTERVALS = ["1h", "1d", "7d", "30d"]


# =============================================================================
# Webhook Configuration (User Decision 2)
# =============================================================================

# Enable webhook notifications for translation events
ENABLE_WEBHOOKS = os.getenv("ENABLE_WEBHOOKS", "false").lower() == "true"

# Webhook endpoints (comma-separated URLs)
WEBHOOK_URLS = os.getenv("WEBHOOK_URLS", "").split(",") if os.getenv("WEBHOOK_URLS") else []

# Webhook authentication
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# Events that trigger webhooks
WEBHOOK_EVENTS = [
    "translation.success",
    "translation.failed",
    "validation.failed",
    "bulk.completed",
]


# =============================================================================
# Supported IWXXM Versions
# =============================================================================

SUPPORTED_IWXXM_VERSIONS = ["2025-2", "2023-1"]
DEFAULT_IWXXM_VERSION = "2025-2"


# =============================================================================
# Helper Functions
# =============================================================================


def get_translation_centre_info() -> Dict[str, any]:
    """
    Get Translation Centre metadata for IWXXM documents.

    Returns:
        Dictionary with Translation Centre information
    """
    return {
        "translationCentreName": TRANSLATION_CENTRE_NAME,
        "translationCentreDesignator": TRANSLATION_CENTRE_DESIGNATOR,
        "icaoLocationIndicator": ICAO_LOCATION_INDICATOR,
        "serviceOnlineSince": SERVICE_ONLINE_SINCE,
        "technicalContact": TECHNICAL_CONTACT_EMAIL,
        "supportedIwxxmVersions": SUPPORTED_IWXXM_VERSIONS,
        "supportedProducts": ["METAR", "SPECI"],
    }


def should_log_statistics() -> bool:
    """Check if statistics logging is enabled."""
    return ENABLE_STATISTICS


def should_send_webhooks() -> bool:
    """Check if webhook notifications are enabled."""
    return ENABLE_WEBHOOKS and len(WEBHOOK_URLS) > 0
