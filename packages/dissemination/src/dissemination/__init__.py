"""Dissemination sinks, writer-contract, and SSRF/allowlist helpers (F16–F19).

No FastAPI or Supabase imports (ADR-030). Thin HTTP routers live in ``apps/backend``.
"""

from __future__ import annotations

from dissemination.allowlist import (
    Allowlist,
    AllowlistError,
    EgressDenied,
    load_allowlist_from_env,
    parse_allowlist,
    validate_egress_host,
)

__version__ = "0.1.0"

__all__ = [
    "Allowlist",
    "AllowlistError",
    "EgressDenied",
    "__version__",
    "load_allowlist_from_env",
    "parse_allowlist",
    "validate_egress_host",
]
