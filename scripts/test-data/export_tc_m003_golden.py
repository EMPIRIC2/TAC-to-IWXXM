#!/usr/bin/env python3
"""Export TC-M003 golden conversion baselines into test-data/golden/.

Run from repo root::

    uv run python scripts/test-data/export_tc_m003_golden.py

Uses ``tests/migration/gifts_baseline.py`` against the current ``GIFTs/`` tree.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.migration.gifts_baseline import (  # noqa: E402
    convert_tac_bulletin_to_observation_xml,
)

from metar_shared.xml_canonical import canonicalize_xml  # noqa: E402

GOLDEN_DIR = ROOT / "test-data" / "golden"
CASES_DIR = GOLDEN_DIR / "cases"

# Representative METAR/SPECI set — migration-plan.md Step 0 golden export.
FIXTURE_CASES: list[dict[str, str]] = [
    {
        "id": "kjfk_basic",
        "tac": "SAXX99 KWBC 231751\nMETAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=",
    },
    {
        "id": "klax_basic",
        "tac": "SAXX99 KWBC 231753\nMETAR KLAX 231753Z 25008KT 10SM FEW020 18/12 A2992=",
    },
    {
        "id": "kord_basic",
        "tac": "SAXX99 KWBC 231756\nMETAR KORD 231756Z 16008KT 10SM SCT035 14/05 A3012=",
    },
    {
        "id": "speci_sn",
        "tac": (
            "SAXX99 KWBC 232045\n"
            "SPECI KJFK 232045Z 20015G25KT 8SM -SN BKN020 OVC040 12/06 A3001="
        ),
    },
    {
        "id": "metar_nil",
        "tac": "SAXX99 XXXX 311300\nMETAR VHHH 311338Z NIL=",
    },
]


def export_golden_baselines() -> None:
    CASES_DIR.mkdir(parents=True, exist_ok=True)

    manifest_cases: list[dict[str, str]] = []

    for case in FIXTURE_CASES:
        case_id = case["id"]
        tac = case["tac"]
        tac_path = CASES_DIR / f"{case_id}.tac"
        golden_path = CASES_DIR / f"{case_id}.golden.xml"

        tac_path.write_text(tac + "\n", encoding="utf-8")

        observation_xml = convert_tac_bulletin_to_observation_xml(tac)
        canonical = canonicalize_xml(observation_xml)
        golden_path.write_text(canonical + "\n", encoding="utf-8")

        manifest_cases.append(
            {
                "id": case_id,
                "tac": f"cases/{case_id}.tac",
                "golden": f"cases/{case_id}.golden.xml",
            }
        )

    manifest = {
        "schema_version": 1,
        "description": "TC-M003 golden conversion baseline (REQ-018)",
        "cases": manifest_cases,
    }
    (GOLDEN_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Exported {len(manifest_cases)} golden cases to {GOLDEN_DIR}")


if __name__ == "__main__":
    export_golden_baselines()
