"""Type stub for Auto-split package (exec chunks) — basedpyright."""
from typing import Any
from tac2iwxxm.models import AhlParts as AhlParts
from tac2iwxxm.models import BulletinMeta as BulletinMeta
from tac2iwxxm.models import BulletinSplit as BulletinSplit
from datetime import datetime as datetime

__all__ = ['AhlParts', 'BulletinMeta', 'BulletinSplit', 'BulletinSplitError', 'ReportStatus', 'UTC', '_AHL_LINE', '_BBB_VALID', '_GLUED_SIGMET_AHL', '_PRODUCT_BODY_RE', '_PRODUCT_TT', '_SIGMET_BODY_STOP', '_TAC_AIRMET', '_TAC_CONVECTIVE_SIGMET', '_TAC_METAR_SPECI', '_TAC_SEQUENCE', '_TAC_SIGMET', '_TAC_SWXA', '_TAC_TAF', '_TAC_TCA', '_TAC_TO_IWXXM', '_TAC_VAA', '_TAC_VONA', '_find_sigmet_reports', '_is_kept_sigmet_report', '_span_overlaps_prior', '_unglue_sigmet_ahl', 'bbb_to_report_status', 'datetime', 'format_ahl', 'iwxxm_filename', 'map_t1t2', 'parse_ahl', 'split_bulletin']

class BulletinSplitError(Exception):
    args: Any
    code: Any
    message: Any
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
def ReportStatus(*args: Any, **kwargs: Any) -> Any: ...
UTC: Any
_AHL_LINE: Any
_BBB_VALID: Any
_GLUED_SIGMET_AHL: Any
_PRODUCT_BODY_RE: Any
_PRODUCT_TT: Any
_SIGMET_BODY_STOP: Any
_TAC_AIRMET: Any
_TAC_CONVECTIVE_SIGMET: Any
_TAC_METAR_SPECI: Any
_TAC_SEQUENCE: Any
_TAC_SIGMET: Any
_TAC_SWXA: Any
_TAC_TAF: Any
_TAC_TCA: Any
_TAC_TO_IWXXM: Any
_TAC_VAA: Any
_TAC_VONA: Any
def _find_sigmet_reports(*args: Any, **kwargs: Any) -> Any: ...
def _is_kept_sigmet_report(*args: Any, **kwargs: Any) -> Any: ...
def _span_overlaps_prior(*args: Any, **kwargs: Any) -> Any: ...
def _unglue_sigmet_ahl(*args: Any, **kwargs: Any) -> Any: ...
def bbb_to_report_status(*args: Any, **kwargs: Any) -> Any: ...
def format_ahl(*args: Any, **kwargs: Any) -> Any: ...
def iwxxm_filename(*args: Any, **kwargs: Any) -> Any: ...
def map_t1t2(*args: Any, **kwargs: Any) -> Any: ...
def parse_ahl(*args: Any, **kwargs: Any) -> Any: ...
def split_bulletin(*args: Any, **kwargs: Any) -> Any: ...
