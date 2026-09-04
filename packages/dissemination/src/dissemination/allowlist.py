"""Egress allowlist and SSRF guards for dissemination destinations (ADR-029).

``DISSEMINATION_EGRESS_ALLOWLIST`` is a comma-separated list of hostnames and/or
CIDRs. An empty allowlist is **fail-closed** - no user-host egress.
"""

from __future__ import annotations

import ipaddress
import os
import socket
from collections.abc import Iterable
from dataclasses import dataclass

ENV_ALLOWLIST = "DISSEMINATION_EGRESS_ALLOWLIST"

# Always blocked - cloud instance metadata / link-local IMDS style targets.
_BLOCKED_NETWORKS: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...] = (
    ipaddress.ip_network("169.254.0.0/16"),  # link-local / AWS IMDS
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
    ipaddress.ip_network("fd00:ec2::/32"),  # AWS IPv6 IMDS prefix (common)
)

_BLOCKED_HOSTNAMES = frozenset(
    {
        "metadata.google.internal",
        "metadata.goog",
        "instance-data",
    }
)


class AllowlistError(ValueError):
    """Raised when an allowlist token cannot be parsed."""


class EgressDenied(PermissionError):
    """Raised when a destination host is not permitted for egress."""


@dataclass(frozen=True, slots=True)
class Allowlist:
    """Parsed egress allowlist entries."""

    hostnames: frozenset[str]
    networks: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...]

    @property
    def is_empty(self) -> bool:
        """Return ``True`` when no hostnames or CIDR networks are configured."""
        return not self.hostnames and not self.networks

    @property
    def entries(self) -> tuple[str, ...]:
        """Return sorted hostnames followed by CIDR strings for display/logging."""
        hosts = sorted(self.hostnames)
        nets = [str(n) for n in self.networks]
        return tuple(hosts + nets)


def parse_allowlist(raw: str | None) -> Allowlist:
    """
    Parse a comma-separated host/CIDR allowlist string.

    Parameters
    ----------
    raw :
        Allowlist text, or ``None`` / blank for an empty (fail-closed) list.

    Returns
    -------
    Allowlist
        Parsed hostnames and networks.

    Raises
    ------
    AllowlistError
        If a token is neither a hostname nor a CIDR/IP.
    """
    if raw is None or not raw.strip():
        return Allowlist(hostnames=frozenset(), networks=())

    hostnames: set[str] = set()
    networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
    for token in raw.split(","):
        item = token.strip().lower()
        if not item:
            continue
        try:
            networks.append(ipaddress.ip_network(item, strict=False))
            continue
        except ValueError:
            pass
        if _is_hostname(item):
            hostnames.add(item)
            continue
        raise AllowlistError(f"invalid allowlist token: {token!r}")
    return Allowlist(hostnames=frozenset(hostnames), networks=tuple(networks))


def load_allowlist_from_env(
    *,
    env_var: str = ENV_ALLOWLIST,
    environ: os._Environ[str] | None = None,
) -> Allowlist:
    """Load and parse ``DISSEMINATION_EGRESS_ALLOWLIST`` from the process environment."""
    env = environ if environ is not None else os.environ
    return parse_allowlist(env.get(env_var))


def validate_egress_host(
    host: str,
    *,
    allowlist: Allowlist | None = None,
) -> None:
    """
    Validate that ``host`` may be used for dissemination egress.

    Empty allowlist ⇒ fail-closed. Hostname must appear on the allowlist (or
    resolve into an allowlisted CIDR). Resolved addresses that fall in blocked
    metadata/link-local ranges are always denied. Private resolved IPs require
    an overlapping allowlisted CIDR (DNS-rebinding guard).

    Parameters
    ----------
    host :
        Destination hostname or literal IP.
    allowlist :
        Parsed allowlist; when ``None``, loaded from the environment.

    Raises
    ------
    EgressDenied
        If the host is not permitted.
    """
    al = allowlist if allowlist is not None else load_allowlist_from_env()
    normalized = host.strip().lower().rstrip(".")
    if not normalized:
        raise EgressDenied("empty host denied")

    if al.is_empty:
        raise EgressDenied(f"egress fail-closed: {ENV_ALLOWLIST} is empty - no user-host egress")

    if normalized in _BLOCKED_HOSTNAMES:
        raise EgressDenied(f"blocked metadata hostname: {normalized}")

    # Literal IP destination.
    try:
        addr = ipaddress.ip_address(normalized)
    except ValueError:
        addr = None

    if addr is not None:
        _deny_if_blocked_ip(addr)
        if not _ip_on_allowlist(addr, al):
            raise EgressDenied(f"IP {normalized} not on allowlist")
        return

    if normalized not in al.hostnames:
        raise EgressDenied(f"host {normalized!r} not on allowlist")

    resolved = _resolve_ips(normalized)
    if not resolved:
        raise EgressDenied(f"host {normalized!r} did not resolve")

    for ip in resolved:
        _deny_if_blocked_ip(ip)
        # Private/loopback/link-local require an overlapping CIDR so a hostname
        # allowlist entry cannot DNS-rebind into an unlisted LAN (ADR-029).
        if (ip.is_private or ip.is_loopback or ip.is_link_local) and not _ip_on_allowlist(ip, al):
            raise EgressDenied(
                f"resolved private/reserved address {ip} for {normalized!r} not covered by allowlisted CIDR"
            )


def _is_hostname(value: str) -> bool:
    if len(value) > 253 or " " in value or value.startswith("-"):
        return False
    labels = value.split(".")
    if not labels:
        return False
    for label in labels:
        if not label or len(label) > 63:
            return False
        if label.startswith("-") or label.endswith("-"):
            return False
        if not all(c.isalnum() or c == "-" for c in label):
            return False
    return True


def _deny_if_blocked_ip(addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> None:
    for net in _BLOCKED_NETWORKS:
        if addr in net:
            raise EgressDenied(f"blocked metadata/link-local address: {addr}")


def _ip_on_allowlist(
    addr: ipaddress.IPv4Address | ipaddress.IPv6Address,
    allowlist: Allowlist,
) -> bool:
    if str(addr) in allowlist.hostnames:
        return True
    return any(addr in net for net in allowlist.networks)


def _resolve_ips(host: str) -> list[ipaddress.IPv4Address | ipaddress.IPv6Address]:
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError:
        return []
    out: list[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
    seen: set[str] = set()
    for info in infos:
        sockaddr = info[4]
        ip_s = sockaddr[0]
        if ip_s in seen:
            continue
        seen.add(ip_s)
        out.append(ipaddress.ip_address(ip_s))
    return out


def iter_allowlist_entries(allowlist: Allowlist) -> Iterable[str]:
    """Yield human-readable allowlist entries (hosts then CIDRs)."""
    yield from allowlist.entries
