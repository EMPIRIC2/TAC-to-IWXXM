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
from metar_shared.supabase_env import (
    get_supabase_publishable_key,
    get_supabase_secret_key,
    get_supabase_url,
)
from metar_shared.xml_canonical import (
    canonicalize_xml,
    compare_canonical_xml,
    diff_canonical_xml,
)

__all__ = [
    "DEFAULT_PROFILE_IDS",
    "METAR_CORS_ORIGINS_ENV",
    "PREFER_PRODUCTS",
    "VITE_API_BASE_URL_ENV",
    "VITE_APP_URL_ENV",
    "VITE_SUPABASE_PUBLISHABLE_KEY_ENV",
    "VITE_SUPABASE_URL_ENV",
    "EffectiveBundle",
    "InheritNode",
    "LayerOverrides",
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
    "load_config",
    "parse_comma_separated_origins",
    "resolve_inherit_tree",
    "should_prefer_station",
]
