"""Typing stub for tac2iwxxm public package API (EV-tac2iwxxm-models-split)."""

from tac_decoding.decode import DecodeResidual as DecodeResidual
from tac_decoding.decode import DecodeResult as DecodeResult
from tac_decoding.decode import DecodeSegment as DecodeSegment

from tac2iwxxm.bulletin import BulletinSplitError as BulletinSplitError
from tac2iwxxm.models import AhlParts as AhlParts
from tac2iwxxm.models import BulletinMeta as BulletinMeta
from tac2iwxxm.models import BulletinSplit as BulletinSplit
from tac2iwxxm.models import ConvertIssue as ConvertIssue
from tac2iwxxm.models import ConvertResult as ConvertResult

__version__: str

class ConvertError(Exception):
    def __init__(self, *args: object, **kwargs: object) -> None: ...

def bbb_to_report_status(bbb: str | None) -> object: ...
def convert(tac: str, **kwargs: object) -> ConvertResult: ...
def decode_tac(tac: str, **kwargs: object) -> DecodeResult: ...
def format_ahl(*args: object, **kwargs: object) -> str: ...
def iwxxm_filename(*args: object, **kwargs: object) -> str: ...
def map_t1t2(*args: object, **kwargs: object) -> object: ...
def parse_ahl(*args: object, **kwargs: object) -> AhlParts: ...
def rust_available() -> bool: ...
def rust_module() -> object: ...
def scan_metar_tokens(*args: object, **kwargs: object) -> object: ...
def split_bulletin(text: str, *, product: str = ...) -> BulletinSplit: ...

__all__ = [
    "AhlParts",
    "BulletinMeta",
    "BulletinSplit",
    "BulletinSplitError",
    "ConvertError",
    "ConvertIssue",
    "ConvertResult",
    "DecodeResidual",
    "DecodeResult",
    "DecodeSegment",
    "__version__",
    "bbb_to_report_status",
    "convert",
    "decode_tac",
    "format_ahl",
    "iwxxm_filename",
    "map_t1t2",
    "parse_ahl",
    "rust_available",
    "rust_module",
    "scan_metar_tokens",
    "split_bulletin",
]
