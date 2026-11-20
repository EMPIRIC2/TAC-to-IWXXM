"""Typing stub for exec-loaded split package (EV-tac2iwxxm-models-split)."""

from typing import Any

from tac2iwxxm.models.conversion_template import (
    BridgeCapture as BridgeCapture,
)
from tac2iwxxm.models.conversion_template import (
    BridgePreview as BridgePreview,
)
from tac2iwxxm.models.conversion_template import (
    BridgeSkipped as BridgeSkipped,
)
from tac2iwxxm.models.conversion_template import (
    ConversionTemplate as ConversionTemplate,
)
from tac2iwxxm.models.conversion_template import (
    Slot as Slot,
)

FIRST_PARTY_TEMPLATES: dict[str, ConversionTemplate]

compile_pattern: Any
fork_first_party: Any
get_first_party_template: Any
list_first_party_templates: Any

def preview_bridge(
    template: ConversionTemplate,
    *,
    focus_group: str | None = None,
) -> BridgePreview: ...
def reorder_slots(
    template: ConversionTemplate,
    ordered_ids: list[str],
) -> ConversionTemplate: ...
def slot_from_dict(raw: dict[str, Any]) -> Slot: ...
def template_from_dict(raw: dict[str, Any]) -> ConversionTemplate: ...

__all__ = [
    "FIRST_PARTY_TEMPLATES",
    "BridgeCapture",
    "BridgePreview",
    "BridgeSkipped",
    "ConversionTemplate",
    "Slot",
    "compile_pattern",
    "fork_first_party",
    "get_first_party_template",
    "list_first_party_templates",
    "preview_bridge",
    "reorder_slots",
    "slot_from_dict",
    "template_from_dict",
]
