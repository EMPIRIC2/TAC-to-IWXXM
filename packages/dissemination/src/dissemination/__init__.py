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
from dissemination.gateway import DisseminationGateway, DisseminationMessage
from dissemination.health import GatewayHealth, default_health_for_kind
from dissemination.plan import DisseminationPlan, execute_plan
from dissemination.transforms import (
    TransformResult,
    TransformStep,
    apply_dissemination_transforms,
    normalize_transform_steps,
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
    "DisseminationGateway",
    "DisseminationMessage",
    "DisseminationPlan",
    "EgressDenied",
    "GatewayHealth",
    "SchemaDiff",
    "TransformResult",
    "TransformStep",
    "__version__",
    "apply_dissemination_transforms",
    "apply_writer_contract",
    "default_health_for_kind",
    "diff_writer_contract",
    "execute_plan",
    "load_allowlist_from_env",
    "normalize_transform_steps",
    "parse_allowlist",
    "validate_egress_host",
    "writer_contract_ddl",
]
