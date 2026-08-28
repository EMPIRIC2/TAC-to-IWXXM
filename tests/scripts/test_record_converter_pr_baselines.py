"""Coverage for scripts/bench/record_converter_pr_baselines.py."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import scripts.bench.record_converter_pr_baselines as record
import yaml


@pytest.mark.unit
def test_main_records_yaml(tmp_path: Path) -> None:
    out = tmp_path / "converter_pr.yaml"
    baselines = MagicMock()
    baselines.raw = {"version": 1, "products": {}}
    payload = {"version": 1, "status": "laptop_seed", "products": {}}

    with (
        patch(
            "scripts.bench.record_converter_pr_baselines.load_converter_pr_baselines",
            return_value=baselines,
        ),
        patch(
            "scripts.bench.record_converter_pr_baselines.record_baselines_dict",
            return_value=payload,
        ),
        patch(
            "sys.argv",
            [
                "prog",
                "--host",
                "test-host",
                "--status",
                "laptop_seed",
                "--out",
                str(out),
            ],
        ),
    ):
        assert record.main() == 0

    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert data["status"] == "laptop_seed"
    assert "recorded" in data
