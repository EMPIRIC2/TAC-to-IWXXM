"""WMO-No. 782 observation-time natural-language phrasing."""

from __future__ import annotations

from tac_decoding import decode_tac


def test_observation_time_uses_handbook_hours_and_minutes_phrasing() -> None:
    tac = "SPECI LUDO 211025Z 31015G27KT 9999 FEW040 10/03 Q0995="
    result = decode_tac(tac, product="SPECI")
    texts = " ".join(s.explanation for s in result.segments)
    if result.summary:
        texts = f"{texts} {result.summary}"
    assert "on 21st of the month at 10 hours and 25 minutes UTC" in texts, texts
