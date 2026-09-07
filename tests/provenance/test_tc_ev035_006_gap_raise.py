"""TC-EV035-006 - gap raise gate (no silent invent)."""

from __future__ import annotations

from tests.provenance._helpers import GAP_REPORT, load_map


def test_tc_ev035_006_gap_report_when_gaps() -> None:
    data = load_map()
    gaps = data.get("gaps") or []
    gap_statuses = []
    for section, key, status_key in (
        ("digs", "path", "status"),
        ("catalog_codes", "code", "status"),
        ("full_stack_rules", "rule_id", "status"),
    ):
        gap_statuses.extend(
            f"{section}:{row[key]}"
            for row in data.get(section) or []
            if row.get(status_key) == "gap"
        )
    gap_statuses.extend(
        f"matrix:{cell['product']}/{cell['role']}"
        for cell in data.get("matrix_cells") or []
        if cell.get("disposition") == "warn" and cell.get("ticket")
    )
    if not gaps and not gap_statuses:
        return

    assert GAP_REPORT.is_file(), (
        f"gap rows present ({len(gaps)} map gaps / {len(gap_statuses)} status) "
        f"but missing {GAP_REPORT}"
    )
    text = GAP_REPORT.read_text(encoding="utf-8")
    assert len(text) > 100, "provenance-gaps.md looks empty/stale"
    # Each map gap ticket must appear in the report
    for g in gaps:
        ticket = (g.get("ticket") or "").lstrip("#")
        if ticket:
            assert ticket in text, f"gap ticket #{ticket} not in provenance-gaps.md"


def test_tc_ev035_006_map_gaps_have_tickets() -> None:
    data = load_map()
    for g in data.get("gaps") or []:
        assert g.get("ticket"), f"gap without ticket: {g}"
        assert g.get("id"), f"gap without id: {g}"
