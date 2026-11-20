"""Issue registry rows for WMO-No. 782 METAR/SPECI quality."""

from __future__ import annotations

from tac_validate.issue_registry.rows_wmo782_a import ISSUES_WMO782_A
from tac_validate.issue_registry.rows_wmo782_b import ISSUES_WMO782_B
from tac_validate.issue_registry.spec import IssueSpec

ISSUES_WMO782: tuple[IssueSpec, ...] = ISSUES_WMO782_A + ISSUES_WMO782_B
