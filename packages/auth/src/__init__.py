"""Auth package public API."""

from auth.api_supabase import router  # re-export for convenience
from auth.supabase_proxy import get_supabase_proxy  # re-export for convenience

__all__ = ["router", "get_supabase_proxy"]
