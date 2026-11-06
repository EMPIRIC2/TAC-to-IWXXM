"""BUG-2026-11-04 / #1557 — parallel convert must not raise GlobalHydra race.

Live-eval CWDQ/CWDV failures were Hydra concurrency, not Canada TAC content.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from tac2iwxxm.convert_allowlist import load_convert_allowlist

from tac2iwxxm import convert

_SAMPLES = (
    "METAR CWDQ 021100Z AUTO 14002KT 9999 06/05 Q1013=",
    "METAR CWDV 021100Z AUTO 14002KT 9999 06/05 Q1013=",
)


def test_parallel_convert_cwdq_cwdv_no_global_hydra_race() -> None:
    """ThreadPool converts must not raise GlobalHydra is already initialized."""

    def _one(index: int) -> None:
        # Clear so each worker re-enters Hydra compose (cold parallel cohort).
        load_convert_allowlist.cache_clear()
        convert(
            _SAMPLES[index % len(_SAMPLES)],
            product="METAR",
            profile="annex3",
            iwxxm_version="2025-2",
        )

    errors: list[Exception] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(_one, i) for i in range(32)]
        for fut in as_completed(futures):
            try:
                fut.result()
            except Exception as exc:
                errors.append(exc)

    hydra_errors = [exc for exc in errors if "GlobalHydra" in str(exc)]
    assert not hydra_errors, hydra_errors
