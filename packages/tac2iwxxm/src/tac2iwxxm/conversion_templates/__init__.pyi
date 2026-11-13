"""Type stub for Auto-split package (exec chunks) — basedpyright."""
from typing import Any

__all__ = ['BridgePreview', 'ConversionTemplate', 'FIRST_PARTY_TEMPLATES', 'Slot', 'SlotMode', 'SlotType', '_WIND_RE', '_builtin_catalog', 'asdict', 'compile_pattern', 'dataclass', 'field', 'fork_first_party', 'get_first_party_template', 'list_first_party_templates', 'preview_bridge', 'reorder_slots', 'slot_from_dict', 'template_from_dict']

class BridgePreview:
    captures: Any
    compiled_pattern: Any
    focus_group: Any
    matched: Any
    skipped: Any
    template_id: Any
    xml_block: Any
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
class ConversionTemplate:
    access: Any
    comments: Any
    fork_of: Any
    id: Any
    iwxxm_block: Any
    name: Any
    profiles: Any
    sample: Any
    slots: Any
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
FIRST_PARTY_TEMPLATES: Any
class Slot:
    digits: Any
    enum_values: Any
    gloss: Any
    id: Any
    iwxxm_field: Any
    label: Any
    literal: Any
    mode: Any
    optional: Any
    type: Any
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
SlotMode = Any
SlotType = Any
_WIND_RE: Any
def _builtin_catalog(*args: Any, **kwargs: Any) -> Any: ...
def asdict(*args: Any, **kwargs: Any) -> Any: ...
def compile_pattern(*args: Any, **kwargs: Any) -> Any: ...
def dataclass(*args: Any, **kwargs: Any) -> Any: ...
def field(*args: Any, **kwargs: Any) -> Any: ...
def fork_first_party(*args: Any, **kwargs: Any) -> Any: ...
def get_first_party_template(*args: Any, **kwargs: Any) -> Any: ...
def list_first_party_templates(*args: Any, **kwargs: Any) -> Any: ...
def preview_bridge(*args: Any, **kwargs: Any) -> Any: ...
def reorder_slots(*args: Any, **kwargs: Any) -> Any: ...
def slot_from_dict(*args: Any, **kwargs: Any) -> Any: ...
def template_from_dict(*args: Any, **kwargs: Any) -> Any: ...
