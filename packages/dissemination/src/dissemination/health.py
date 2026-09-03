"""GatewayHealth helpers for DisseminationGateway (ADR-041 / EV-936)."""

from __future__ import annotations

from dataclasses import dataclass

from dissemination.f19_stubs import F19_SINK_TYPES


@dataclass(frozen=True, slots=True)
class GatewayHealth:
    """
    Connectivity-only health snapshot for one gateway kind.

    Parameters
    ----------
    ok :
        Overall operator-facing health (never implies message delivery).
    gateway :
        Gateway kind discriminator (``postgres``, ``wis2``, ``amhs``, …).
    connectivity_ok :
        Whether a live probe succeeded.
    detail :
        Operator-safe detail — never BYOC secrets or raw URIs.
    """

    ok: bool
    gateway: str
    connectivity_ok: bool
    detail: str | None = None


def default_health_for_kind(gateway_kind: str) -> GatewayHealth:
    """
    Return a default health row when no live probe is registered.

    F19 kinds (``amhs`` / ``swim`` / ``afs``) are staging-honest: not green until a
    live pathway is configured. Other kinds report that no probe ran.

    Parameters
    ----------
    gateway_kind :
        Sink / gateway discriminator.

    Returns
    -------
    GatewayHealth
        Operator-safe health row.
    """
    if gateway_kind in F19_SINK_TYPES:
        return GatewayHealth(
            ok=False,
            gateway=gateway_kind,
            connectivity_ok=False,
            detail="Staging adapter only; live pathway not configured",
        )
    return GatewayHealth(
        ok=False,
        gateway=gateway_kind,
        connectivity_ok=False,
        detail="No live probe configured",
    )


__all__ = ["GatewayHealth", "default_health_for_kind"]
