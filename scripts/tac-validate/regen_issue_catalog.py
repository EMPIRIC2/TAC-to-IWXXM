#!/usr/bin/env python3
"""Regenerate docs/domain/rules/ISSUE_CATALOG.md (+ JSON) from tac-validate registry.

Also writes packages/tac-validate/.../catalog_attribution.json from PROVENANCE_MAP
(EV-040 source attribution for API/FE). Used by ``make catalog-regen``.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Operator-facing attribution must stay free of planning vocabulary (EV-048).
_INTERNAL_DOC_REF_IN_NOTE = re.compile(
    r"(?:\[Corpus:|\bADR-\d+\b|\bEV-\d+\b|\bS0\d+\b|\bTC-[A-Z0-9-]+\b|"
    r"\bE\d{2}-\d+\b|(?<!\w)#\d{3,}\b|\bF\d+\b|docs/sessions/|docs/feature-list)"
)
CATALOG_MD = REPO / "docs" / "domain" / "rules" / "ISSUE_CATALOG.md"
CATALOG_JSON = REPO / "docs" / "domain" / "rules" / "ISSUE_CATALOG.json"
PROVENANCE = REPO / "docs" / "domain" / "rules" / "PROVENANCE_MAP.json"
ATTRIBUTION_JSON = (
    REPO
    / "packages"
    / "tac-validate"
    / "src"
    / "tac_validate"
    / "data"
    / "catalog_attribution.json"
)
SRC = REPO / "packages" / "tac-validate" / "src"


def _stub_rows() -> list[dict[str, object]]:
    return []


def _load_provenance() -> dict[str, dict[str, object]]:
    if not PROVENANCE.is_file():
        return {}
    try:
        data = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    out: dict[str, dict[str, object]] = {}
    for row in data.get("catalog_codes") or []:
        if not isinstance(row, dict):
            continue
        code = row.get("code")
        if not code:
            continue
        out[str(code)] = row
    return out


def _attribution_fields(prov: dict[str, object] | None) -> dict[str, str | None]:
    if not prov:
        return {
            "source_id": None,
            "source_url": None,
            "source_attribution": None,
        }
    source_id = prov.get("source_id")
    source_url = prov.get("source_url")
    status = prov.get("status")
    note = prov.get("note")
    parts: list[str] = []
    if source_id:
        parts.append(str(source_id))
    if status in {"paywall", "gap", "N/A"}:
        parts.append(f"access:{status}")
    # Prefer stable URL in operator-facing attribution; note is secondary.
    if source_url:
        parts.append(str(source_url))
    if note and not _INTERNAL_DOC_REF_IN_NOTE.search(str(note)):
        parts.append(str(note))
    elif note:
        print(
            f"warning: omitting provenance note with internal doc refs from "
            f"operator attribution: {note!r}",
            file=sys.stderr,
        )
    return {
        "source_id": str(source_id) if source_id else None,
        "source_url": str(source_url) if source_url else None,
        "source_attribution": " — ".join(parts) if parts else None,
    }


def _load_rows() -> tuple[list[dict[str, object]], str]:
    sys.path.insert(0, str(SRC))
    try:
        from tac_validate.issue_registry import ISSUES  # type: ignore[import-not-found]
    except ModuleNotFoundError as exc:
        missing = exc.name or ""
        if missing in {
            "tac_validate",
            "tac_validate.issue_registry",
        } or missing.startswith("tac_validate."):
            return (
                _stub_rows(),
                "stub — packages/tac-validate issue_registry not present yet (T1.2)",
            )
        raise
    except ImportError:
        return (
            _stub_rows(),
            "stub — packages/tac-validate issue_registry not present yet (T1.2)",
        )

    provenance = _load_provenance()
    rows: list[dict[str, object]] = []
    for spec in ISSUES:
        code = getattr(spec, "code", None)
        attr = _attribution_fields(provenance.get(str(code)) if code else None)
        rows.append(
            {
                "code": code,
                "severity": getattr(spec, "severity", None),
                "message_template": getattr(spec, "message_template", None)
                or getattr(spec, "message", None),
                "product": getattr(spec, "product", None),
                "tags": list(getattr(spec, "tags", ()) or ()),
                **attr,
            }
        )
    rows.sort(key=lambda r: str(r.get("code") or ""))
    return rows, "generated from tac_validate.issue_registry + PROVENANCE_MAP"


def _write_attribution_package(rows: list[dict[str, object]], generated: str) -> None:
    codes: dict[str, dict[str, object]] = {}
    for r in rows:
        code = r.get("code")
        if not code:
            continue
        codes[str(code)] = {
            "source_id": r.get("source_id"),
            "source_url": r.get("source_url"),
            "status": None,
            "note": None,
            "source_attribution": r.get("source_attribution"),
        }
    # Prefer richer fields from provenance map when present
    for code, prov in _load_provenance().items():
        if code not in codes:
            continue
        codes[code] = {
            "source_id": prov.get("source_id"),
            "source_url": prov.get("source_url"),
            "status": prov.get("status"),
            "note": prov.get("note"),
            "source_attribution": _attribution_fields(prov)["source_attribution"],
        }
    ATTRIBUTION_JSON.parent.mkdir(parents=True, exist_ok=True)
    ATTRIBUTION_JSON.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated": generated,
                "source": "PROVENANCE_MAP.json catalog_codes",
                "codes": codes,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _stable_generated(rows: list[dict[str, object]], source: str) -> str:
    """Keep prior generated date when issue rows/source are unchanged (CI-friendly)."""
    today = date.today().isoformat()
    if not CATALOG_JSON.exists():
        return today
    try:
        prior = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return today
    if prior.get("source") == source and prior.get("issues") == rows:
        prev = prior.get("generated")
        if isinstance(prev, str) and prev:
            return prev
    return today


def _write_md(rows: list[dict[str, object]], source: str, generated: str) -> None:
    lines = [
        "# TAC lint issue catalog",
        "",
        f"> **Source**: {source}  ",
        f"> **Generated**: {generated} via `make catalog-regen`  ",
        "> **ADR**: ADR-028 / F15 / EV-011 / F20 / EV-015 / F23 / EV-019 / EV-040",
        "",
        "Public `code` values are stable. Default severities may tighten in minor releases.",
        "Do not invent ad-hoc `severity=` literals in rule bodies — import from the registry.",
        "Source attribution joins `PROVENANCE_MAP` (WMO / ICAO / IWXXM citations — no Annex prose).",
        "",
        "| Code | Severity | Message template | Product | Tags | Source attribution |",
        "|------|----------|------------------|---------|------|--------------------|",
    ]
    if not rows:
        lines.append("| _(none yet)_ | — | Registry module pending T1.2 | — | — | — |")
    else:
        for r in rows:
            tags = ", ".join(str(t) for t in (r.get("tags") or []))
            src = r.get("source_attribution") or "—"
            # Escape pipes in attribution for markdown tables
            src_cell = str(src).replace("|", "\\|")
            lines.append(
                f"| `{r.get('code')}` | `{r.get('severity')}` | "
                f"{r.get('message_template') or ''} | {r.get('product') or '—'} | "
                f"{tags or '—'} | {src_cell} |"
            )
    lines.append("")
    CATALOG_MD.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_MD.write_text("\n".join(lines), encoding="utf-8")


def _write_json(rows: list[dict[str, object]], source: str, generated: str) -> None:
    payload = {
        "schema_version": 1,
        "source": source,
        "generated": generated,
        "issues": rows,
    }
    CATALOG_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    rows, source = _load_rows()
    generated = _stable_generated(rows, source)
    _write_md(rows, source, generated)
    _write_json(rows, source, generated)
    _write_attribution_package(rows, generated)
    print(
        f"Wrote {CATALOG_MD.relative_to(REPO)}, {CATALOG_JSON.relative_to(REPO)}, "
        f"and {ATTRIBUTION_JSON.relative_to(REPO)} ({source})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
