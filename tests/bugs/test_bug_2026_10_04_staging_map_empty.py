"""BUG-2026-10-04 - staging map stays empty when the API misses the shared cache.

The image rollout turns the API timer off. It must also point the API at the
same database the translator writes, or Decode visuals returns no places.
"""

from __future__ import annotations

from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "deploy"
    / "doks_rollout_images.sh"
)


def test_bug_2026_10_04_staging_rollout_shares_the_map_cache() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "LIVE_MAP_CACHE_URL" in text
    assert "metar-api-secrets" in text
    assert "DATABASE_URL" in text
