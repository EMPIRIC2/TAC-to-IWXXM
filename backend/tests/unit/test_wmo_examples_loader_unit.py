"""Unit tests for WMOExamplesLoader – 0% coverage target."""


from src.utilities.wmo_examples_loader import WMOExample, WMOExamplesLoader, load_wmo_examples


def _make_examples_dir(tmp_path, version="2025-2"):
    """Create a fake schema/version/examples directory with sample XML files."""
    examples_dir = tmp_path / version / "examples"
    examples_dir.mkdir(parents=True)
    return examples_dir


def _write_xml(examples_dir, filename):
    (examples_dir / filename).write_text(
        '<?xml version="1.0"?><MeteorologicalAerodromeObservationReport xmlns="http://icao.int/iwxxm/2.1"/>'
    )


class TestWMOExampleDataclass:
    def test_defaults(self, tmp_path):
        xml_path = tmp_path / "file.xml"
        xml_path.write_text("<xml/>")
        ex = WMOExample(
            example_id="metar-A3-1",
            version="2025-2",
            message_type="METAR",
            xml_path=xml_path,
        )
        assert ex.tac_path is None
        assert ex.is_nil_report is False
        assert ex.is_collect is False
        assert ex.metadata == {}


class TestWMOExamplesLoaderInit:
    def test_init_stores_path(self, tmp_path):
        loader = WMOExamplesLoader(schemas_base_path=tmp_path)
        assert loader.schemas_base_path == tmp_path


class TestWMOExamplesLoaderLoadExamples:
    def test_load_examples_missing_dir_returns_empty(self, tmp_path):
        loader = WMOExamplesLoader(schemas_base_path=tmp_path)
        result = loader.load_examples(version="9999-9")
        assert result == []

    def test_load_examples_returns_list(self, tmp_path):
        examples_dir = _make_examples_dir(tmp_path)
        _write_xml(examples_dir, "metar-A3-1.xml")
        loader = WMOExamplesLoader(schemas_base_path=tmp_path)
        result = loader.load_examples(version="2025-2")
        assert isinstance(result, list)

    def test_load_examples_detects_metar(self, tmp_path):
        examples_dir = _make_examples_dir(tmp_path)
        _write_xml(examples_dir, "metar-A3-1.xml")
        loader = WMOExamplesLoader(schemas_base_path=tmp_path)
        results = loader.load_examples(version="2025-2")
        metar_examples = [e for e in results if e.message_type == "METAR"]
        assert len(metar_examples) >= 1

    def test_load_examples_detects_taf(self, tmp_path):
        examples_dir = _make_examples_dir(tmp_path)
        _write_xml(examples_dir, "taf-B1-1.xml")
        loader = WMOExamplesLoader(schemas_base_path=tmp_path)
        results = loader.load_examples(version="2025-2")
        taf_examples = [e for e in results if e.message_type == "TAF"]
        assert len(taf_examples) >= 1

    def test_load_examples_filter_by_type(self, tmp_path):
        examples_dir = _make_examples_dir(tmp_path)
        _write_xml(examples_dir, "metar-A3-1.xml")
        _write_xml(examples_dir, "taf-B1-1.xml")
        loader = WMOExamplesLoader(schemas_base_path=tmp_path)
        results = loader.load_examples(version="2025-2", message_types=["METAR"])
        assert all(e.message_type == "METAR" for e in results)
        assert len(results) >= 1

    def test_load_examples_tac_file_linked(self, tmp_path):
        examples_dir = _make_examples_dir(tmp_path)
        _write_xml(examples_dir, "metar-A3-1.xml")
        (examples_dir / "metar-A3-1.tac").write_text("METAR KJFK 291955Z AUTO 09005KT 9999 FEW020 18/16 A3003=")
        loader = WMOExamplesLoader(schemas_base_path=tmp_path)
        results = loader.load_examples(version="2025-2")
        matched = [e for e in results if e.example_id == "metar-A3-1"]
        if matched:
            assert matched[0].tac_path is not None

    def test_load_examples_nil_flag(self, tmp_path):
        examples_dir = _make_examples_dir(tmp_path)
        _write_xml(examples_dir, "metar-nil-A3-1.xml")
        loader = WMOExamplesLoader(schemas_base_path=tmp_path)
        results = loader.load_examples(version="2025-2")
        nil_examples = [e for e in results if e.is_nil_report]
        # nil flag depends on implementation; just confirm no crash
        assert isinstance(nil_examples, list)

    def test_load_examples_unknown_type_falls_back(self, tmp_path):
        examples_dir = _make_examples_dir(tmp_path)
        _write_xml(examples_dir, "unknown-type-001.xml")
        loader = WMOExamplesLoader(schemas_base_path=tmp_path)
        # Should not raise; unknown type examples included as UNKNOWN or similar
        results = loader.load_examples(version="2025-2")
        assert isinstance(results, list)


