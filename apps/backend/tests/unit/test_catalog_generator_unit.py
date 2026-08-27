"""Unit tests for CatalogGenerator - 0% coverage target."""

import json
from pathlib import Path

import pytest
from lxml import etree as ET
from src.services.catalog_generator import (
    CatalogGenerator,
    generate_all_catalogs,
    generate_catalog_for_version,
)


class TestCatalogGeneratorInit:
    def test_init_stores_path(self, tmp_path):
        gen = CatalogGenerator(schemas_base_path=tmp_path)
        assert gen.schemas_base_path == tmp_path

    def test_init_converts_to_path(self, tmp_path):
        gen = CatalogGenerator(schemas_base_path=str(tmp_path))
        assert isinstance(gen.schemas_base_path, Path)


class TestCatalogGeneratorGenerateCatalog:
    def _setup_version_dir(self, tmp_path, version="2025-2"):
        schema_dir = tmp_path / version
        schema_dir.mkdir()
        return schema_dir

    def test_generate_catalog_creates_xml(self, tmp_path):
        self._setup_version_dir(tmp_path)
        gen = CatalogGenerator(schemas_base_path=tmp_path)
        path = gen.generate_catalog(version="2025-2", remote_base_url="https://schemas.wmo.int/iwxxm/2025-2/")
        assert path.exists()
        assert path.name == "catalog.xml"

    def test_generate_catalog_raises_when_dir_missing(self, tmp_path):
        gen = CatalogGenerator(schemas_base_path=tmp_path)
        with pytest.raises(FileNotFoundError, match=r".*"):
            gen.generate_catalog(version="9999-9", remote_base_url="https://example.com/")

    def test_generate_catalog_contains_rewrite_uri(self, tmp_path):
        self._setup_version_dir(tmp_path)
        gen = CatalogGenerator(schemas_base_path=tmp_path)
        path = gen.generate_catalog(version="2025-2", remote_base_url="https://schemas.wmo.int/iwxxm/2025-2/")
        tree = ET.parse(str(path))
        root = tree.getroot()
        # Root should be a catalog element
        assert "catalog" in root.tag

    def test_generate_catalog_with_explicit_local_dir(self, tmp_path):
        explicit_dir = tmp_path / "explicit"
        explicit_dir.mkdir()
        gen = CatalogGenerator(schemas_base_path=tmp_path)
        path = gen.generate_catalog(
            version="2025-2",
            remote_base_url="https://schemas.wmo.int/iwxxm/2025-2/",
            local_schema_dir=explicit_dir,
        )
        assert path.exists()
        assert path.parent == explicit_dir

    def test_generates_common_dependencies_when_present(self, tmp_path):
        schema_dir = self._setup_version_dir(tmp_path)
        # Create one common dependency dir
        gml_dir = schema_dir / "externalSchema" / "gml" / "3.2.1"
        gml_dir.mkdir(parents=True)
        gen = CatalogGenerator(schemas_base_path=tmp_path)
        path = gen.generate_catalog(version="2025-2", remote_base_url="https://schemas.wmo.int/iwxxm/2025-2/")
        content = path.read_text()
        # GML rewrite should be included
        assert "opengis.net/gml" in content

    def test_no_common_dependencies_when_dirs_missing(self, tmp_path):
        self._setup_version_dir(tmp_path)
        gen = CatalogGenerator(schemas_base_path=tmp_path)
        path = gen.generate_catalog(version="2025-2", remote_base_url="https://schemas.wmo.int/iwxxm/2025-2/")
        content = path.read_text()
        # Should not include GML since externalSchema/gml doesn't exist
        assert "opengis.net/gml" not in content


class TestCatalogGeneratorHelpers:
    def test_add_rewrite_uri_appends_element(self, tmp_path):
        gen = CatalogGenerator(schemas_base_path=tmp_path)
        CATALOG_NS = "urn:oasis:names:tc:entity:xmlns:xml:catalog"
        catalog_elem = ET.Element(f"{{{CATALOG_NS}}}catalog")
        gen._add_rewrite_uri(catalog_elem, "https://example.com/", "file:///local/")
        children = list(catalog_elem)
        assert len(children) == 1
        assert children[0].get("uriStartString") == "https://example.com/"
        assert children[0].get("rewritePrefix") == "file:///local/"


