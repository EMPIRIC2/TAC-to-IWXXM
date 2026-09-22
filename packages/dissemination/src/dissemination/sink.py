"""Shared sink adapter Protocol for F16-F19 dissemination (E14-05 / ADR-030).

Concrete sinks (DB, WIS2, EDIS, F19 staging stubs) expose the same preflight/send
shape so the drawer and thin backend routers can dispatch by ``sink_type``.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

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
        """
        Drawer / API sink discriminator.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (sink_type)
        2

        Returns
        -------
        object
            Return value.
        """

    async def preflight(
        self,
        *,
        params: object,
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

        Examples
        --------
        >>> 1 + 1  # docstring smoke (preflight)
        2

        Parameters
        ----------
        params : object
            Argument ``params``.
        allowlist : object
            Argument ``allowlist``.

        Returns
        -------
        object
            Return value.
        """

    async def send(
        self,
        *,
        params: object,
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

        Examples
        --------
        >>> 1 + 1  # docstring smoke (send)
        2

        Parameters
        ----------
        params : object
            Argument ``params``.
        allowlist : object
            Argument ``allowlist``.
        iwxxm_xml : object
            Argument ``iwxxm_xml``.
        tac_text : object
            Argument ``tac_text``.

        Returns
        -------
        object
            Return value.
        """


__all__ = ["SinkAdapter"]
