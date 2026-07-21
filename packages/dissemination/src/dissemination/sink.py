"""Shared sink adapter Protocol for F16–F19 dissemination (E14-05 / ADR-030).

Concrete sinks (DB, WIS2, EDIS, F19 staging stubs) expose the same preflight/send
shape so the drawer and thin backend routers can dispatch by ``sink_type``.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from dissemination.allowlist import Allowlist
from dissemination.models import PreflightResponse, SendResponse, SinkType


@runtime_checkable
class SinkAdapter(Protocol):
    """
    Common preflight + send contract for operator dissemination sinks.

    Parameters for both methods are sink-specific (URI, MQTT, SMTP, AMHS, …) and
    must never be logged raw; allowlist/SSRF checks apply before egress.
    """

    @property
    def sink_type(self) -> SinkType:
        """Drawer / API sink discriminator."""

    async def preflight(
        self,
        *,
        params: Any,
        allowlist: Allowlist,
    ) -> PreflightResponse:
        """
        Connectivity / schema preflight without committing the payload.

        Raises
        ------
        EgressDenied
            When destination hosts are not allowlisted.
        ValueError
            When params or transport checks fail (secrets redacted).
        """

    async def send(
        self,
        *,
        params: Any,
        allowlist: Allowlist,
        iwxxm_xml: str | bytes | None = None,
        tac_text: str | None = None,
    ) -> SendResponse:
        """
        Deliver IWXXM and/or TAC to the sink after allowlist checks.

        Raises
        ------
        EgressDenied
            When destination hosts are not allowlisted.
        ValueError
            When params, payload, or transport fail (secrets redacted).
        """


__all__ = ["SinkAdapter"]
