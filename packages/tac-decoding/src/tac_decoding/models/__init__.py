"""Data models for tac-decoding.

[Corpus: product §F9]
"""

from __future__ import annotations

from tac_decoding.models.bulletin import _BulletinMeta, _BulletinSplit
from tac_decoding.models.catalog import CatalogEntry, CatalogTokenMeta
from tac_decoding.models.collect import CollectError, CollectField, CollectRead
from tac_decoding.models.decode_result import DecodeResidual, DecodeResult, DecodeSegment
from tac_decoding.models.dictionary import (
    DictionaryEntry,
    DictionaryFacets,
    DictionaryTokenFields,
)
from tac_decoding.models.ir import IrResidual, IrSpan, PackIr
from tac_decoding.models.locale import ExplanationHook, LocaleError
from tac_decoding.models.match import MatchBudgetError, MatchContext, MatchResult, MatchSpan
from tac_decoding.models.pack_file import PackFileMapping, PackRuleMapping
from tac_decoding.models.packs import Pack, PackSchemaError, Rule
from tac_decoding.models.remarks import REMARK_FAMILIES, RemarkDecodeResult, RemarkGroup

__all__ = [
    "REMARK_FAMILIES",
    "CatalogEntry",
    "CatalogTokenMeta",
    "CollectError",
    "CollectField",
    "CollectRead",
    "DecodeResidual",
    "DecodeResult",
    "DecodeSegment",
    "DictionaryEntry",
    "DictionaryFacets",
    "DictionaryTokenFields",
    "ExplanationHook",
    "IrResidual",
    "IrSpan",
    "LocaleError",
    "MatchBudgetError",
    "MatchContext",
    "MatchResult",
    "MatchSpan",
    "Pack",
    "PackFileMapping",
    "PackIr",
    "PackRuleMapping",
    "PackSchemaError",
    "RemarkDecodeResult",
    "RemarkGroup",
    "Rule",
    "_BulletinMeta",
    "_BulletinSplit",
]
