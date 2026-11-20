"""sigmet_airmet package split."""

# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false
from __future__ import annotations

from tac_validate.product_rules_pkg.sigmet_airmet.airmet_checks import (
    _check_airmet_a1,
    _check_airmet_a2,
)
from tac_validate.product_rules_pkg.sigmet_airmet.common_sigmet import (
    _check_sigmet_g1,
    _check_sigmet_g2,
    _count_families,
    _sigmet_validity_hours,
)
from tac_validate.product_rules_pkg.sigmet_airmet.entry import (
    _check_sigmet_airmet,
)
from tac_validate.product_rules_pkg.sigmet_airmet.va_tc_us import (
    _CONVECTIVE_DVLPG,
    _CONVECTIVE_DVLPG_AREA_OK,
    _CONVECTIVE_SIGMET_BULLETIN,
    _CONVECTIVE_VALID_UNTIL,
    _SIGMET_AIRMET_CCCC_IDENTITY,
    _US_DOMESTIC_WS_SERIES,
    _US_DOMESTIC_WS_VALID_UNTIL,
    _WSUS_TTAAII,
    _check_convective_sigmet,
    _check_sigmet_tc,
    _check_sigmet_v1,
    _check_us_domestic_ws_sigmet,
    _is_us_domestic_ws_sigmet,
)

__all__ = [
    "_CONVECTIVE_DVLPG",
    "_CONVECTIVE_DVLPG_AREA_OK",
    "_CONVECTIVE_SIGMET_BULLETIN",
    "_CONVECTIVE_VALID_UNTIL",
    "_SIGMET_AIRMET_CCCC_IDENTITY",
    "_US_DOMESTIC_WS_SERIES",
    "_US_DOMESTIC_WS_VALID_UNTIL",
    "_WSUS_TTAAII",
    "_check_airmet_a1",
    "_check_airmet_a2",
    "_check_convective_sigmet",
    "_check_sigmet_airmet",
    "_check_sigmet_g1",
    "_check_sigmet_g2",
    "_check_sigmet_tc",
    "_check_sigmet_v1",
    "_check_us_domestic_ws_sigmet",
    "_count_families",
    "_is_us_domestic_ws_sigmet",
    "_sigmet_validity_hours",
]
