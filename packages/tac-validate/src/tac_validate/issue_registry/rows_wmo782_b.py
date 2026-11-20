"""Issue registry rows for WMO-No. 782 METAR/SPECI quality (part B)."""

# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from tac_validate.issue_registry.spec import IssueSpec, _row

ISSUES_WMO782_B: tuple[IssueSpec, ...] = (
    _row(
        "TEMP_DEWPOINT_INVERSION",
        "warning",
        "{product} dew-point temperature is higher than air temperature (Td must be less than or equal to T).",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "temperature",
        ),
    ),
    _row(
        "TREND_CLOUD_LAYERS_INCOMPLETE",
        "warning",
        "{product} TREND that changes cloud must repeat all cloud layers, not only the changed layer.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "cloud",
        ),
    ),
    _row(
        "TREND_FM_FORMAT",
        "error",
        "{product} TREND FM time must be four-digit FMGGgg, not TAF FMYYGGgg.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "trend",
        ),
    ),
    _row(
        "TREND_NCD_OR_SOLIDUS_FORBIDDEN",
        "error",
        "{product} TREND must not use NCD or cloud solidus forms reserved for the observation body / AUTO.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "trend",
        ),
    ),
    _row(
        "TREND_NOSIG_EXCLUSIVITY",
        "error",
        "{product} NOSIG with BECMG TEMPO or trend elements",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "trend",
        ),
    ),
    _row(
        "TREND_NSW_ONLY_IN_CHANGE",
        "error",
        "{product} NSW is only allowed inside TREND change groups, not in the base observation body.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "trend",
        ),
    ),
    _row(
        "TREND_PROB_FORBIDDEN",
        "error",
        "{product} TREND forecast must not use PROB; PROB belongs to TAF change groups.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "trend",
        ),
    ),
    _row(
        "TREND_UNIT_MISMATCH",
        "error",
        "{product} TREND wind or visibility units must match the parent METAR/SPECI body.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "trend",
        ),
    ),
    _row(
        "TREND_WIND_V_GROUP_FORBIDDEN",
        "error",
        "{product} TREND wind must not include a directional variation V-group.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "wind",
        ),
    ),
    _row(
        "VISIBILITY_MISSING_AS_SOLIDUS",
        "warning",
        "{product} encodes missing or temporarily incorrect visibility as //// (or ////SM); non-AUTO use is a solidus warning; AUTO use is expected sensor-unavailable.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "visibility",
        ),
    ),
    _row(
        "VISIBILITY_SCALE_STEP",
        "warning",
        "{product} visibility value {token!r} does not follow the reporting scale (50 m below 800 m; 100 m from 800 m to under 5 km; 1 000 m from 5 km to under 10 km; 10 km when 10 km or more).",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "visibility",
        ),
    ),
    _row(
        "VV_EXCLUDES_CLOUD_LAYERS",
        "error",
        "{product} VV group mixed with cloud layers NSC NCD or CAVOK",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "cloud",
        ),
    ),
    _row(
        "WEATHER_AUTO_UP_OR_SH",
        "warning",
        "{product} AUTO present-weather uses UP or SH forms that require automated-system rules.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "weather",
        ),
    ),
    _row(
        "WEATHER_BR_VIS_BAND",
        "warning",
        "{product} BR outside 1000-5000 m band",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "visibility",
        ),
    ),
    _row(
        "WEATHER_DESCRIPTOR_PAIRING",
        "error",
        "{product} MI/BC/PR not paired with FG only, or DR/BL not with DU/SA/SN",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "weather",
        ),
    ),
    _row(
        "WEATHER_FG_VIS_THRESHOLD",
        "warning",
        "{product} FG with prevailing visibility at or above 1000 m",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "visibility",
        ),
    ),
    _row(
        "WEATHER_FZ_REQUIRES_SUBZERO",
        "warning",
        "{product} FZFG/FZDZ/FZRA without sub-zero temperature evidence",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "weather",
        ),
    ),
    _row(
        "WEATHER_SHPL_FORBIDDEN",
        "error",
        "{product} includes SHPL, which is not an accepted present-weather combination.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "weather",
        ),
    ),
    _row(
        "WEATHER_SQ_MIN_SPEED",
        "warning",
        "{product} SQ with mean wind under 22 kt",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "weather",
        ),
    ),
    _row(
        "WEATHER_VC_COMBINATION",
        "error",
        "{product} VC with intensity or with a phenomenon not allowed in vicinity",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "weather",
        ),
    ),
    _row(
        "WEATHER_VIS_OBSCURATION_THRESHOLD",
        "warning",
        "{product} visibility below 5 000 m should include an obscuration or weather cause; encoded 5000 without FU/HZ/DU/SA/BR can be valid when observed visibility was 5 001-5 999 m.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "visibility",
        ),
    ),
    _row(
        "WIND_CALM_MISENCODE",
        "error",
        "{product} calm wind must be 00000KT or 00000MPS; directed calm, calm with gust, or calm with a V-group is not allowed.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "wind",
        ),
    ),
    _row(
        "WIND_GUST_BELOW_THRESHOLD",
        "warning",
        "{product} gust is reported when the maximum does not exceed the mean by at least 10 kt (5 m/s).",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "wind",
        ),
    ),
    _row(
        "WIND_HIGH_SPEED_P_INDICATOR",
        "error",
        "{product} speeds at or above 100 kt (50 m/s) must use P99KT or P49MPS; wrong P-threshold or unit is not allowed.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "wind",
        ),
    ),
    _row(
        "WIND_PHYSICAL_RANGE",
        "warning",
        "{product} wind speed or gust spread is outside the usual physical range for this product (for example hurricane-force mean wind in METAR, or gust far above the mean).",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "wind",
        ),
    ),
    _row(
        "WIND_SHEAR_FORMAT",
        "warning",
        "{product} wind shear group should be WS RDRDR or WS ALL RWY.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "wind",
        ),
    ),
    _row(
        "WIND_VARIATION_SPAN",
        "error",
        "{product} directional variation group dndndnVdxdxdx requires mean speed at least 3 kt and a direction span of 60 degrees to less than 180 degrees.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "wind",
        ),
    ),
    _row(
        "WIND_VRB_MISUSE",
        "error",
        "{product} uses VRB with a directed wind-variation group. VRB is only for light variable wind under 3 kt (1.5 m/s), or for variation of 180° or more when a single direction cannot be given.",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "wind",
        ),
    ),
    _row(
        "WS_ALL_RWY_EXCLUSIVE",
        "error",
        "{product} WS ALL RWY with individual WS runway groups",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "wind",
        ),
    ),
    _row(
        "WX_COLUMN_SEQUENCE",
        "error",
        "{product} w'w' violates intensity-descriptor-phenomenon column order",
        tags=(
            "metar",
            "speci",
            "wmo782",
            "weather",
        ),
    ),
)
