"""Shared cross-cutting utilities for the METAR to IWXXM monorepo."""

from metar_shared.config_loader import (
    get_config_env,
    get_cors_origins_from_config,
    get_frontend_url_from_config,
    load_config,
)
from metar_shared.constants import (
    METAR_CORS_ORIGINS_ENV,
    VITE_API_BASE_URL_ENV,
    VITE_APP_URL_ENV,
    VITE_SUPABASE_PUBLISHABLE_KEY_ENV,
    VITE_SUPABASE_URL_ENV,
)
from metar_shared.env import parse_comma_separated_origins
from metar_shared.inherit_factory import (
    DEFAULT_PROFILE_IDS,
    PREFER_PRODUCTS,
    EffectiveBundle,
    InheritNode,
    LayerOverrides,
    empty_bundle,
    resolve_inherit_tree,
    should_prefer_station,
)
from metar_shared.models import AhlHeadingParts, StationIcao
from metar_shared.supabase_env import (
    get_supabase_publishable_key,
    get_supabase_secret_key,
    get_supabase_url,
)
from metar_shared.tac_patterns import (
    AHL_HEADING_LINE,
    AHL_HEADING_LINE_BBB3,
    STATION_ICAO_FULLMATCH,
    STATION_ICAO_TOKEN,
    is_ahl_heading_line,
    is_station_icao,
    parse_ahl_heading_line,
    parse_station_icao,
    replace_ahl_heading_mapping,
)
from metar_shared.xml_canonical import (
    canonicalize_xml,
    compare_canonical_xml,
    diff_canonical_xml,
)

__all__ = [
    "AHL_HEADING_LINE",
    "AHL_HEADING_LINE_BBB3",
    "DEFAULT_PROFILE_IDS",
    "METAR_CORS_ORIGINS_ENV",
    "PREFER_PRODUCTS",
    "STATION_ICAO_FULLMATCH",
    "STATION_ICAO_TOKEN",
    "VITE_API_BASE_URL_ENV",
    "VITE_APP_URL_ENV",
    "VITE_SUPABASE_PUBLISHABLE_KEY_ENV",
    "VITE_SUPABASE_URL_ENV",
    "AhlHeadingParts",
    "EffectiveBundle",
    "InheritNode",
    "LayerOverrides",
    "StationIcao",
    "canonicalize_xml",
    "compare_canonical_xml",
    "diff_canonical_xml",
    "empty_bundle",
    "get_config_env",
    "get_cors_origins_from_config",
    "get_frontend_url_from_config",
    "get_supabase_publishable_key",
    "get_supabase_secret_key",
    "get_supabase_url",
    "is_ahl_heading_line",
    "is_station_icao",
    "load_config",
    "parse_ahl_heading_line",
    "parse_comma_separated_origins",
    "parse_station_icao",
    "replace_ahl_heading_mapping",
    "resolve_inherit_tree",
    "should_prefer_station",
]
