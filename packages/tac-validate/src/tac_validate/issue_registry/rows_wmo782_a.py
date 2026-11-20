"""Issue registry rows for WMO-No. 782 METAR/SPECI quality (part A)."""

# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from tac_validate.issue_registry.spec import IssueSpec, _row

ISSUES_WMO782_A: tuple[IssueSpec, ...] = (
    _row(
        "AUTO_MISPLACED",
        "error",
        "{product} places AUTO outside the accepted identification slot after the code name and date/time group, or combines AUTO with NIL.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "modifier",
        ),
    ),
    _row(
        "AUTO_VISIBILITY_NOT_OBSERVABLE",
        "warning",
        "{product} AUTO report encodes visibility as //// (temporarily missing or incorrect). In AUTO reports, prevailing visibility is the best practicable runway and touchdown indication.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "visibility",
        ),
    ),
    _row(
        "CAVOK_CONDITIONS_NOT_MET",
        "warning",
        "{product} includes CAVOK but visibility, cloud of operational significance, or significant weather does not meet all CAVOK conditions at once.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "visibility",
        ),
    ),
    _row(
        "CAVOK_EXCLUDES_RVR",
        "error",
        "{product} CAVOK present with RVR groups",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "rvr",
        ),
    ),
    _row(
        "CAVOK_NSC_BOUNDARY",
        "warning",
        "{product} uses 9999 with NSC or NCD when CAVOK would replace visibility, weather, and cloud; or uses NSC when CAVOK conditions are met.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "visibility",
        ),
    ),
    _row(
        "CLOUD_COMMON_BASE_CB_TCU",
        "warning",
        "{product} should merge CB and TCU that share a common base into one cloud group when required.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "cloud",
        ),
    ),
    _row(
        "CLOUD_HEIGHT_NOT_ASCENDING",
        "warning",
        "{product} cloud layer heights are not in ascending order.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "cloud",
        ),
    ),
    _row(
        "CLOUD_LAYER_COUNT_EXCEEDED",
        "warning",
        "{product} reports more than three cloud groups without a CB/TCU fourth-layer exemption.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "cloud",
        ),
    ),
    _row(
        "CLOUD_TYPE_SUFFIX_ONLY_CB_TCU",
        "error",
        "{product} Cloud type suffix outside CB TCU or AUTO ///",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "cloud",
        ),
    ),
    _row(
        "COR_MISPLACED",
        "error",
        "{product} places COR outside the accepted identification slot after the code name (and before CCCC / YYGGggZ as required).",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "modifier",
        ),
    ),
    _row(
        "DIRECTIONAL_VISIBILITY_FORMAT",
        "warning",
        "{product} directional minimum visibility {token!r} should be four digits plus a direction (for example 1400SW) when minimum visibility differs from prevailing and is under 1 500 m or under 50 percent of prevailing.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "visibility",
        ),
    ),
    _row(
        "FIRST_GROUPS_FORMAT",
        "warning",
        "{product} identification groups do not match an accepted METAR/SPECI ± COR/AUTO/NIL and CCCC YYGGggZ shape.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "order",
        ),
    ),
    _row(
        "MISSING_MANDATORY_DIGIT_AS_SOLIDUS",
        "warning",
        "{product} uses solidus (/) for a temporarily missing or incorrect mandatory digit. For non-AUTO reports this is a warning until the element is restored.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "parse",
        ),
    ),
    _row(
        "NATIONAL_RMK_NOT_INTERNATIONAL",
        "info",
        "{product} includes a national RMK section that should not be disseminated internationally; conversion may omit national remarks when requested.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "remarks",
        ),
    ),
    _row(
        "NCD_REQUIRES_AUTO",
        "error",
        "{product} NCD without AUTO",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "modifier",
        ),
    ),
    _row(
        "NDV_REQUIRES_AUTO",
        "error",
        "{product} NDV directional-visibility marker without AUTO",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "modifier",
        ),
    ),
    _row(
        "NIL_AUTO_CONFLICT",
        "error",
        "{product} includes both NIL and AUTO; a missing report cannot be a fully automated observation.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "modifier",
        ),
    ),
    _row(
        "NIL_MISPLACED",
        "error",
        "{product} places NIL outside the accepted identification slot, or combines NIL with AUTO or meteorological body groups incorrectly.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "nil",
        ),
    ),
    _row(
        "PRECIP_INTENSITY_VIS_PLAUSIBILITY",
        "warning",
        "{product} Precipitation intensity inconsistent with visibility band in handbook table",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "visibility",
        ),
    ),
    _row(
        "QNH_MISSING_AS_SOLIDUS",
        "warning",
        "{product} encodes missing QNH as Q//// when pressure is temporarily missing or incorrect.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "pressure",
        ),
    ),
    _row(
        "QNH_PREFIX_UNIT_MISMATCH",
        "error",
        "{product} Q with inHg-like digits or A with hPa-like digits",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "pressure",
        ),
    ),
    _row(
        "RECENT_WEATHER_LIMITS",
        "warning",
        "{product} recent weather REw'w' does not meet accepted Code table 4678 recent-weather limits.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "weather",
        ),
    ),
    _row(
        "RECENT_WEATHER_NO_INTENSITY",
        "error",
        "{product} REw'w' includes - + or VC",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "weather",
        ),
    ),
    _row(
        "REUP_REQUIRES_AUTO",
        "warning",
        "{product} includes REUP without AUTO; unknown precipitation recent weather is an automated-system form.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "modifier",
        ),
    ),
    _row(
        "RVR_MAX_GROUPS",
        "warning",
        "{product} includes more than four RVR groups; at most four alphanumeric RVR groups are accepted.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "rvr",
        ),
    ),
    _row(
        "RVR_MISSING_AS_SOLIDUS",
        "warning",
        "{product} encodes missing RVR digits with solidi (for example R24/////) when RVR is temporarily missing or incorrect.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "rvr",
        ),
    ),
    _row(
        "RVR_SCALE_STEP",
        "warning",
        "{product} RVR value does not follow the accepted reporting steps, including P2000 / M lower-bound forms.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "rvr",
        ),
    ),
    _row(
        "RVR_TENDENCY_FORMAT",
        "warning",
        "{product} RVR tendency must be U, D, or N when a tendency is reported.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "rvr",
        ),
    ),
    _row(
        "SEA_SURFACE_GROUP_FORMAT",
        "error",
        "{product} WTsTs paired incorrectly with S' vs HHsHsHs",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "sea",
        ),
    ),
)
