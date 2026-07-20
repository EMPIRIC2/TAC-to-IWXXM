#!/usr/bin/env python3
"""Regenerate docs/domain/rules/ISSUE_CATALOG.md (+ JSON) from tac-validate registry.

Used by ``make catalog-regen``. Until T1.2 lands ``issue_registry``, writes a stub
catalog noting the pending module (exit 0). After registry exists, exports all rows.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CATALOG_MD = REPO / "docs" / "domain" / "rules" / "ISSUE_CATALOG.md"
CATALOG_JSON = REPO / "docs" / "domain" / "rules" / "ISSUE_CATALOG.json"
SRC = REPO / "packages" / "tac-validate" / "src"


def _stub_rows() -> list[dict[str, object]]:
    return []


def _load_rows() -> tuple[list[dict[str, object]], str]:
    sys.path.insert(0, str(SRC))
    try:
        from tac_validate.issue_registry import ISSUES  # type: ignore[import-not-found]
    except ImportError:
        return (
            _stub_rows(),
            "stub — packages/tac-validate issue_registry not present yet (T1.2)",
        )

    rows: list[dict[str, object]] = []
    for spec in ISSUES:
        rows.append(
            {
                "code": getattr(spec, "code", None),
                "severity": getattr(spec, "severity", None),
                "message_template": getattr(spec, "message_template", None)
                or getattr(spec, "message", None),
                "product": getattr(spec, "product", None),
                "tags": list(getattr(spec, "tags", ()) or ()),
            }
        )
    rows.sort(key=lambda r: str(r.get("code") or ""))
    return rows, "generated from tac_validate.issue_registry"


def _write_md(rows: list[dict[str, object]], source: str) -> None:
    lines = [
        "# TAC lint issue catalog",
        "",
        f"> **Source**: {source}  ",
        f"> **Generated**: {date.today().isoformat()} via `make catalog-regen`  ",
        "> **ADR**: ADR-028 / F15 / EV-011",
        "",
        "Public `code` values are stable. Default severities may tighten in minor releases.",
        "Do not invent ad-hoc `severity=` literals in rule bodies — import from the registry.",
        "",
        "| Code | Severity | Message template | Product | Tags |",
        "|------|----------|------------------|---------|------|",
    ]
    if not rows:
        lines.append("| _(none yet)_ | — | Registry module pending T1.2 | — | — |")
    else:
        for r in rows:
            tags = ", ".join(str(t) for t in (r.get("tags") or []))
            lines.append(
                f"| `{r.get('code')}` | `{r.get('severity')}` | "
                f"{r.get('message_template') or ''} | {r.get('product') or '—'} | {tags or '—'} |"
            )
    lines.append("")
    CATALOG_MD.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_MD.write_text("\n".join(lines), encoding="utf-8")


def _write_json(rows: list[dict[str, object]], source: str) -> None:
    payload = {
        "schema_version": 1,
        "source": source,
        "generated": date.today().isoformat(),
        "issues": rows,
    }
    CATALOG_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    rows, source = _load_rows()
    _write_md(rows, source)
    _write_json(rows, source)
    print(
        f"Wrote {CATALOG_MD.relative_to(REPO)} and {CATALOG_JSON.relative_to(REPO)} ({source})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
