"""Public ``convert()`` entrypoint (F6 products + F28 SWXA annex3 + iwxxm_us METAR/SPECI)."""

from __future__ import annotations

# Imports/constants consumed by exec'd part bodies.

import gzip

import os

import re

from collections.abc import Callable

from datetime import UTC, datetime

from typing import Any, cast

from xml.sax.saxutils import escape

from tac_decoding.match import MatchContext, match_tac

from tac_decoding.packs import load_packs

from tac2iwxxm.bulletin import BulletinSplitError, iwxxm_filename, parse_ahl

from tac2iwxxm.convert_allowlist import products_for

from tac2iwxxm.decode import decode_tac

from tac2iwxxm.emit_map import emit_with_map

from tac2iwxxm.exchange_output import default_ca_translation_centre

from tac2iwxxm.geometry.reference_point import UnknownVOR

from tac2iwxxm.ir_source import IR_SOURCE_ENV, resolve_ir_source

from tac2iwxxm.models import (
    AhlParts,
    ConvertIr,
    ConvertIssue,
    ConvertResult,
    PropagateResidualsConfig,
)

from tac2iwxxm.pack_ir_map import PackIrMapError, map_spans_to_convert_ir, pack_id_for_product

from tac2iwxxm.profile_registry import (
    EMIT_ANNEX3,
    EMIT_CA_ECCC,
    EMIT_CA_MSC_SIGMET,
    EMIT_IWXXM_US,
    EMIT_US_NWS_CONVECTIVE_SIGMET,
    resolve_semantic_profile,
    supported_iwxxm_versions_for_profile,
    supported_report_variants_for_profile,
)

from tac2iwxxm.profiles.annex3 import obs_timestamp

from tac2iwxxm.profiles.annex3_emit import (
    emit_swxa_annex3,
    emit_vona_annex3,
)

from tac2iwxxm.profiles.ca_eccc import CA_IWXXM_VERSION

from tac2iwxxm.slot_builders.metar_speci import fold_observation_case, parse_metar_speci

from tac2iwxxm.slot_builders.sigmet_airmet import parse_airmet, parse_sigmet

from tac2iwxxm.slot_builders.swxa import parse_swxa

from tac2iwxxm.slot_builders.taf import parse_taf

from tac2iwxxm.slot_builders.vaa_tca import parse_tca, parse_vaa

from tac2iwxxm.slot_builders.vona import parse_vona

from tac2iwxxm.taf_time_links import failed_preview_nil_element

from tac2iwxxm.time_anchor import (
    ImpossibleTacDay,
    anchor_from_bulletin_date,
    pop_bulletin_anchor,
    push_bulletin_anchor,
)

_SUPPORTED_PRODUCTS = frozenset({"METAR", "SPECI", "TAF", "SIGMET", "AIRMET", "VAA", "TCA", "SWXA", "VONA"})

_SOURCE_UNAVAILABLE = {
    "us_nws_g_airmet": ("United States G-AIRMET conversion is unavailable until a text bulletin is on file."),
    "us_nws_vona": (
        "United States volcano observatory notice conversion is unavailable until a complete notice is on file."
    ),
    "ca_msc_sigmet": ("Canadian SIGMET text conversion is unavailable until a text source is on file."),
}

_REPORT_STATUSES = frozenset({"NORMAL", "AMENDMENT", "CORRECTION"})

_REMARK_SPAN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("malformed AO", re.compile(r"\bAO(?![12]\b)\w*\b")),
    ("malformed SLP", re.compile(r"\bSLP(?!\d{3}\b)\w*\b")),
    ("malformed PK WND", re.compile(r"\bPK\s+WND\b")),
)

_RMK_TOKEN = re.compile(r"\bRMK\b")

_PREVIEW_ROOTS = frozenset({"METAR", "SPECI", "TAF", "SIGMET", "AIRMET", "VAA", "TCA", "SWXA", "VONA"})

_PREVIEW_NS = {
    "2025-2": "http://icao.int/iwxxm/2025-2",
    "2023-1": "http://icao.int/iwxxm/2023-1",
}

_UNRELIABLE_TAC = re.compile(r"\bINVALID\b", re.IGNORECASE)

_PRODUCT_LEAD = {
    "METAR": re.compile(r"^\s*METAR\b", re.IGNORECASE),
    "SPECI": re.compile(r"^\s*SPECI\b", re.IGNORECASE),
    "TAF": re.compile(r"^\s*TAF\b", re.IGNORECASE),
    "SIGMET": re.compile(r"^\s*(?:[A-Z]{4}\s+)?SIGMET\b", re.IGNORECASE | re.MULTILINE),
    "AIRMET": re.compile(r"^\s*(?:[A-Z]{4}\s+)?AIRMET\b", re.IGNORECASE | re.MULTILINE),
    "VAA": re.compile(r"VA\s+ADVISORY\b", re.IGNORECASE),
    "TCA": re.compile(r"TC\s+ADVISORY\b", re.IGNORECASE),
    "SWXA": re.compile(r"SWX\s+ADVISORY\b", re.IGNORECASE),
    "VONA": re.compile(r"(?m)^\s*VONA\b", re.IGNORECASE),
}

_QUARANTINE_ROOT = {
    "METAR": "METAR",
    "SPECI": "SPECI",
    "TAF": "TAF",
    "SIGMET": "SIGMET",
    "AIRMET": "AIRMET",
    "VAA": "VolcanicAshAdvisory",
    "TCA": "TropicalCycloneAdvisory",
    "SWXA": "SpaceWeatherAdvisory",
    "VONA": "VolcanoObservatoryNoticeForAviation",
}

_STATION_AFTER_PRODUCT = re.compile(
    r"^\s*(?:METAR|SPECI|TAF)\s+(?:COR\s+)?(?P<station>[A-Z][A-Z0-9]{3})\b",
    re.IGNORECASE,
)

_REMARKS_HRT_EMIT_PROFILES = frozenset({EMIT_IWXXM_US, EMIT_CA_ECCC})

_PROPAGATE_RESIDUALS_DEFAULTS: PropagateResidualsConfig = {
    EMIT_ANNEX3: False,
    "icao_2025": False,
}

_STATUS_TEST = re.compile(r"(?im)^\s*STATUS:\s*TEST\s*$")

_THIS_IS_A_TEST = re.compile(r"THIS IS A TEST", re.IGNORECASE)

_EXERCISE_WORD = re.compile(r"\bEXERCISE\b", re.IGNORECASE)

_RMK_LINE = re.compile(r"RMK\s*:\s*(.*)$", re.IGNORECASE)

_NEXT_FIELD = re.compile(r"^[A-Z0-9 /+]{2,}:")

_NIL_MISSING = "http://codes.wmo.int/common/nil/missing"

_VALID_6 = re.compile(r"\b(\d{2})(\d{2})(\d{2})/(\d{2})(\d{2})(\d{2})\b")

_VALID_4 = re.compile(r"\b(\d{2})(\d{2})/(\d{2})(\d{2})\b")

_ATS_UNIT = re.compile(r"\b([A-Z]{4})\s+(?:SIGMET|AIRMET)\b")

_ADVISORY_CENTRE = {
    "VAAC": re.compile(r"^VAAC:\s*(\S+)", re.MULTILINE),
    "TCAC": re.compile(r"^TCAC:\s*(\S+)", re.MULTILINE),
    "SWXC": re.compile(r"^SWXC:\s*(\S+)", re.MULTILINE),
}

_ROOT_OPEN = re.compile(r"(<(?:iwxxm|iwxxm-ca):[A-Za-z]+\b)([^>]*)(>)", re.DOTALL)
