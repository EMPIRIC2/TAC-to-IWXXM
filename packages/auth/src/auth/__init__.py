"""Compatibility package exposing auth modules from the flat src layout."""

from api_supabase import router  # noqa: F401
from supabase_proxy import get_supabase_proxy  # noqa: F401

__all__ = ["router", "get_supabase_proxy"]
