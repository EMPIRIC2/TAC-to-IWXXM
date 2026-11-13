"""WIS2 exchange-admin helpers (single role, GitOps allowlist, memory templates).

Locked v1 defaults:
- One role: ``exchange-admin``
- Invitation groups selected at login (multi-tenant)
- Egress allowlist is read-only (GitOps / env is source of truth)
- No admin replay (drawer re-send only)
- WIS2-only admin surface
- Memory-only BYOC + non-secret templates (no vault)
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from dissemination.allowlist import Allowlist, load_allowlist_from_env

EXCHANGE_ADMIN_ROLE = "exchange-admin"


@dataclass(frozen=True, slots=True)
class InvitationGroup:
    """Tenant invitation group offered at login."""

    id: str
    name: str
    centre_id: str


@dataclass
class NonSecretTemplate:
    """Memory-only non-secret WIS2 destination template (no passwords)."""

    id: str
    name: str
    mqtt_host: str
    mqtt_topic: str
    dataset_url: str
    mqtt_port: int = 8883
    centre_id: str | None = None
    use_tls: bool = True
    owner_sub: str = ""
    created_at: float = field(default_factory=time.time)


@dataclass
class OperatorExchangePrefs:
    """Per-operator exchange preferences (memory-only in v1)."""

    include_national_remarks: bool = False
    invitation_group_id: str | None = None


_DEFAULT_GROUPS: tuple[InvitationGroup, ...] = (
    InvitationGroup(id="group-demo-a", name="Demo Centre A", centre_id="demo-a"),
    InvitationGroup(id="group-demo-b", name="Demo Centre B", centre_id="demo-b"),
)

_templates: dict[str, NonSecretTemplate] = {}
_prefs: dict[str, OperatorExchangePrefs] = {}
_lock = threading.Lock()


def user_has_exchange_admin(user: dict[str, Any]) -> bool:
    """
    Return True when JWT claims include the exchange-admin role.

    Checks ``app_metadata.roles``, ``user_metadata.roles``, and top-level ``role``.

    Examples
    --------
    >>> user_has_exchange_admin({"app_metadata": {"roles": ["exchange-admin"]}})
    True
    >>> user_has_exchange_admin({})
    False
    """
    roles: list[str] = []
    for bag_key in ("app_metadata", "user_metadata"):
        bag = user.get(bag_key)
        if isinstance(bag, dict):
            raw = bag.get("roles") or bag.get("role")
            if isinstance(raw, str):
                roles.append(raw)
            elif isinstance(raw, (list, tuple)):
                roles.extend(str(r) for r in raw)
    top = user.get("role")
    if isinstance(top, str):
        roles.append(top)
    return EXCHANGE_ADMIN_ROLE in {r.strip().lower() for r in roles if r}


def list_invitation_groups() -> list[InvitationGroup]:
    """
    Return invitation groups offered at login.

    Examples
    --------
    >>> len(list_invitation_groups()) >= 1
    True
    """
    return list(_DEFAULT_GROUPS)


def allowlist_view() -> dict[str, Any]:
    """
    Read-only projection of the GitOps egress allowlist.

    Examples
    --------
    >>> "entries" in allowlist_view()
    True
    """
    allow: Allowlist = load_allowlist_from_env()
    return {
        "source": "DISSEMINATION_EGRESS_ALLOWLIST",
        "read_only": True,
        "fail_closed": allow.is_empty,
        "entries": list(allow.entries),
        "admin_replay": False,
        "sink_scope": "wis2",
    }


def get_prefs(sub: str) -> OperatorExchangePrefs:
    """Return memory prefs for ``sub``, creating defaults when absent."""
    with _lock:
        prefs = _prefs.get(sub)
        if prefs is None:
            prefs = OperatorExchangePrefs()
            _prefs[sub] = prefs
        return prefs


def set_national_remarks(sub: str, include: bool) -> OperatorExchangePrefs:
    """
    Toggle whether national remarks ride along on WIS2 publish.

    Examples
    --------
    >>> p = set_national_remarks("u1", True)
    >>> p.include_national_remarks
    True
    """
    with _lock:
        prefs = _prefs.get(sub) or OperatorExchangePrefs()
        prefs.include_national_remarks = bool(include)
        _prefs[sub] = prefs
        return prefs


def set_invitation_group(sub: str, group_id: str) -> OperatorExchangePrefs:
    """
    Bind the operator to one invitation group chosen at login.

    Raises
    ------
    ValueError
        When ``group_id`` is unknown.

    Examples
    --------
    >>> p = set_invitation_group("u1", "group-demo-a")
    >>> p.invitation_group_id
    'group-demo-a'
    """
    known = {g.id for g in _DEFAULT_GROUPS}
    if group_id not in known:
        raise ValueError(f"unknown invitation group: {group_id}")
    with _lock:
        prefs = _prefs.get(sub) or OperatorExchangePrefs()
        prefs.invitation_group_id = group_id
        _prefs[sub] = prefs
        return prefs


def list_templates(sub: str) -> list[NonSecretTemplate]:
    """List non-secret templates owned by ``sub``."""
    with _lock:
        return [t for t in _templates.values() if t.owner_sub == sub]


def upsert_template(sub: str, body: dict[str, Any]) -> NonSecretTemplate:
    """
    Create or replace a non-secret WIS2 template (memory-only; no vault).

    Raises
    ------
    ValueError
        When required fields are missing.

    Examples
    --------
    >>> t = upsert_template(
    ...     "u1",
    ...     {
    ...         "name": "Demo",
    ...         "mqtt_host": "h",
    ...         "mqtt_topic": "t",
    ...         "dataset_url": "http://x/y",
    ...     },
    ... )
    >>> t.name
    'Demo'
    """
    name = str(body.get("name") or "").strip()
    host = str(body.get("mqtt_host") or "").strip()
    topic = str(body.get("mqtt_topic") or "").strip()
    dataset = str(body.get("dataset_url") or "").strip()
    if not name or not host or not topic or not dataset:
        raise ValueError("name, mqtt_host, mqtt_topic, and dataset_url are required")
    # Reject accidental secret fields — vault is out of scope for v1.
    for secret_key in ("mqtt_password", "password", "token", "secret"):
        if body.get(secret_key):
            raise ValueError("secret fields are not stored; paste BYOC at send time")
    template_id = str(body.get("id") or "").strip() or f"tmpl_{uuid.uuid4().hex[:12]}"
    tmpl = NonSecretTemplate(
        id=template_id,
        name=name,
        mqtt_host=host,
        mqtt_topic=topic,
        dataset_url=dataset,
        mqtt_port=int(body.get("mqtt_port") or 8883),
        centre_id=(str(body.get("centre_id")).strip() if body.get("centre_id") else None),
        use_tls=bool(body.get("use_tls", True)),
        owner_sub=sub,
    )
    with _lock:
        _templates[template_id] = tmpl
    return tmpl


def clear_exchange_admin_state() -> None:
    """Reset memory stores (tests only)."""
    with _lock:
        _templates.clear()
        _prefs.clear()


__all__ = [
    "EXCHANGE_ADMIN_ROLE",
    "InvitationGroup",
    "NonSecretTemplate",
    "OperatorExchangePrefs",
    "allowlist_view",
    "clear_exchange_admin_state",
    "get_prefs",
    "list_invitation_groups",
    "list_templates",
    "set_invitation_group",
    "set_national_remarks",
    "upsert_template",
    "user_has_exchange_admin",
]
