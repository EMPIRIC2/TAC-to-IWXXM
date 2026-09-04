"""CA_ECCC operational exchange-output contract (EV-071 M2 / #1032 / #1040).

MSC datamart filename pattern, WMO AHL designators, distribution path template,
and profile-gated translation centre defaults. Constants mirror
``docs/domain/profiles/catalog.yaml`` ``CA_ECCC.exchange_output``.

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC]
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime

from tac2iwxxm.bulletin import bbb_to_report_status, iwxxm_filename
from tac2iwxxm.models import AhlParts

CA_ECCC_IWXXM_VERSION = "3.0.0"
CA_MSC_FILENAME_PATTERN = "A_{TTAAiiCCCCYYGGggBBB}_C_{CCC}_{YYYYMMddhhmmss}.xml"
CA_DISTRIBUTION_PATH_TEMPLATE = "https://dd.meteo.gc.ca/today/aviation/iwxxm/{product}/{issuer_code}/{HH}"

_WMO_HEADER_BY_PRODUCT: dict[str, str] = {
    "METAR": "A_LACN",
    "SPECI": "A_LPCN",
    "TAF": "A_LTCN",
    "AIRMET": "A_LWCN",
    "SIGMET": "A_LSCN",
    "VAA": "A_LUCN",
}

_SIGMET_KIND_DESIGNATOR: dict[str, str] = {
    "weather": "A_LSCN",
    "va": "A_LVCN",
    "tc": "A_LYCN",
}

_DATAMART_PRODUCT_SEGMENT: dict[str, str] = {
    "METAR": "metar",
    "SPECI": "speci",
    "TAF": "taf",
    "AIRMET": "airmet",
    "SIGMET": "sigmet",
    "VAA": "vaa",
}

_MSC_FILENAME_PARTS_RE = re.compile(
    r"^A_([A-Z]{2})([A-Z]{2})(\d{2})([A-Z]{4})(\d{6})(?:([A-Z0-9]{3}))?_C_([A-Z]{4})_(\d{14})\.xml$"
)

_MSC_FILENAME_RE = re.compile(r"^A_[A-Z]{2}[A-Z]{2}\d{2}[A-Z]{4}\d{6}(?:[A-Z0-9]{3})?_C_[A-Z]{4}_\d{14}\.xml$")


@dataclass(frozen=True, slots=True)
class ProfileOutputSpec:
    """Operator-visible exchange output fields for CA_ECCC convert."""

    semantic_profile: str
    file_naming_pattern: str
    wmo_header_designator: str
    distribution_path_template: str
    iwxxm_version_pin: str
    suggested_filename: str | None = None
    wmo_ahl_header: str | None = None
    distribution_path: str | None = None
    translation_centre_designator: str | None = None
    translation_centre_name: str | None = None


def _clean_env(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip()
    return value or default


def default_ca_translation_centre() -> tuple[str, str]:
    """
    Return configured translation centre designator and name for CA_ECCC.

    Returns
    -------
    tuple[str, str]
        ``(translationCentreDesignator, translationCentreName)`` from env or
        operator-neutral defaults (configurable per #1040).
    """
    designator = _clean_env("CA_ECCC_TRANSLATION_CENTRE_DESIGNATOR", "CWAO")
    name = _clean_env("CA_ECCC_TRANSLATION_CENTRE_NAME", "Environment and Climate Change Canada")
    return designator, name


def ca_wmo_header_designator(product: str, *, sigmet_kind: str | None = None) -> str:
    """Return MSC WMO AHL designator prefix for a product (e.g. ``A_LACN`` for METAR)."""
    key = product.strip().upper()
    if key == "SIGMET" and sigmet_kind:
        kind = sigmet_kind.strip().lower()
        if kind in _SIGMET_KIND_DESIGNATOR:
            return _SIGMET_KIND_DESIGNATOR[kind]
    try:
        return _WMO_HEADER_BY_PRODUCT[key]
    except KeyError as exc:
        raise ValueError(f"CA exchange output not defined for product {product!r}") from exc


def format_ca_wmo_ahl(parts: AhlParts, *, product: str, sigmet_kind: str | None = None) -> str:
    """
    Format a WMO AHL header line using MSC designator prefix.

    Parameters
    ----------
    parts :
        Parsed bulletin AHL parts (TAC ``T1T2`` on ``parts.tt``; filename uses ``iwxxm_tt``).
    product :
        API product enum (``METAR``, ``SPECI``, …).

    Returns
    -------
    str
        ``A_LACN31 CYUL 231800`` style header for layer-6 cross-check.
    """
    prefix = ca_wmo_header_designator(product, sigmet_kind=sigmet_kind)
    line = f"{prefix}{parts.ii} {parts.cccc} {parts.yygggg}"
    if parts.bbb:
        line = f"{line} {parts.bbb.strip().upper()}"
    return line


def issued_at_from_yygggg(yygggg: str, *, reference: datetime | None = None) -> datetime:
    """
    Build a UTC ``datetime`` from AHL ``YYGGgg`` using a reference year/month.

    Parameters
    ----------
    yygggg :
        Six-digit AHL time group ``YYGGgg``.
    reference :
        Reference instant for calendar year/month (defaults to now UTC).

    Returns
    -------
    datetime
        Aware UTC timestamp with day/hour/minute from ``yygggg``.
    """
    ref = reference or datetime.now(UTC)
    day = int(yygggg[:2])
    hh = int(yygggg[2:4])
    mm = int(yygggg[4:6])
    return ref.replace(day=day, hour=hh, minute=mm, second=0, microsecond=0, tzinfo=UTC)


def ca_msc_filename(
    parts: AhlParts,
    *,
    issued_at: datetime,
    gzip: bool = False,
) -> str:
    """
    Build MSC datamart IWXXM filename for CA_ECCC exchange output.

    Parameters
    ----------
    parts :
        Parsed AHL parts (``iwxxm_tt`` used in the ``TT`` segment).
    issued_at :
        Issue timestamp for the ``_C_CCCC_yyyyMMddhhmmss`` segment.
    gzip :
        When ``True``, append ``.gz`` (MSC distribution uses plain ``.xml`` by default).

    Returns
    -------
    str
        Filename matching ``CA_MSC_FILENAME_PATTERN``.
    """
    return iwxxm_filename(parts, issued_at=issued_at, gzip=gzip)


def ca_distribution_path(product: str, *, issuer_code: str, hour: int) -> str:
    """Expand MSC HTTPS distribution path for a product and issuer."""
    segment = _DATAMART_PRODUCT_SEGMENT.get(product.strip().upper())
    if segment is None:
        raise ValueError(f"CA distribution path not defined for product {product!r}")
    template = CA_DISTRIBUTION_PATH_TEMPLATE.format(product=segment, issuer_code=issuer_code, HH=f"{hour:02d}")
    return template


def msc_filename_matches_pattern(filename: str) -> bool:
    """Return whether ``filename`` matches the MSC IWXXM exchange pattern."""
    return bool(_MSC_FILENAME_RE.match(filename.strip()))


def parse_msc_exchange_filename(filename: str) -> tuple[AhlParts, datetime] | None:
    """
    Parse an MSC datamart filename into AHL parts and issue timestamp.

    Returns
    -------
    tuple[AhlParts, datetime] | None
        Parsed parts and UTC issue time, or ``None`` when the pattern does not match.
    """
    match = _MSC_FILENAME_PARTS_RE.match(filename.strip())
    if not match:
        return None
    tt, aa, ii, cccc, yygggg, bbb, _centre, issued_stamp = match.groups()
    iwxxm_tt = tt
    designator = f"A_{tt}{aa}"
    ahl = f"{designator}{ii} {cccc} {yygggg}"
    bbb_norm = bbb.upper() if bbb else None
    if bbb_norm:
        ahl = f"{ahl} {bbb_norm}"
        try:
            report_status = bbb_to_report_status(bbb_norm)
        except (KeyError, ValueError):
            report_status = "NORMAL"
    else:
        report_status = "NORMAL"
    parts = AhlParts(
        ahl=ahl,
        tt=tt,
        aa=aa,
        ii=ii,
        cccc=cccc,
        yygggg=yygggg,
        bbb=bbb_norm,
        iwxxm_tt=iwxxm_tt,
        report_status=report_status,
    )
    issued = datetime.strptime(issued_stamp, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
    return parts, issued


def build_ca_eccc_output_spec_from_msc_filename(
    *,
    product: str,
    source_filename: str,
    sigmet_kind: str | None = None,
    include_translation_centre: bool = True,
) -> ProfileOutputSpec | None:
    """
    Build output spec from an MSC datamart filename (ops corpus / validate-first path).

    Parameters
    ----------
    product :
        API product enum.
    source_filename :
        MSC filename such as ``A_LSCN22CWAO241540_C_CWAO_20260824154038.xml``.
    sigmet_kind :
        Optional SIGMET variant hint when product is ``SIGMET``.
    """
    parsed = parse_msc_exchange_filename(source_filename)
    if parsed is None:
        return None
    parts, issued = parsed
    return build_ca_eccc_output_spec(
        product=product,
        parts=parts,
        issued_at=issued,
        include_translation_centre=include_translation_centre,
        sigmet_kind=sigmet_kind,
    )


def build_ca_eccc_output_spec(
    *,
    product: str,
    parts: AhlParts | None = None,
    issued_at: datetime | None = None,
    include_translation_centre: bool = True,
    sigmet_kind: str | None = None,
) -> ProfileOutputSpec:
    """
    Build operator-visible output spec for CA_ECCC convert responses.

    Parameters
    ----------
    product :
        API product enum (``METAR``, ``SPECI``, ``TAF``, ``AIRMET``, ``SIGMET``, ``VAA``).
    parts :
        Optional parsed AHL parts for filename/header expansion.
    issued_at :
        Optional issue time for filename/path expansion.
    include_translation_centre :
        When ``True``, include configured translation centre ids (#1040).

    Returns
    -------
    ProfileOutputSpec
        Contract fields for API ``metadata.output_spec``.
    """
    product_u = product.strip().upper()
    designator = ca_wmo_header_designator(product_u, sigmet_kind=sigmet_kind)
    suggested: str | None = None
    wmo_ahl: str | None = None
    distribution: str | None = None
    if parts is not None:
        wmo_ahl = format_ca_wmo_ahl(parts, product=product_u, sigmet_kind=sigmet_kind)
        ts = issued_at or issued_at_from_yygggg(parts.yygggg)
        suggested = ca_msc_filename(parts, issued_at=ts)
        distribution = ca_distribution_path(product_u, issuer_code=parts.cccc, hour=ts.hour)
    centre_designator: str | None = None
    centre_name: str | None = None
    if include_translation_centre:
        centre_designator, centre_name = default_ca_translation_centre()
    return ProfileOutputSpec(
        semantic_profile="CA_ECCC",
        file_naming_pattern=CA_MSC_FILENAME_PATTERN,
        wmo_header_designator=designator,
        distribution_path_template=CA_DISTRIBUTION_PATH_TEMPLATE,
        iwxxm_version_pin=CA_ECCC_IWXXM_VERSION,
        suggested_filename=suggested,
        wmo_ahl_header=wmo_ahl,
        distribution_path=distribution,
        translation_centre_designator=centre_designator,
        translation_centre_name=centre_name,
    )


def profile_output_spec_to_dict(spec: ProfileOutputSpec) -> dict[str, str | None]:
    """Serialize ``ProfileOutputSpec`` for HTTP metadata (omit nulls)."""
    raw = {
        "semantic_profile": spec.semantic_profile,
        "file_naming_pattern": spec.file_naming_pattern,
        "wmo_header_designator": spec.wmo_header_designator,
        "distribution_path_template": spec.distribution_path_template,
        "iwxxm_version_pin": spec.iwxxm_version_pin,
        "suggested_filename": spec.suggested_filename,
        "wmo_ahl_header": spec.wmo_ahl_header,
        "distribution_path": spec.distribution_path,
        "translation_centre_designator": spec.translation_centre_designator,
        "translation_centre_name": spec.translation_centre_name,
    }
    return {key: value for key, value in raw.items() if value is not None}


__all__ = [
    "CA_DISTRIBUTION_PATH_TEMPLATE",
    "CA_ECCC_IWXXM_VERSION",
    "CA_MSC_FILENAME_PATTERN",
    "ProfileOutputSpec",
    "build_ca_eccc_output_spec",
    "build_ca_eccc_output_spec_from_msc_filename",
    "ca_distribution_path",
    "ca_msc_filename",
    "ca_wmo_header_designator",
    "default_ca_translation_centre",
    "format_ca_wmo_ahl",
    "issued_at_from_yygggg",
    "msc_filename_matches_pattern",
    "parse_msc_exchange_filename",
    "profile_output_spec_to_dict",
]
