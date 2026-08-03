"""F29 / #831 quality-matrix helpers (EV-030).

Spike loaders for YAML RuleCase files. Full runners land in M1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

import yaml

Bucket = Literal["happy", "sad", "edge_pass", "edge_fail"]
Engine = Literal["lint", "convert", "validate"]
CaseStatus = Literal["ready", "needs-fixture", "oos"]

BUCKETS: tuple[Bucket, ...] = ("happy", "sad", "edge_pass", "edge_fail")


def _as_str_any_dict(value: object, *, path: Path, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{path}: {field_name} must be a mapping")
    out: dict[str, Any] = {}
    for key_obj, item in cast(dict[object, object], value).items():
        if not isinstance(key_obj, str):
            raise ValueError(f"{path}: {field_name} keys must be strings")
        out[key_obj] = item
    return out


@dataclass(frozen=True)
class RuleCase:
    """One matrix slot: rule x bucket x case id."""

    rule_id: str
    engine: Engine
    bucket: Bucket
    case_id: str
    tac: str | None = None
    status: CaseStatus = "ready"
    expect: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def node_id(self) -> str:
        """Stable pytest / failure id: ``RULE/bucket/case``."""
        return f"{self.rule_id}/{self.bucket}/{self.case_id}"


def load_rule_cases(path: Path) -> list[RuleCase]:
    """Load RuleCase list from a YAML file.

    Accepted shapes:
    - ``{ rule_id, engine, cases: [ {bucket, case_id, ...}, ... ] }``
    - ``{ cases: [ {rule_id, engine, bucket, case_id, ...}, ... ] }``
    """
    raw_obj: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw_obj, dict):
        raise ValueError(f"{path}: root must be a mapping")
    raw = cast(dict[str, object], raw_obj)

    cases_obj = raw.get("cases")
    if not isinstance(cases_obj, list) or not cases_obj:
        raise ValueError(f"{path}: 'cases' must be a non-empty list")
    cases_raw: list[object] = []
    for entry in cases_obj:
        cases_raw.append(cast(object, entry))

    default_rule = raw.get("rule_id")
    default_engine = raw.get("engine")
    out: list[RuleCase] = []
    for i, item_obj in enumerate(cases_raw):
        if not isinstance(item_obj, dict):
            raise ValueError(f"{path}: cases[{i}] must be a mapping")
        item = cast(dict[str, object], item_obj)
        rule_id = item.get("rule_id", default_rule)
        engine_obj = item.get("engine", default_engine)
        if not isinstance(rule_id, str) or not rule_id.strip():
            raise ValueError(f"{path}: cases[{i}] missing rule_id")
        if engine_obj not in ("lint", "convert", "validate"):
            raise ValueError(f"{path}: cases[{i}] invalid engine {engine_obj!r}")
        engine: Engine = engine_obj  # narrowed by membership check above
        bucket_obj = item.get("bucket")
        if bucket_obj not in BUCKETS:
            raise ValueError(f"{path}: cases[{i}] invalid bucket {bucket_obj!r}")
        bucket: Bucket = bucket_obj  # narrowed
        raw_case_id = item.get("case_id")
        if isinstance(raw_case_id, int):
            case_id = f"{raw_case_id:02d}" if raw_case_id < 100 else str(raw_case_id)
        elif isinstance(raw_case_id, str):
            case_id = raw_case_id.strip()
        else:
            raise ValueError(f"{path}: cases[{i}] case_id must be str or int")
        if not (len(case_id) == 2 and case_id.isdigit()):
            raise ValueError(
                f"{path}: cases[{i}] case_id must be two digits (got {case_id!r})"
            )
        status_obj = item.get("status", "ready")
        if status_obj not in ("ready", "needs-fixture", "oos"):
            raise ValueError(f"{path}: cases[{i}] invalid status {status_obj!r}")
        status: CaseStatus = status_obj  # narrowed
        tac_obj = item.get("tac")
        if tac_obj is not None and not isinstance(tac_obj, str):
            raise ValueError(f"{path}: cases[{i}] tac must be string or null")
        tac: str | None = tac_obj
        expect = _as_str_any_dict(
            item.get("expect") or {}, path=path, field_name="expect"
        )
        meta = _as_str_any_dict(item.get("meta") or {}, path=path, field_name="meta")
        out.append(
            RuleCase(
                rule_id=rule_id.strip(),
                engine=engine,
                bucket=bucket,
                case_id=case_id,
                tac=tac,
                status=status,
                expect=expect,
                meta=meta,
            )
        )
    return out
