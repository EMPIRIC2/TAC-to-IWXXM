"""Dissemination sinks, writer-contract, and SSRF/allowlist helpers (F16-F19).

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
from dissemination.writer_contract import (
    CONTRACT_TABLE,
    CONTRACT_VERSION,
    DiffKind,
    SchemaDiff,
    apply_writer_contract,
    diff_writer_contract,
    writer_contract_ddl,
)

__version__ = "0.1.0"

__all__ = [
    "CONTRACT_TABLE",
    "CONTRACT_VERSION",
    "Allowlist",
    "AllowlistError",
    "DiffKind",
    "EgressDenied",
    "SchemaDiff",
    "__version__",
    "apply_writer_contract",
    "diff_writer_contract",
    "load_allowlist_from_env",
    "parse_allowlist",
    "validate_egress_host",
    "writer_contract_ddl",
]
