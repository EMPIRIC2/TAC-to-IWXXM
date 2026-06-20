"""Unit tests for airport_data service (airport_data.py) – 0% coverage target."""
import os
import subprocess
from unittest.mock import MagicMock, patch

from src.services import airport_data as airport_module
from src.services.airport_data import _run_parser, check_and_regenerate_airports


class TestRunParser:
    def test_success(self, tmp_path):
        script = tmp_path / "parse.py"
        script.write_text("")
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "done"
        mock_result.stderr = ""
        with patch("src.services.airport_data.subprocess.run", return_value=mock_result):
            assert _run_parser(script) is True

    def test_failure_nonzero_returncode(self, tmp_path):
        script = tmp_path / "parse.py"
        script.write_text("")
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error"
        with patch("src.services.airport_data.subprocess.run", return_value=mock_result):
            assert _run_parser(script) is False

    def test_timeout(self, tmp_path):
        script = tmp_path / "parse.py"
        script.write_text("")
        with patch(
            "src.services.airport_data.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="x", timeout=30),
        ):
            assert _run_parser(script) is False

    def test_generic_exception(self, tmp_path):
        script = tmp_path / "parse.py"
        script.write_text("")
        with patch(
            "src.services.airport_data.subprocess.run",
            side_effect=RuntimeError("unexpected"),
        ):
            assert _run_parser(script) is False


class TestCheckAndRegenerateAirports:
    def _set_module_file(self, monkeypatch, tmp_path):
        fake_module = tmp_path / "backend" / "src" / "services" / "airport_data.py"
        fake_module.parent.mkdir(parents=True)
        fake_module.write_text("# test")
        monkeypatch.setattr(airport_module, "__file__", str(fake_module))

    def test_csv_missing_returns_false(self, monkeypatch, tmp_path):
        self._set_module_file(monkeypatch, tmp_path)
        assert check_and_regenerate_airports() is False

    def test_script_missing_returns_false(self, monkeypatch, tmp_path):
        self._set_module_file(monkeypatch, tmp_path)
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "af-airports.csv").write_text("icao,name\nKJFK,JFK")

        assert check_and_regenerate_airports() is False

    def test_regenerates_when_json_missing(self, monkeypatch, tmp_path):
        self._set_module_file(monkeypatch, tmp_path)
        data_dir = tmp_path / "data"
        scripts_dir = tmp_path / "scripts"
        data_dir.mkdir()
        scripts_dir.mkdir()
        (data_dir / "af-airports.csv").write_text("icao,name\nKJFK,JFK")
        parser = scripts_dir / "parse_airports_csv.py"
        parser.write_text("print('ok')")

        with patch("src.services.airport_data._run_parser", return_value=True) as mock_parser:
            assert check_and_regenerate_airports() is True
            mock_parser.assert_called_once_with(parser)

    def test_regenerates_when_csv_newer(self, monkeypatch, tmp_path):
        self._set_module_file(monkeypatch, tmp_path)
        data_dir = tmp_path / "data"
        scripts_dir = tmp_path / "scripts"
        backend_data = tmp_path / "backend" / "src" / "data"
        data_dir.mkdir()
        scripts_dir.mkdir()
        backend_data.mkdir(parents=True)
        csv_path = data_dir / "af-airports.csv"
        csv_path.write_text("icao,name\nKJFK,JFK")
        json_path = backend_data / "airports.json"
        json_path.write_text("[]")
        parser = scripts_dir / "parse_airports_csv.py"
        parser.write_text("print('ok')")

        os.utime(json_path, (100, 100))
        os.utime(csv_path, (200, 200))

        with patch("src.services.airport_data._run_parser", return_value=True) as mock_parser:
            assert check_and_regenerate_airports() is True
            mock_parser.assert_called_once_with(parser)

    def test_no_regeneration_when_json_newer(self, monkeypatch, tmp_path):
        self._set_module_file(monkeypatch, tmp_path)
        data_dir = tmp_path / "data"
        scripts_dir = tmp_path / "scripts"
        backend_data = tmp_path / "backend" / "src" / "data"
        data_dir.mkdir()
        scripts_dir.mkdir()
        backend_data.mkdir(parents=True)
        csv_path = data_dir / "af-airports.csv"
        json_path = backend_data / "airports.json"
        csv_path.write_text("icao,name\nKJFK,JFK")
        json_path.write_text("[]")
        (scripts_dir / "parse_airports_csv.py").write_text("print('ok')")

        os.utime(csv_path, (100, 100))
        os.utime(json_path, (200, 200))

        with patch("src.services.airport_data._run_parser") as mock_parser:
            assert check_and_regenerate_airports() is False
            mock_parser.assert_not_called()

    def test_exception_returns_false(self):
        """Function should return False on unexpected exception."""
        with patch(
            "src.services.airport_data.Path",
            side_effect=Exception("unexpected"),
        ):
            result = check_and_regenerate_airports()
        assert result is False
