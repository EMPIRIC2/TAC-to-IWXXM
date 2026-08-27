"""Allowlist / SSRF helpers - fail-closed + private/metadata deny (T1.3 / ADR-029)."""

from __future__ import annotations

import ipaddress
from unittest.mock import patch

import pytest
from dissemination.allowlist import (
    AllowlistError,
    EgressDenied,
    load_allowlist_from_env,
    parse_allowlist,
    validate_egress_host,
)


def test_parse_allowlist_empty_or_whitespace_is_empty() -> None:
    assert parse_allowlist(None).entries == ()
    assert parse_allowlist("").entries == ()
    assert parse_allowlist("  , , ").entries == ()


def test_parse_allowlist_hosts_and_cidrs() -> None:
    al = parse_allowlist("example.com, 10.0.0.0/8, 2001:db8::/32")
    assert "example.com" in al.hostnames
    assert ipaddress.ip_network("10.0.0.0/8") in al.networks
    assert ipaddress.ip_network("2001:db8::/32") in al.networks


def test_load_allowlist_from_env_fail_closed_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DISSEMINATION_EGRESS_ALLOWLIST", raising=False)
    al = load_allowlist_from_env()
    assert al.is_empty
    with pytest.raises(EgressDenied, match=r"fail-closed|allowlist"):
        validate_egress_host("example.com", allowlist=al)


def test_load_allowlist_from_env_fail_closed_when_empty_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "")
    al = load_allowlist_from_env()
    assert al.is_empty
    with pytest.raises(EgressDenied):
        validate_egress_host("db.example.com", allowlist=al)


def test_validate_allows_listed_hostname_with_public_resolved_ip() -> None:
    al = parse_allowlist("db.example.com")
    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("8.8.8.8", 0))],
    ):
        validate_egress_host("db.example.com", allowlist=al)


def test_validate_denies_host_not_on_allowlist() -> None:
    al = parse_allowlist("allowed.example.com")
    with pytest.raises(EgressDenied, match="not on allowlist"):
        validate_egress_host("other.example.com", allowlist=al)


def test_validate_denies_cloud_metadata_even_if_allowlisted() -> None:
    al = parse_allowlist("169.254.169.254, metadata.google.internal")
    with pytest.raises(EgressDenied, match=r"metadata|blocked"):
        validate_egress_host("169.254.169.254", allowlist=al)


def test_validate_denies_dns_rebinding_to_private_when_not_in_cidr() -> None:
    """Hostname allowlisted, but resolved A record is private and not in an allowlisted CIDR."""
    al = parse_allowlist("tricky.example.com")
    with (
        patch(
            "dissemination.allowlist.socket.getaddrinfo",
            return_value=[(None, None, None, None, ("10.1.2.3", 0))],
        ),
        pytest.raises(EgressDenied, match=r"private|resolved"),
    ):
        validate_egress_host("tricky.example.com", allowlist=al)


def test_validate_allows_private_ip_when_cidr_allowlisted() -> None:
    al = parse_allowlist("wis2box, 10.0.0.0/8")
    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("10.5.6.7", 0))],
    ):
        validate_egress_host("wis2box", allowlist=al)


def test_parse_allowlist_rejects_garbage_token() -> None:
    with pytest.raises(AllowlistError):
        parse_allowlist("not a host!!!")


def test_validate_denies_empty_host() -> None:
    al = parse_allowlist("example.com")
    with pytest.raises(EgressDenied, match="empty host"):
        validate_egress_host("  ", allowlist=al)


def test_validate_allows_literal_ip_on_allowlist() -> None:
    al = parse_allowlist("203.0.113.10")
    validate_egress_host("203.0.113.10", allowlist=al)


def test_validate_denies_literal_ip_not_on_allowlist() -> None:
    al = parse_allowlist("203.0.113.10")
    with pytest.raises(EgressDenied, match="not on allowlist"):
        validate_egress_host("198.51.100.1", allowlist=al)


def test_validate_denies_blocked_metadata_hostname() -> None:
    al = parse_allowlist("metadata.google.internal")
    with pytest.raises(EgressDenied, match="metadata"):
        validate_egress_host("metadata.google.internal", allowlist=al)


def test_load_allowlist_from_env_parses_hosts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "a.example,10.0.0.0/8")
    al = load_allowlist_from_env()
    assert "a.example" in al.hostnames
    assert not al.is_empty


def test_validate_denies_when_dns_returns_no_addresses() -> None:
    al = parse_allowlist("empty.example.com")
    with (
        patch("dissemination.allowlist.socket.getaddrinfo", return_value=[]),
        pytest.raises(EgressDenied, match="did not resolve"),
    ):
        validate_egress_host("empty.example.com", allowlist=al)


def test_validate_denies_when_dns_raises_oserror() -> None:
    al = parse_allowlist("nx.example.com")
    with (
        patch(
            "dissemination.allowlist.socket.getaddrinfo",
            side_effect=OSError("name resolution failed"),
        ),
        pytest.raises(EgressDenied, match="did not resolve"),
    ):
        validate_egress_host("nx.example.com", allowlist=al)


def test_iter_allowlist_entries_and_default_env_load(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from dissemination.allowlist import iter_allowlist_entries

    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "z.example,10.1.0.0/16")
    al = load_allowlist_from_env()
    entries = list(iter_allowlist_entries(al))
    assert "z.example" in entries
    assert "10.1.0.0/16" in entries


def test_validate_uses_env_allowlist_when_none_passed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DISSEMINATION_EGRESS_ALLOWLIST", "only.example.com")
    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[(None, None, None, None, ("8.8.4.4", 0))],
    ):
        validate_egress_host("only.example.com")


def test_parse_allowlist_rejects_bad_hostname_labels() -> None:
    with pytest.raises(AllowlistError):
        parse_allowlist("-bad.example.com")
    with pytest.raises(AllowlistError):
        parse_allowlist("has space.com")
    with pytest.raises(AllowlistError):
        parse_allowlist("bad-.example.com")
    with pytest.raises(AllowlistError):
        parse_allowlist("a.." + ("x" * 64))
    with pytest.raises(AllowlistError):
        parse_allowlist("empty..label.example.com")


def test_validate_allows_ip_listed_as_hostname_entry() -> None:
    from dissemination.allowlist import Allowlist

    al = Allowlist(hostnames=frozenset({"8.8.8.8"}), networks=())
    validate_egress_host("8.8.8.8", allowlist=al)


def test_resolve_dedupes_duplicate_getaddrinfo_rows() -> None:
    al = parse_allowlist("dup.example.com")
    with patch(
        "dissemination.allowlist.socket.getaddrinfo",
        return_value=[
            (None, None, None, None, ("8.8.8.8", 0)),
            (None, None, None, None, ("8.8.8.8", 0)),
        ],
    ):
        validate_egress_host("dup.example.com", allowlist=al)
