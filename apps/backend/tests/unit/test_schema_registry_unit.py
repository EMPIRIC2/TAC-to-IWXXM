"""Unit tests for schema registry helpers."""

from src.utilities import schema_registry as registry_module


def test_registry_singleton_and_supported_versions() -> None:
    registry_module._registry_instance = None

    first = registry_module.get_schema_registry()
    second = registry_module.get_schema_registry()

    assert first is second
    assert "2025-2" in first.get_supported_versions()


def test_get_xsd_schematron_and_codelists_paths_cached(monkeypatch, tmp_path) -> None:
    registry = registry_module.SchemaRegistry()
    calls = {"count": 0}

    def fake_resolve(version, file_type):
        calls["count"] += 1
        return tmp_path / version / file_type

    monkeypatch.setattr(registry_module, "normalize_version", lambda v: v)
    monkeypatch.setattr(registry_module, "resolve_schema_file", fake_resolve)

    first = registry.get_xsd_path("2025-2")
    second = registry.get_xsd_path("2025-2")
    sch = registry.get_schematron_path("2025-2")
    code = registry.get_codelists_dir("2025-2")

    assert first == second
    assert calls["count"] == 3
    assert sch.name == "schematron"
    assert code.name == "codelists"


def test_registry_file_cache_short_circuits_lru_resolution(tmp_path) -> None:
    registry = registry_module.SchemaRegistry()

    xsd_path = tmp_path / "xsd.xsd"
    schematron_path = tmp_path / "rules.sch"
    codelists_path = tmp_path / "codelists"

    registry._file_cache["xsd_2025-2"] = xsd_path
    registry._file_cache["schematron_2025-2"] = schematron_path
    registry._file_cache["codelists_2025-2"] = codelists_path

    assert registry.get_xsd_path("2025-2") == xsd_path
    assert registry.get_schematron_path("2025-2") == schematron_path
    assert registry.get_codelists_dir("2025-2") == codelists_path


def test_version_info_passthrough_helpers(monkeypatch) -> None:
    registry = registry_module.SchemaRegistry()

    monkeypatch.setattr(registry_module, "normalize_version", lambda _: "normalized")
    monkeypatch.setattr(registry_module, "get_namespace_uri", lambda v: f"ns:{v}")
    monkeypatch.setattr(registry_module, "get_schema_url", lambda v: f"url:{v}")
    monkeypatch.setattr(registry_module, "get_version_config", lambda v: {"v": v})
    monkeypatch.setattr(registry_module, "get_breaking_changes", lambda a, b: [{"from": a, "to": b}])
    monkeypatch.setattr(registry_module, "get_versions_by_channel", lambda c: [f"{c}-1"])
    monkeypatch.setattr(registry_module, "is_rc_version", lambda v: v.endswith("RC1"))
    monkeypatch.setattr(registry_module, "get_version_channel", lambda v: "rc" if v.endswith("RC1") else "stable")
    monkeypatch.setattr(registry_module, "get_version_discovery_date", lambda _: "2025-01-01T00:00:00Z")
    monkeypatch.setattr(registry_module, "get_all_versions_with_metadata", lambda: {"k": "v"})

    assert registry.get_namespace_uri("2025-2") == "ns:normalized"
    assert registry.get_schema_url("2025-2") == "url:normalized"
    assert registry.get_version_info("2025-2") == {"v": "normalized"}
    assert registry.get_breaking_changes("2023-1", "2025-2") == [{"from": "2023-1", "to": "2025-2"}]
    assert registry.get_all_versions("stable") == ["stable-1"]
    assert registry.is_rc_version("2025-2RC1") is True
    assert registry.get_version_channel("2025-2RC1") == "rc"
    assert registry.get_version_discovery_date("2025-2") == "2025-01-01T00:00:00Z"
    assert registry.get_all_versions_with_metadata() == {"k": "v"}