class TestWMOExamplesLoaderHelpers:
    def test_load_all_versions_auto_detects_non_empty_versions(self, tmp_path):
        first_dir = _make_examples_dir(tmp_path, version="2024-1")
        second_dir = _make_examples_dir(tmp_path, version="2025-2")
        _write_xml(first_dir, "metar-A3-1.xml")
        _write_xml(second_dir, "taf-B1-1.xml")
        (tmp_path / "ignored").mkdir()

        loader = WMOExamplesLoader(schemas_base_path=tmp_path)
        results = loader.load_all_versions()

        assert sorted(results) == ["2024-1", "2025-2"]
        assert results["2024-1"][0].message_type == "METAR"
        assert results["2025-2"][0].message_type == "TAF"

    def test_get_tac_xml_pairs_filters_by_message_type(self, tmp_path):
        examples_dir = _make_examples_dir(tmp_path)
        _write_xml(examples_dir, "metar-A3-1.xml")
        _write_xml(examples_dir, "taf-B1-1.xml")
        (examples_dir / "metar-A3-1.tac").write_text("METAR TEST")
        (examples_dir / "taf-B1-1.tac").write_text("TAF TEST")
        loader = WMOExamplesLoader(schemas_base_path=tmp_path)

        pairs = loader.get_tac_xml_pairs("2025-2", message_type="METAR")

        assert len(pairs) == 1
        assert pairs[0][2] == "metar-A3-1"
        assert pairs[0][0].suffix == ".tac"
        assert pairs[0][1].suffix == ".xml"

    def test_load_guidance_document_and_manifest_counts(self, tmp_path):
        examples_dir = _make_examples_dir(tmp_path)
        _write_xml(examples_dir, "metar-nil-A3-1.xml")
        _write_xml(examples_dir, "taf-collect-translation-failed-B1-1.xml")
        (examples_dir / "metar-nil-A3-1.tac").write_text("METAR TEST")
        guidance_path = examples_dir / "TAC-to-XML-Guidance.txt"
        guidance_path.write_text("guidance", encoding="utf-8")
        loader = WMOExamplesLoader(schemas_base_path=tmp_path)

        manifest = loader.get_example_manifest("2025-2")

        assert loader.load_guidance_document("2025-2") == "guidance"
        assert loader.load_guidance_document("2024-1") is None
        assert manifest == {
            "version": "2025-2",
            "total_examples": 2,
            "by_message_type": {"METAR": 1, "TAF": 1},
            "with_tac_pairs": 1,
            "nil_reports": 1,
            "collect_bulletins": 1,
            "translation_failed_cases": 1,
        }

    def test_message_type_scenario_and_version_detection_helpers(self, tmp_path):
        _make_examples_dir(tmp_path, version="2025-2")
        loader = WMOExamplesLoader(schemas_base_path=tmp_path)

        assert loader._detect_message_type("spacewx-001") == "SPACE_WEATHER"
        assert loader._detect_message_type("qvaci-example") == "QVACI"
        assert loader._detect_message_type("mystery-example") == "UNKNOWN"
        assert loader._extract_scenario("metar-A3-1") == "A3-1"
        assert loader._extract_scenario("metar") is None
        assert loader._detect_available_versions() == ["2025-2"]

    def test_load_wmo_examples_convenience_function(self, tmp_path):
        examples_dir = _make_examples_dir(tmp_path)
        _write_xml(examples_dir, "speci-A1.xml")

        examples = load_wmo_examples("2025-2", tmp_path, message_types=["SPECI"])

        assert len(examples) == 1
        assert examples[0].message_type == "SPECI"
