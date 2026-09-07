"""DisseminationPlan execute helper (ADR-041 / EV-936).

Runtime plan execution over :class:`DisseminationGateway`. Persistence of audit
rows is injected via ``audit_sink`` (backend owns Postgres writes).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime

from dissemination.gateway import (
    DeliveryReceipt,
    DisseminationGateway,
    DisseminationMessage,
)


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Retry knobs for plan execute (documented; used by later milestones)."""

    max_attempts: int = 1
    backoff_seconds: float = 0.0


@dataclass(frozen=True, slots=True)
class DisseminationPlan:
    """
    Operator DisseminationPlan (policy + destination refs — no secrets).

    Parameters
    ----------
    plan_id :
        Stable plan identifier.
    validity_policy :
        ``valid-only`` requires green validate before send; ``warn-ok`` sends anyway.
    destination_refs :
        Gateway kinds (or destination ids resolved by the caller) to send to.
    transforms :
        Optional exchange packaging refs.
    retry :
        Optional retry policy.
    dry_run :
        When true, produce ``SKIPPED`` receipts without calling send.
    """

    plan_id: str
    validity_policy: str
    destination_refs: list[str]
    transforms: list[str] = field(default_factory=list)
    retry: RetryPolicy | None = None
    dry_run: bool = False


AuditSink = Callable[[DeliveryReceipt], Awaitable[None]]


async def execute_plan(
    plan: DisseminationPlan,
    message: DisseminationMessage,
    gateway: DisseminationGateway,
    *,
    audit_sink: AuditSink | None = None,
) -> list[DeliveryReceipt]:
    """
    Execute a plan against ``gateway`` for each destination ref.

    Parameters
    ----------
    plan :
        Plan document (no BYOC secrets).
    message :
        Base message; ``gateway_kind`` is replaced per destination ref.
    gateway :
        Façade used for validate/send.
    audit_sink :
        Optional async callback per receipt (e.g. persist redacted audit).

    Returns
    -------
    list of DeliveryReceipt
        One receipt per destination ref.
    """
    receipts: list[DeliveryReceipt] = []
    for ref in plan.destination_refs:
        msg = DisseminationMessage(
            gateway_kind=ref,
            params=message.params,
            allowlist=message.allowlist,
            iwxxm_xml=message.iwxxm_xml,
            tac_text=message.tac_text,
        )
        completed = datetime.now(UTC)
        if plan.dry_run:
            receipt = DeliveryReceipt(
                status="SKIPPED",
                gateway=ref,
                detail="dry_run",
                attempt=1,
                completed_at=completed,
            )
        elif plan.validity_policy == "valid-only":
            validation = await gateway.validate(msg)
            if not validation.ok:
                receipt = DeliveryReceipt(
                    status="SKIPPED",
                    gateway=ref,
                    detail=validation.detail or "validate failed",
                    attempt=1,
                    completed_at=completed,
                )
            else:
                receipt = await gateway.send(msg)
        else:
            receipt = await gateway.send(msg)

        receipts.append(receipt)
        if audit_sink is not None:
            await audit_sink(receipt)
    return receipts


__all__ = [
    "AuditSink",
    "DisseminationPlan",
    "RetryPolicy",
    "execute_plan",
]