def test_list_codelists_sorts_names(tmp_path, monkeypatch) -> None:
    codelists = tmp_path / "code"
    codelists.mkdir(parents=True)
    (codelists / "b.rdf").write_text("", encoding="utf-8")
    (codelists / "a.rdf").write_text("", encoding="utf-8")
    (codelists / "ignored.txt").write_text("", encoding="utf-8")

    registry = registry_module.SchemaRegistry()
    monkeypatch.setattr(registry, "get_codelists_dir", lambda _version: codelists)

    assert registry.list_codelists("2025-2") == ["a.rdf", "b.rdf"]


def test_get_catalog_path_returns_expected_location(monkeypatch, tmp_path) -> None:
    registry = registry_module.SchemaRegistry()
    version_dir = tmp_path / "2025-2" / "IWXXM"
    version_dir.mkdir(parents=True)

    monkeypatch.setattr(registry_module, "normalize_version", lambda v: v)
    monkeypatch.setattr(registry_module, "get_version_config", lambda _v: {"local_schema_base": version_dir})

    catalog = registry.get_catalog_path("2025-2")

    assert catalog == version_dir.parent / "catalog.xml"


def test_get_catalog_path_returns_missing_catalog_path(monkeypatch, tmp_path) -> None:
    registry = registry_module.SchemaRegistry()
    version_dir = tmp_path / "2025-2" / "IWXXM"
    version_dir.mkdir(parents=True)

    monkeypatch.setattr(registry_module, "normalize_version", lambda v: v)
    monkeypatch.setattr(registry_module, "get_version_config", lambda _v: {"local_schema_base": version_dir})

    catalog = registry.get_catalog_path("2025-2")

    assert catalog.exists() is False
    assert catalog.name == "catalog.xml"


def test_get_catalog_path_existing_catalog_avoids_warning_branch(monkeypatch, tmp_path) -> None:
    registry = registry_module.SchemaRegistry()
    version_dir = tmp_path / "2025-2" / "IWXXM"
    version_dir.mkdir(parents=True)
    existing_catalog = version_dir.parent / "catalog.xml"
    existing_catalog.write_text("<catalog/>", encoding="utf-8")

    monkeypatch.setattr(registry_module, "normalize_version", lambda v: v)
    monkeypatch.setattr(registry_module, "get_version_config", lambda _v: {"local_schema_base": version_dir})

    catalog = registry.get_catalog_path("2025-2")

    assert catalog == existing_catalog
    assert catalog.exists() is True


def test_verify_schema_integrity_manifest_and_xsd_checks(monkeypatch, tmp_path) -> None:
    registry = registry_module.SchemaRegistry()
    version_dir = tmp_path / "2025-2" / "IWXXM"
    version_dir.mkdir(parents=True)

    monkeypatch.setattr(registry_module, "normalize_version", lambda v: v)
    monkeypatch.setattr(registry_module, "get_version_config", lambda _v: {"local_schema_base": version_dir})

    # Missing manifest should fail.
    assert registry.verify_schema_integrity("2025-2") is False

    manifest = version_dir.parent / ".manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    xsd = version_dir / "iwxxm.xsd"
    xsd.write_text("<xsd:schema/>", encoding="utf-8")
    monkeypatch.setattr(registry, "get_xsd_path", lambda _v: xsd)

    assert registry.verify_schema_integrity("2025-2") is True


def test_verify_schema_integrity_handles_exceptions(monkeypatch) -> None:
    registry = registry_module.SchemaRegistry()
    monkeypatch.setattr(registry_module, "normalize_version", lambda _v: (_ for _ in ()).throw(RuntimeError("boom")))

    assert registry.verify_schema_integrity("2025-2") is False


def test_clear_registry_cache_resets_method_caches(monkeypatch, tmp_path) -> None:
    registry = registry_module.SchemaRegistry()
    registry_module._registry_instance = registry

    path = tmp_path / "2025-2" / "xsd"
    monkeypatch.setattr(registry_module, "normalize_version", lambda v: v)
    monkeypatch.setattr(registry_module, "resolve_schema_file", lambda _v, _t: path)

    _ = registry.get_xsd_path("2025-2")
    assert registry._file_cache

    registry_module.clear_registry_cache()

    assert registry._file_cache == {}


def test_clear_registry_cache_without_singleton_is_noop() -> None:
    registry_module._registry_instance = None

    registry_module.clear_registry_cache()

    assert registry_module._registry_instance is None
