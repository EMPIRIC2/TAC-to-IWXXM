"""Public-bulletin profile check (TC-LIVE-PROFILE).

Offline callers inject bulletins and a check function. The live command is
``make test-live-profile``.

[Corpus: tests §TC-LIVE-PROFILE] [Corpus: product §F6] [Corpus: adr/ADR-036]
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import httpx
import yaml

_REPO = Path(__file__).resolve().parents[2]
_CATALOG = _REPO / "docs" / "domain" / "profiles" / "catalog.yaml"

HTTP_TIMEOUT_SECONDS = 30.0
DEFAULT_SUMMARY = Path("artifacts/live-profile/summary.json")
USER_AGENT = "TAC-to-IWXXM-live-feeds/1.0 github.com/EMPIRIC2/TAC-to-IWXXM"

AWC_METAR = "https://aviationweather.gov/api/data/metar"
AWC_TAF = "https://aviationweather.gov/api/data/taf"
AWC_ISIGMET = "https://aviationweather.gov/api/data/isigmet"
AWC_SIGMET = "https://aviationweather.gov/api/data/sigmet"
TGFTP_RAW = "https://tgftp.nws.noaa.gov/data/raw"
JMA_VAAC_INDEX = "https://ds.data.jma.go.jp/svd/vaac/data/"

_LISTING_ROW = re.compile(
    r'href="([^"/?][^"]*)"[^>]*>[^<]*</a></td><td[^>]*>\s*'
    r"(\d{2}-[A-Za-z]{3}-\d{4} \d{2}:\d{2})"
)
_JMA_TEXT = re.compile(r'href="(TextData/\d{4}/[^"]+_Text\.html)"')
_JMA_BODY = re.compile(
    r"<!-- VAA Text Start -->(.*?)<!-- VAA Text End -->",
    re.DOTALL,
)
_TAG = re.compile(r"<[^>]+>")
_BR = re.compile(r"<br\s*/?>", re.IGNORECASE)

# Feed id, product. One sample is required from each feed.
REQUIRED_FEEDS: tuple[tuple[str, str], ...] = (
    ("awc-metar", "METAR"),
    ("awc-taf", "TAF"),
    ("awc-sigmet-intl", "SIGMET"),
    ("awc-sigmet-convective", "SIGMET"),
    ("noaa-airmet", "AIRMET"),
    ("noaa-vaa", "VAA"),
    ("noaa-tca", "TCA"),
    ("noaa-vona", "VONA"),
    ("noaa-swx", "SWXA"),
    ("jma-vaac", "VAA"),
)


@dataclass(frozen=True)
class Bulletin:
    """One TAC report taken from a named feed."""

    feed: str
    product: str
    text: str


@dataclass(frozen=True)
class ProfileTarget:
    """An implemented semantic profile and the products it lists."""

    profile_id: str
    emit_key: str
    products: tuple[str, ...]


@dataclass(frozen=True)
class Finding:
    """One check result. Warnings do not fail the command."""

    check: str
    code: str
    message: str
    severity: str = "error"


Check = Callable[[Bulletin, ProfileTarget], list[Finding]]


def load_semantic_profiles(
    catalog_path: Path | None = None,
) -> tuple[ProfileTarget, ...]:
    """Return implemented semantic profiles from the profile catalog."""
    path = catalog_path or _CATALOG
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    profiles: list[ProfileTarget] = []
    for row in document.get("profiles") or []:
        if row.get("kind") != "semantic" or row.get("status") != "implemented":
            continue
        products = tuple(str(product) for product in row.get("products") or [])
        profiles.append(
            ProfileTarget(
                profile_id=str(row["id"]),
                emit_key=str(row.get("emit_key") or row["id"]),
                products=products,
            )
        )
    return tuple(profiles)


def _first_per_feed(bulletins: Sequence[Bulletin]) -> dict[str, Bulletin]:
    chosen: dict[str, Bulletin] = {}
    for bulletin in bulletins:
        chosen.setdefault(bulletin.feed, bulletin)
    return chosen


def _row(
    *,
    feed: str,
    product: str,
    profile_id: str,
    finding: Finding,
) -> dict[str, str]:
    return {
        "feed": feed,
        "product": product,
        "profile_id": profile_id,
        "check": finding.check,
        "code": finding.code,
        "message": finding.message,
        "severity": finding.severity,
    }


def run_check(
    bulletins: Sequence[Bulletin],
    *,
    profiles: Sequence[ProfileTarget],
    check: Check,
    summary_path: Path,
    required: Sequence[tuple[str, str]] = REQUIRED_FEEDS,
) -> int:
    """Run one bulletin per feed under each matching profile and write the summary.

    Returns 0 when every required feed is present and no error-severity finding
    was produced. ``SCHEMA_PARSE_ERROR`` is stored apart from document errors.
    """
    chosen = _first_per_feed(bulletins)
    schema_parse_errors: list[dict[str, str]] = []
    document_errors: list[dict[str, str]] = []
    failures: list[dict[str, str]] = []

    for feed, product in required:
        if feed not in chosen:
            failures.append(
                {
                    "feed": feed,
                    "product": product,
                    "profile_id": "",
                    "check": "fetch",
                    "code": "MISSING_FEED",
                    "message": f"{feed} did not provide a {product} report",
                    "severity": "error",
                }
            )

    for bulletin in chosen.values():
        for profile in profiles:
            if bulletin.product not in profile.products:
                continue
            for finding in check(bulletin, profile):
                row = _row(
                    feed=bulletin.feed,
                    product=bulletin.product,
                    profile_id=profile.profile_id,
                    finding=finding,
                )
                if finding.code == "SCHEMA_PARSE_ERROR":
                    schema_parse_errors.append(row)
                elif finding.code == "XSD_VALIDATION_ERROR":
                    document_errors.append(row)
                if finding.severity == "error":
                    failures.append(row)

    ok = not failures
    payload = {
        "ok": ok,
        "schema_parse_errors": schema_parse_errors,
        "document_errors": document_errors,
        "failures": failures,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    _print_summary(payload)
    return 0 if ok else 1


def _print_summary(payload: dict[str, object]) -> None:
    print(f"profile-check ok={str(payload['ok']).lower()}")
    schema_rows = payload["schema_parse_errors"]
    document_rows = payload["document_errors"]
    failure_rows = payload["failures"]
    if isinstance(schema_rows, list):
        for row in schema_rows:
            if isinstance(row, dict):
                print(f"schema-parse {row.get('code')} {row.get('message')}")
    if isinstance(document_rows, list):
        for row in document_rows:
            if isinstance(row, dict):
                print(f"document {row.get('code')} {row.get('message')}")
    if isinstance(failure_rows, list):
        for row in failure_rows:
            if not isinstance(row, dict):
                continue
            if row.get("code") in {"SCHEMA_PARSE_ERROR", "XSD_VALIDATION_ERROR"}:
                continue
            print(
                "failure"
                f" {row.get('code')} {row.get('feed')}"
                f" {row.get('profile_id')} {row.get('check')}"
            )


def indexed_files(listing_html: str) -> list[tuple[datetime, str]]:
    """Newest-first files from an Apache directory listing."""
    rows: list[tuple[datetime, str]] = []
    for name, stamp in _LISTING_ROW.findall(listing_html):
        rows.append((datetime.strptime(stamp, "%d-%b-%Y %H:%M"), name))
    rows.sort(reverse=True)
    return rows


def first_nonempty_line(body: str) -> str | None:
    """First non-blank line of a raw METAR or TAF feed."""
    for line in body.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return None


_VALID_PAIR = re.compile(r"\bVALID\s+(\d{6})/(\d{6})\b", re.IGNORECASE)
_WS_MAX_HOURS = 4.0
_WV_WC_MAX_HOURS = 6.0


def marked_reports(body: str, marker: str) -> list[str]:
    """Bulletin chunks that contain ``marker``.

    Aviation Weather Center international and convective SIGMET feeds prefix
    each bulletin with a ``Hazard:`` or ``Type:`` line.
    """
    chunks = re.split(r"(?m)^(?:Hazard:|Type:).*$", body)
    reports: list[str] = []
    for chunk in chunks:
        lines = [line.strip() for line in chunk.splitlines() if line.strip()]
        if not lines:
            continue
        text = "\n".join(lines)
        if marker in text:
            reports.append(text)
    return reports


def first_marked_report(body: str, marker: str) -> str | None:
    """First bulletin chunk that contains ``marker``."""
    reports = marked_reports(body, marker)
    return reports[0] if reports else None


def sigmet_validity_hours(start: str, end: str) -> float | None:
    """Hours from a ``ddhhmm/ddhhmm`` pair, or None when the tokens are invalid."""
    if len(start) != 6 or len(end) != 6 or not start.isdigit() or not end.isdigit():
        return None
    start_day, start_hour, start_minute = (
        int(start[:2]),
        int(start[2:4]),
        int(start[4:6]),
    )
    end_day, end_hour, end_minute = int(end[:2]), int(end[2:4]), int(end[4:6])
    if not (
        1 <= start_day <= 31
        and 1 <= end_day <= 31
        and start_hour < 24
        and end_hour < 24
        and start_minute < 60
        and end_minute < 60
    ):
        return None
    start_minutes = start_day * 24 * 60 + start_hour * 60 + start_minute
    end_minutes = end_day * 24 * 60 + end_hour * 60 + end_minute
    if end_minutes < start_minutes:
        end_minutes += 31 * 24 * 60
    return (end_minutes - start_minutes) / 60.0


def sigmet_within_annex3_validity(text: str) -> bool:
    """True when a VALID pair is absent or within 4 hours, or 6 for VA or TC."""
    match = _VALID_PAIR.search(text)
    if match is None:
        return True
    hours = sigmet_validity_hours(match.group(1), match.group(2))
    if hours is None:
        return True
    upper = text.upper()
    if re.search(r"\bVA\b", upper) or re.search(r"\bTC\b", upper):
        limit = _WV_WC_MAX_HOURS
    else:
        limit = _WS_MAX_HOURS
    return hours <= limit


def first_sigmet_within_validity(body: str) -> str | None:
    """First international SIGMET whose VALID window meets the Annex 3 maximum.

    A published bulletin can run longer than 4 hours (WS) or 6 hours (VA or TC).
    That bulletin is still a lint error. The sample is the next one that meets
    the limit. When every bulletin exceeds it, the first is returned.
    """
    reports = [
        text
        for text in marked_reports(body, "SIGMET")
        if "CONVECTIVE SIGMET" not in text
    ]
    if not reports:
        return None
    for text in reports:
        if sigmet_within_annex3_validity(text):
            return text
    return reports[0]


def body_has_line(body: str, line: str) -> bool:
    """True when ``line`` is a whole line, not a substring of another word."""
    return any(candidate.strip() == line for candidate in body.splitlines())


def complete_vona(body: str) -> bool:
    """True for a VONA that still has its issuing observatory line.

    TAC VONA uses WMO data designator ``WM``. Some US files under that
    directory stop after the colour-code lines, so they have no ``SVO:``.
    """
    if not body_has_line(body, "VONA"):
        return False
    return any(line.strip().upper().startswith("SVO:") for line in body.splitlines())


def latest_jma_text_href(index_html: str) -> str | None:
    """Latest Tokyo VAAC text page linked from the VAAC index."""
    hrefs = _JMA_TEXT.findall(index_html)
    if not hrefs:
        return None

    def sort_key(href: str) -> tuple[str, str]:
        name = href.rsplit("/", 1)[-1]
        parts = name.split("_")
        date = parts[0] if parts else ""
        clock = parts[2] if len(parts) > 2 else ""
        return (date, clock)

    return max(hrefs, key=sort_key)


def extract_jma_advisory(page_html: str) -> str | None:
    """TAC text from a Tokyo VAAC advisory HTML page."""
    match = _JMA_BODY.search(page_html)
    if match is None:
        return None
    text = _BR.sub("\n", match.group(1))
    text = _TAG.sub("", text)
    cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return cleaned or None


_LINT_ENGINES = frozenset({"annex3", "iwxxm_us", "ca_eccc", "in_imd"})
_SCHEMA_ENGINES = frozenset({"annex3", "iwxxm_us", "ca_eccc"})


def _iwxxm_version(profile: ProfileTarget) -> str:
    if profile.emit_key == "ca_eccc":
        return "3.0.0"
    return "2025-2"


def _lint_engine(profile: ProfileTarget, product: str) -> str:
    """Lint key the engine implements for this profile.

    National profiles that do not have their own lint module share Annex 3
    rules. ``in_imd`` is TAF-only.
    """
    if profile.emit_key == "in_imd" and product != "TAF":
        return "annex3"
    if profile.emit_key in _LINT_ENGINES:
        return profile.emit_key
    return "annex3"


def _schema_engine(emit_key: str) -> str:
    """Schema profile for XML produced under ``emit_key``."""
    if emit_key in _SCHEMA_ENGINES:
        return emit_key
    return "annex3"


def _findings_from_issues(check_name: str, issues: Sequence[object]) -> list[Finding]:
    findings: list[Finding] = []
    for issue in issues:
        severity = str(getattr(issue, "severity", "error"))
        if severity not in {"error", "warning"}:
            continue
        findings.append(
            Finding(
                check=check_name,
                code=str(getattr(issue, "code", "ERROR")),
                message=str(getattr(issue, "message", "")),
                severity=severity,
            )
        )
    return findings


def _unsupported_profile(converted: object) -> bool:
    issues = getattr(converted, "issues", ())
    return any(getattr(issue, "code", "") == "UNSUPPORTED_PROFILE" for issue in issues)


def engine_check(bulletin: Bulletin, profile: ProfileTarget) -> list[Finding]:
    """Lint, convert, schema-validate, and decode one bulletin under one profile.

    An exception becomes an error finding. Decode residuals do not fail the
    command. ``SCHEMA_PARSE_ERROR`` stays a schema finding so the summary can
    keep it apart from document errors.
    """
    from iwxxm_validate.api import validate
    from tac_decoding.decode import decode_tac
    from tac_validate.api import lint

    from tac2iwxxm import convert

    findings: list[Finding] = []
    version = _iwxxm_version(profile)
    lint_key = _lint_engine(profile, bulletin.product)
    try:
        linted = lint(bulletin.text, product=bulletin.product, profile=lint_key)
    except (ValueError, TypeError) as exc:
        if lint_key != "annex3" and "use annex3" in str(exc):
            linted = lint(bulletin.text, product=bulletin.product, profile="annex3")
            findings.extend(_findings_from_issues("lint", linted.issues))
        else:
            findings.append(Finding("lint", "LINT_ERROR", str(exc)))
    else:
        findings.extend(_findings_from_issues("lint", linted.issues))

    xml = ""
    convert_key = profile.emit_key
    try:
        converted = convert(
            bulletin.text,
            product=bulletin.product,
            profile=convert_key,
            iwxxm_version=version,
        )
    except (ValueError, TypeError) as exc:
        findings.append(Finding("convert", "CONVERT_ERROR", str(exc)))
        converted = None
    if (
        converted is not None
        and _unsupported_profile(converted)
        and convert_key != "annex3"
    ):
        convert_key = "annex3"
        version = "2025-2"
        try:
            converted = convert(
                bulletin.text,
                product=bulletin.product,
                profile=convert_key,
                iwxxm_version=version,
            )
        except (ValueError, TypeError) as exc:
            findings.append(Finding("convert", "CONVERT_ERROR", str(exc)))
            converted = None
    if converted is not None:
        findings.extend(_findings_from_issues("convert", converted.issues))
        xml = converted.xml or ""

    if xml:
        schema_key = _schema_engine(convert_key)
        schema_version = "3.0.0" if schema_key == "ca_eccc" else version
        try:
            validated = validate(
                xml,
                iwxxm_version=schema_version,
                profile=schema_key,
                product=bulletin.product,
            )
        except (ValueError, TypeError) as exc:
            findings.append(Finding("schema", "SCHEMA_ERROR", str(exc)))
        else:
            findings.extend(_findings_from_issues("schema", validated.issues))

    try:
        decode_tac(bulletin.text, product=bulletin.product)
    except (ValueError, TypeError) as exc:
        findings.append(Finding("decode", "DECODE_ERROR", str(exc)))
    return findings


def _get_text(
    client: httpx.Client, url: str, params: dict[str, str] | None = None
) -> str:
    response = client.get(url, params=params)
    response.raise_for_status()
    return response.text


def matching_names(
    entries: Sequence[tuple[datetime, str]],
    prefix: str,
) -> list[tuple[datetime, str]]:
    """Keep directory rows whose file name starts with ``prefix``."""
    needle = prefix.lower()
    return [row for row in entries if row[1].lower().startswith(needle)]


def _newest_match(
    client: httpx.Client,
    directory: str,
    predicate: Callable[[str], bool],
    *,
    limit: int = 8,
    name_prefix: str | None = None,
) -> str | None:
    listing = _get_text(client, directory)
    entries = indexed_files(listing)
    if name_prefix is not None:
        entries = matching_names(entries, name_prefix)
    for _stamp, name in entries[:limit]:
        body = _get_text(client, directory + name)
        if predicate(body):
            return body.strip()
    return None


def _optional(load: Callable[[], str | None]) -> str | None:
    """Return fetched text, or None when the request fails. No retry."""
    try:
        return load()
    except httpx.HTTPError:
        return None


def fetch_bulletins(client: httpx.Client) -> list[Bulletin]:
    """One report from each pinned feed. A failed fetch is omitted.

    ``run_check`` records an omitted required feed as ``MISSING_FEED``.
    Timeout is the client timeout. This function does not retry.
    """
    found: list[Bulletin] = []

    def take(feed: str, product: str, text: str | None) -> None:
        if text:
            found.append(Bulletin(feed=feed, product=product, text=text))

    take(
        "awc-metar",
        "METAR",
        _optional(
            lambda: first_nonempty_line(
                _get_text(
                    client, AWC_METAR, {"ids": "KDEN", "format": "raw", "hours": "6"}
                )
            )
        ),
    )
    take(
        "awc-taf",
        "TAF",
        _optional(
            lambda: first_nonempty_line(
                _get_text(client, AWC_TAF, {"ids": "KDEN", "format": "raw"})
            )
        ),
    )
    take(
        "awc-sigmet-intl",
        "SIGMET",
        _optional(
            lambda: first_sigmet_within_validity(
                _get_text(client, AWC_ISIGMET, {"format": "raw"})
            )
        ),
    )
    take(
        "awc-sigmet-convective",
        "SIGMET",
        _optional(
            lambda: first_marked_report(
                _get_text(client, AWC_SIGMET, {"format": "raw"}),
                "CONVECTIVE SIGMET",
            )
        ),
    )

    directory_feeds: tuple[
        tuple[str, str, str, Callable[[str], bool], str | None], ...
    ] = (
        (
            "noaa-airmet",
            "AIRMET",
            f"{TGFTP_RAW}/wa/",
            lambda body: "AIRMET" in body,
            None,
        ),
        (
            "noaa-vaa",
            "VAA",
            f"{TGFTP_RAW}/fv/",
            lambda body: "VA ADVISORY" in body and "USER MESSAGE" not in body,
            None,
        ),
        (
            "noaa-tca",
            "TCA",
            f"{TGFTP_RAW}/fk/",
            lambda body: "TC ADVISORY" in body,
            None,
        ),
        (
            "noaa-swx",
            "SWXA",
            f"{TGFTP_RAW}/fn/",
            lambda body: "SWX ADVISORY" in body,
            "fnxx",
        ),
    )
    for feed, product, directory, predicate, name_prefix in directory_feeds:
        take(
            feed,
            product,
            _optional(
                lambda directory=directory, predicate=predicate, name_prefix=name_prefix: (
                    _newest_match(client, directory, predicate, name_prefix=name_prefix)
                )
            ),
        )

    take(
        "noaa-vona",
        "VONA",
        _optional(
            lambda: _newest_match(
                client,
                f"{TGFTP_RAW}/wm/",
                complete_vona,
                limit=12,
            )
        ),
    )

    def _jma() -> str | None:
        index = _get_text(client, JMA_VAAC_INDEX)
        href = latest_jma_text_href(index)
        if href is None:
            return None
        return extract_jma_advisory(_get_text(client, JMA_VAAC_INDEX + href))

    take("jma-vaac", "VAA", _optional(_jma))
    return found


def main(argv: Sequence[str] | None = None) -> int:
    """Fetch the pinned feeds and write the pass/fail summary."""
    parser = argparse.ArgumentParser(description="Public-bulletin profile check")
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args(list(argv) if argv is not None else None)
    with httpx.Client(
        timeout=HTTP_TIMEOUT_SECONDS,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    ) as client:
        bulletins = fetch_bulletins(client)
    return run_check(
        bulletins,
        profiles=load_semantic_profiles(),
        check=engine_check,
        summary_path=args.summary,
    )


if __name__ == "__main__":
    raise SystemExit(main())
