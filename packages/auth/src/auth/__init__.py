"""Compatibility package exposing auth modules from the flat src layout."""

from admin_api import router as admin_router  # noqa: F401
from api_supabase import router  # noqa: F401
from supabase_proxy import get_supabase_proxy  # noqa: F401

__all__ = ["router", "admin_router", "get_supabase_proxy"]