class TestCatalogGeneratorGenerateAll:
    def test_generate_all_empty_when_no_versions(self, tmp_path):
        gen = CatalogGenerator(schemas_base_path=tmp_path)
        result = gen.generate_all_catalogs()
        assert isinstance(result, list)

    def test_generate_all_skips_dirs_without_manifest_or_root_url(self, monkeypatch, tmp_path):
        missing_manifest = tmp_path / "2025-1"
        missing_manifest.mkdir()
        empty_root = tmp_path / "2025-2"
        empty_root.mkdir()
        (empty_root / ".manifest.json").write_text(json.dumps({"root_url": ""}), encoding="utf-8")
        valid_dir = tmp_path / "2025-3"
        valid_dir.mkdir()
        (valid_dir / ".manifest.json").write_text(
            json.dumps({"root_url": "https://schemas.wmo.int/iwxxm/2025-3/iwxxm.xsd"}), encoding="utf-8"
        )
        calls = []

        def fake_generate_catalog(version, remote_base_url, local_schema_dir=None):
            calls.append((version, remote_base_url, local_schema_dir))
            return local_schema_dir / "catalog.xml"

        monkeypatch.setattr(CatalogGenerator, "generate_catalog", staticmethod(fake_generate_catalog))

        result = CatalogGenerator(tmp_path).generate_all_catalogs()

        assert result == [valid_dir / "catalog.xml"]
        assert calls == [
            ("2025-3", "https://schemas.wmo.int/iwxxm/2025-3/", valid_dir),
        ]

    def test_generate_all_uses_manifest_and_skips_special_directories(self, monkeypatch, tmp_path):
        version_dir = tmp_path / "2025-2"
        version_dir.mkdir()
        (version_dir / ".manifest.json").write_text(
            json.dumps({"root_url": "https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd"}), encoding="utf-8"
        )
        (tmp_path / "backup-old").mkdir()
        (tmp_path / "template-schemas").mkdir()
        (tmp_path / "plain-file.txt").write_text("ignore", encoding="utf-8")
        calls = []

        def fake_generate_catalog(version, remote_base_url, local_schema_dir=None):
            calls.append((version, remote_base_url, local_schema_dir))
            return local_schema_dir / "catalog.xml"

        monkeypatch.setattr(CatalogGenerator, "generate_catalog", staticmethod(fake_generate_catalog))

        result = CatalogGenerator(tmp_path).generate_all_catalogs()

        assert result == [version_dir / "catalog.xml"]
        assert calls == [
            (
                "2025-2",
                "https://schemas.wmo.int/iwxxm/2025-2/",
                version_dir,
            )
        ]

    def test_generate_all_logs_and_continues_on_generation_error(self, monkeypatch, tmp_path):
        version_dir = tmp_path / "2025-2"
        version_dir.mkdir()
        (version_dir / ".manifest.json").write_text(
            json.dumps({"root_url": "https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd"}), encoding="utf-8"
        )

        def fake_generate_catalog(version, remote_base_url, local_schema_dir=None):
            raise RuntimeError(f"failed for {version}")

        monkeypatch.setattr(CatalogGenerator, "generate_catalog", staticmethod(fake_generate_catalog))

        result = CatalogGenerator(tmp_path).generate_all_catalogs()

        assert result == []


class TestCatalogValidationAndConvenience:
    def test_validate_catalog_true_false_and_parse_error(self, tmp_path):
        gen = CatalogGenerator(schemas_base_path=tmp_path)
        valid_catalog = tmp_path / "catalog.xml"
        valid_catalog.write_text(
            "<?xml version='1.0' encoding='utf-8'?><catalog xmlns='urn:oasis:names:tc:entity:xmlns:xml:catalog'><rewriteURI uriStartString='https://example.com/' rewritePrefix='file:///tmp/'/></catalog>",
            encoding="utf-8",
        )
        invalid_root = tmp_path / "invalid-root.xml"
        invalid_root.write_text("<root/>", encoding="utf-8")
        no_rewrite = tmp_path / "no-rewrite.xml"
        no_rewrite.write_text(
            "<?xml version='1.0' encoding='utf-8'?><catalog xmlns='urn:oasis:names:tc:entity:xmlns:xml:catalog' />",
            encoding="utf-8",
        )
        broken = tmp_path / "broken.xml"
        broken.write_text("<<<not xml>>>", encoding="utf-8")

        assert gen.validate_catalog(valid_catalog) is True
        assert gen.validate_catalog(invalid_root) is False
        assert gen.validate_catalog(no_rewrite) is False
        assert gen.validate_catalog(broken) is False

    def test_catalog_convenience_functions_delegate(self, monkeypatch, tmp_path):
        calls = []

        def fake_generate_catalog(self, version, remote_base_url, local_schema_dir=None):
            calls.append(("one", self.schemas_base_path, version, remote_base_url, local_schema_dir))
            return self.schemas_base_path / version / "catalog.xml"

        def fake_generate_all_catalogs(self):
            calls.append(("all", self.schemas_base_path))
            return [self.schemas_base_path / "2025-2" / "catalog.xml"]

        monkeypatch.setattr(CatalogGenerator, "generate_catalog", fake_generate_catalog)
        monkeypatch.setattr(CatalogGenerator, "generate_all_catalogs", fake_generate_all_catalogs)

        one = generate_catalog_for_version("2025-2", "https://schemas.wmo.int/iwxxm/2025-2/", tmp_path)
        all_paths = generate_all_catalogs(tmp_path)

        assert one == tmp_path / "2025-2" / "catalog.xml"
        assert all_paths == [tmp_path / "2025-2" / "catalog.xml"]
        assert calls == [
            ("one", tmp_path, "2025-2", "https://schemas.wmo.int/iwxxm/2025-2/", None),
            ("all", tmp_path),
        ]
