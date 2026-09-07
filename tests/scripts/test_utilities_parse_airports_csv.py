"""Coverage for scripts/utilities/parse_airports_csv.py."""

from __future__ import annotations

from pathlib import Path

import pytest
import scripts.utilities.parse_airports_csv as airports


@pytest.mark.unit
def test_parse_airports_csv_filters_and_enriches(tmp_path: Path) -> None:
    csv_path = tmp_path / "airports.csv"
    csv_path.write_text(
        "\n".join(
            [
                "icao_code,name,municipality,country_name,type,iata_code,latitude_deg,longitude_deg,elevation_ft",
                ",Skip Me,,,,,,,",
                "KJFK,JFK Intl,New York,USA,large_airport,JFK,40.6,-73.7,13",
                "EGLL,Heathrow,London,UK,large_airport,,51.47,-0.45,not-a-number",
                "LFPG,CDG,Paris,France,large_airport,,bad,also-bad,100",
            ]
        ),
        encoding="utf-8",
    )
    rows = airports.parse_airports_csv(csv_path)
    assert len(rows) == 3
    jfk = next(r for r in rows if r["icao"] == "KJFK")
    assert jfk["iata"] == "JFK"
    assert jfk["coordinates"]["elevation_ft"] == 13
    egll = next(r for r in rows if r["icao"] == "EGLL")
    assert "coordinates" in egll
    assert "elevation_ft" not in egll["coordinates"]
    lfpg = next(r for r in rows if r["icao"] == "LFPG")
    assert "coordinates" not in lfpg


@pytest.mark.unit
def test_write_json_output(tmp_path: Path) -> None:
    out = tmp_path / "nested" / "airports.json"
    airports.write_json_output([{"icao": "KJFK"}], out)
    assert out.read_text(encoding="utf-8").startswith("[")


@pytest.mark.unit
def test_parse_airports_elevation_parses_int() -> None:
    rows = airports.parse_airports_csv(
        Path(__file__).resolve().parents[2] / "data" / "af-airports.csv"
    )
    with_elev = [
        r for r in rows if r.get("coordinates", {}).get("elevation_ft") is not None
    ]
    assert with_elev


@pytest.mark.unit
def test_main_missing_csv(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        airports, "__file__", str(tmp_path / "scripts/utilities/parse_airports_csv.py")
    )
    monkeypatch.chdir(tmp_path)
    airports.main()
    assert "ERROR" in capsys.readouterr().out


@pytest.mark.unit
def test_main_happy_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "project"
    scripts_dir = root / "scripts"
    (scripts_dir / "utilities").mkdir(parents=True)
    (scripts_dir / "data").mkdir(parents=True)
    (root / "frontend" / "src" / "data").mkdir(parents=True)
    (root / "backend" / "src" / "data").mkdir(parents=True)
    csv_path = scripts_dir / "data" / "af-airports.csv"
    csv_path.write_text(
        "icao_code,name,municipality,country_name,type,iata_code,latitude_deg,longitude_deg,elevation_ft\n"
        "KJFK,JFK,New York,USA,large_airport,JFK,40.6,-73.7,13\n",
        encoding="utf-8",
    )
    script = scripts_dir / "utilities" / "parse_airports_csv.py"
    monkeypatch.setattr(airports, "__file__", str(script))
    airports.main()
    out = capsys.readouterr().out
    assert "Parsed 1 airports" in out
    assert "Statistics:" in out
