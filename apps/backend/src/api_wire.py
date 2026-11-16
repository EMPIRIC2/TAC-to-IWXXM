"""Facade for ``api_wire.py`` (line-cap split)."""

import sys
import types

from . import api_wire_part_2 as _part2
from .api_wire_part_1 import (
    _AHL_HEADING_SPLIT_CODES,
    _API_PRODUCTS,
    _BULLETIN_ID_RE,
    _CCCC_RE,
    _EMPTY_BULLETIN_MESSAGE,
    _INVALID_AHL_MESSAGE,
    _MULTILINE_TEMPLATE_PRODUCTS,
    MAX_BULLETIN_REPORTS,
    _coerce_form_list,
    _coerce_form_str,
    _is_multiline_template_product,
    _is_named_upload,
    _iwxxm_validate_fn,
    _package_issue_payload,
    _package_stages_payload,
    _resolve_request_extensions,
    add_loopback_origin_variants,
    add_origin_if_missing,
    get_cors_allowed_headers,
    get_cors_origins,
    is_dev_cors_relaxation_enabled,
    logger,
    normalize_api_product,
    parse_files,
)
from .api_wire_part_2 import (
    _call_iwxxm_validate,
    _product_uses_metar_tac_layers,
    _resolve_request_profiles,
    classify_and_validate_upload_content,
    is_xml_input,
    manual_entries_with_offsets,
    normalize_code,
    normalize_validation_level,
    read_upload_files_text,
    read_uploaded_text,
    split_manual_entries,
)
from .api_wire_part_3 import (
    _product_uses_aerodrome_icao_layer,
    bulletin_split_http_error,
    parse_optional_bulletin_id,
    parse_optional_files,
    parse_optional_issuing_center,
)

_SYNC = {"read_uploaded_text", "read_upload_files_text", "_call_iwxxm_validate"}


_ORIG: dict[str, object] = {}
for _n in _SYNC:
    for _mod in (_part2,):
        if hasattr(_mod, _n):
            _ORIG.setdefault(_n, getattr(_mod, _n))


class _ApiWireModule(types.ModuleType):
    """Sync facade attribute patches into split part modules."""

    def __setattr__(self, name: str, value: object) -> None:
        """
        Internal helper ``__setattr__``.

        Parameters
        ----------
        name : object
            Argument ``name``.
        value : object
            Argument ``value``.
        """
        if name in _SYNC and hasattr(_part2, name):
            setattr(_part2, name, value)
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        """
        Internal helper ``__delattr__``.

        Parameters
        ----------
        name : object
            Argument ``name``.
        """
        if name in _ORIG and hasattr(_part2, name):
            setattr(_part2, name, _ORIG[name])
        super().__delattr__(name)


sys.modules[__name__].__class__ = _ApiWireModule

__all__ = [
    "MAX_BULLETIN_REPORTS",
    "_AHL_HEADING_SPLIT_CODES",
    "_API_PRODUCTS",
    "_BULLETIN_ID_RE",
    "_CCCC_RE",
    "_EMPTY_BULLETIN_MESSAGE",
    "_INVALID_AHL_MESSAGE",
    "_MULTILINE_TEMPLATE_PRODUCTS",
    "_call_iwxxm_validate",
    "_coerce_form_list",
    "_coerce_form_str",
    "_is_multiline_template_product",
    "_is_named_upload",
    "_iwxxm_validate_fn",
    "_package_issue_payload",
    "_package_stages_payload",
    "_product_uses_aerodrome_icao_layer",
    "_product_uses_metar_tac_layers",
    "_resolve_request_extensions",
    "_resolve_request_profiles",
    "add_loopback_origin_variants",
    "add_origin_if_missing",
    "bulletin_split_http_error",
    "classify_and_validate_upload_content",
    "get_cors_allowed_headers",
    "get_cors_origins",
    "is_dev_cors_relaxation_enabled",
    "is_xml_input",
    "logger",
    "manual_entries_with_offsets",
    "normalize_api_product",
    "normalize_code",
    "normalize_validation_level",
    "parse_files",
    "parse_optional_bulletin_id",
    "parse_optional_files",
    "parse_optional_issuing_center",
    "read_upload_files_text",
    "read_uploaded_text",
    "split_manual_entries",
]
