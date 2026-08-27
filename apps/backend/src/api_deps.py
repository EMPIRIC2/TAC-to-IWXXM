"""Patchable API collaborators (EV-037 TD-3a).

Central module for dependencies that unit tests monkeypatch on ``src.api``.
Route handlers in ``api.py`` resolve unqualified names from this module's
exports via ``api`` re-exports; future routers should call ``api_deps.X(...)``
at use sites.

[Corpus: system-spec] · [Corpus: decisions] ev-037-tech-debt-pass §TD-3
"""

from __future__ import annotations

try:
    from .config.icao_opmet import get_icao_region, get_translation_centre_info
    from .msgspec_http import msgspec_json_response
    from .services.statistics import statistics_service
    from .services.validation import ValidationService
    from .services.validation_orchestrator import get_validation_orchestrator
    from .services.webhooks import webhook_service
    from .utilities.conversion import convert_metar_tac_with_metadata
except ImportError:  # pragma: no cover - Docker/local import path mirror
    from config.icao_opmet import get_icao_region, get_translation_centre_info
    from msgspec_http import msgspec_json_response
    from services.statistics import statistics_service
    from services.validation import ValidationService
    from services.validation_orchestrator import get_validation_orchestrator
    from services.webhooks import webhook_service
    from utilities.conversion import convert_metar_tac_with_metadata

from iwxxm_validate import validate_iwxxm as iwxxm_validate_fn
from tac2iwxxm import split_bulletin as tac2iwxxm_split_bulletin

try:
    from . import api_wire
except ImportError:  # pragma: no cover - Docker/local import path mirror
    import api_wire

read_uploaded_text = api_wire.read_uploaded_text
read_upload_files_text = api_wire.read_upload_files_text
classify_and_validate_upload_content = api_wire.classify_and_validate_upload_content
_call_iwxxm_validate = api_wire._call_iwxxm_validate

__all__ = [
    "ValidationService",
    "_call_iwxxm_validate",
    "classify_and_validate_upload_content",
    "convert_metar_tac_with_metadata",
    "get_icao_region",
    "get_translation_centre_info",
    "get_validation_orchestrator",
    "iwxxm_validate_fn",
    "msgspec_json_response",
    "read_upload_files_text",
    "read_uploaded_text",
    "statistics_service",
    "tac2iwxxm_split_bulletin",
    "webhook_service",
]
