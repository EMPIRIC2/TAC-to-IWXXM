"""Typing stub for exec-loaded split package (EV-tac2iwxxm-models-split)."""

from tac2iwxxm.models import ConvertResult as ConvertResult

class ConvertError(Exception):
    def __init__(self, *args: object, **kwargs: object) -> None: ...

def convert(
    tac: str,
    *,
    product: str = ...,
    profile: str | None = ...,
    iwxxm_version: str | None = ...,
    **kwargs: object,
) -> ConvertResult: ...
def resolve_propagate_residuals_to_remarks(
    *args: object,
    **kwargs: object,
) -> object: ...

__all__ = [
    "ConvertError",
    "ConvertResult",
    "convert",
    "resolve_propagate_residuals_to_remarks",
]
