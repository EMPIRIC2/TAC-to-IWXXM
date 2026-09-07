"""DisseminationGateway façade over SinkAdapter (ADR-041 / EV-936).

Maps ``validate`` → adapter ``preflight``, ``send`` → adapter ``send``, and
``health`` → connectivity-only probes. Does not replace the HTTP SinkAdapter
drawer contract.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

from dissemination.allowlist import Allowlist
from dissemination.health import GatewayHealth, default_health_for_kind
from dissemination.models import PreflightResponse, SchemaDiffItem
from dissemination.redact import redact_secrets
from dissemination.sink import SinkAdapter

DeliveryStatus = Literal["DELIVERED", "FAILED", "SKIPPED"]

HealthProbe = Callable[[str], Awaitable[GatewayHealth]]


@dataclass(frozen=True, slots=True)
class DisseminationMessage:
    """
    Message envelope for gateway validate/send.

    Parameters
    ----------
    gateway_kind :
        Registry key (usually a ``SinkType`` string).
    params :
        Sink-specific connection params (memory-only; never logged raw).
    allowlist :
        Egress allowlist for adapter checks.
    iwxxm_xml :
        Optional IWXXM payload.
    tac_text :
        Optional TAC payload (e.g. EDIS).
    """

    gateway_kind: str
    params: object
    allowlist: Allowlist
    iwxxm_xml: str | bytes | None = None
    tac_text: str | None = None


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Gateway validate outcome mapped from ``PreflightResponse``."""

    ok: bool
    connectivity_ok: bool
    diffs: list[SchemaDiffItem]
    detail: str | None = None
    handle: str | None = None


@dataclass(frozen=True, slots=True)
class DeliveryReceipt:
    """
    Delivery audit row (ADR-041) — never stores BYOC secrets.

    Parameters
    ----------
    status :
        ``DELIVERED`` | ``FAILED`` | ``SKIPPED``.
    gateway :
        Gateway kind used for the attempt.
    detail :
        Operator-safe detail.
    idempotency_key :
        Optional idempotency token.
    attempt :
        Attempt number (1-based).
    completed_at :
        UTC completion timestamp.
    """

    status: DeliveryStatus
    gateway: str
    detail: str | None = None
    idempotency_key: str | None = None
    attempt: int = 1
    completed_at: datetime | None = None


def _from_preflight(pre: PreflightResponse) -> ValidationResult:
    return ValidationResult(
        ok=pre.ok,
        connectivity_ok=pre.connectivity_ok,
        diffs=list(pre.diffs),
        detail=pre.detail,
        handle=pre.handle,
    )


class DisseminationGateway:
    """
    Thin registry façade over existing ``SinkAdapter`` implementations.

    Parameters
    ----------
    adapters :
        Map of ``gateway_kind`` → adapter.
    health_probe :
        Optional async probe; defaults to :func:`default_health_for_kind`.
    """

    def __init__(
        self,
        *,
        adapters: Mapping[str, SinkAdapter],
        health_probe: HealthProbe | None = None,
    ) -> None:
        self._adapters = dict(adapters)
        self._health_probe = health_probe

    def _adapter(self, gateway_kind: str) -> SinkAdapter:
        try:
            return self._adapters[gateway_kind]
        except KeyError as exc:
            raise KeyError(f"unknown gateway_kind: {gateway_kind!r}") from exc

    async def validate(self, message: DisseminationMessage) -> ValidationResult:
        """
        Run adapter preflight for ``message.gateway_kind``.

        Parameters
        ----------
        message :
            Envelope with params and allowlist.

        Returns
        -------
        ValidationResult
            Mapped preflight outcome.

        Raises
        ------
        KeyError
            When ``gateway_kind`` is not registered.
        """
        adapter = self._adapter(message.gateway_kind)
        pre = await adapter.preflight(
            params=message.params,
            allowlist=message.allowlist,
        )
        return _from_preflight(pre)

    async def send(self, message: DisseminationMessage) -> DeliveryReceipt:
        """
        Deliver via adapter send; map outcome to ``DeliveryReceipt``.

        Parameters
        ----------
        message :
            Envelope with optional payloads.

        Returns
        -------
        DeliveryReceipt
            ``DELIVERED`` or ``FAILED`` (exceptions become ``FAILED`` with
            redacted detail).

        Raises
        ------
        KeyError
            When ``gateway_kind`` is not registered.
        """
        adapter = self._adapter(message.gateway_kind)
        completed = datetime.now(UTC)
        try:
            resp = await adapter.send(
                params=message.params,
                allowlist=message.allowlist,
                iwxxm_xml=message.iwxxm_xml,
                tac_text=message.tac_text,
            )
        except Exception as exc:
            return DeliveryReceipt(
                status="FAILED",
                gateway=message.gateway_kind,
                detail=redact_secrets(str(exc)),
                attempt=1,
                completed_at=completed,
            )
        return DeliveryReceipt(
            status="DELIVERED" if resp.ok else "FAILED",
            gateway=message.gateway_kind,
            detail=resp.detail,
            attempt=1,
            completed_at=completed,
        )

    async def health(self, gateway_kind: str | None = None) -> list[GatewayHealth]:
        """
        Connectivity-only health for one or all registered gateway kinds.

        Parameters
        ----------
        gateway_kind :
            Optional single kind; when omitted, all registered adapters.

        Returns
        -------
        list of GatewayHealth
            One row per kind.
        """
        kinds = [gateway_kind] if gateway_kind is not None else sorted(self._adapters)
        rows: list[GatewayHealth] = []
        for kind in kinds:
            if self._health_probe is not None:
                rows.append(await self._health_probe(kind))
            else:
                rows.append(default_health_for_kind(kind))
        return rows


__all__ = [
    "DeliveryReceipt",
    "DeliveryStatus",
    "DisseminationGateway",
    "DisseminationMessage",
    "GatewayHealth",
    "HealthProbe",
    "ValidationResult",
    "default_health_for_kind",
]
