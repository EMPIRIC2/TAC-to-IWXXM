"""Unit tests for schema mirror service helpers and integrity paths."""

from __future__ import annotations

import hashlib
import json

import pytest

from src.services.schema_mirror_service import SchemaMirrorService, mirror_schema_version


@pytest.mark.asyncio
async def test_mirror_version_writes_manifest_and_requests_optional_resources(monkeypatch, tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)
    calls = []
    lockfile_updates = []

    async def fake_download_xsd_tree(url, target_dir, manifest):
        calls.append(("xsd", url, target_dir.name))
        manifest["iwxxm.xsd"] = {
            "url": url,
            "sha256": "abc",
            "size_bytes": 3,
        }

    async def fake_download_directory(url, target_dir, manifest, skip_on_404=False):
        calls.append(("dir", url, target_dir.name, skip_on_404))

    async def fake_update_lockfile(version, manifest_data):
        lockfile_updates.append((version, manifest_data["resources"], manifest_data["base_url"]))

    monkeypatch.setattr(service, "_download_xsd_tree", fake_download_xsd_tree)
    monkeypatch.setattr(service, "_download_directory", fake_download_directory)
    monkeypatch.setattr(service, "_update_lockfile", fake_update_lockfile)

    result = await service.mirror_version(
        "2025-2",
        "https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd",
        include_examples=True,
        include_html=True,
        include_xmi=False,
    )

    manifest_path = tmp_path / "2025-2" / ".manifest.json"
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert result["files_mirrored"] == 1
    assert manifest_data["resources"] == {
        "schemas": True,
        "examples": True,
        "html": True,
        "xmi": False,
    }
    assert ("xsd", "https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd", "2025-2") in calls
    assert ("dir", "https://schemas.wmo.int/iwxxm/2025-2/examples/", "examples", False) in calls
    assert ("dir", "https://schemas.wmo.int/iwxxm/2025-2/html/", "html", True) in calls
    assert lockfile_updates == [
        (
            "2025-2",
            {"schemas": True, "examples": True, "html": True, "xmi": False},
            "https://schemas.wmo.int/iwxxm/2025-2/",
        )
    ]


@pytest.mark.asyncio
async def test_download_xsd_tree_writes_file_and_processes_imports(monkeypatch, tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)
    imports = []
    xsd_content = (
        b'<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"><xs:include schemaLocation="child.xsd"/></xs:schema>'
    )

    class _Response:
        status_code = 200
        content = xsd_content

        def raise_for_status(self):
            return None

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            return _Response()

    async def fake_process_xsd_imports(content, base_url, target_dir, manifest):
        imports.append((content, base_url, target_dir, dict(manifest)))

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())
    monkeypatch.setattr(service, "_process_xsd_imports", fake_process_xsd_imports)

    manifest = {}
    await service._download_xsd_tree(
        "https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd",
        tmp_path,
        manifest,
    )

    local_file = tmp_path / "iwxxm" / "2025-2" / "iwxxm.xsd"
    assert local_file.exists()
    assert manifest[str(local_file.relative_to(tmp_path))]["size_bytes"] == len(xsd_content)
    assert imports and imports[0][1] == "https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd"


@pytest.mark.asyncio
async def test_download_file_records_manifest_and_avoids_duplicate_download(monkeypatch, tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)
    service.current_version_dir = tmp_path / "2025-2"
    service.current_version_dir.mkdir()
    calls = []
    content = b"file-body"

    class _Response:
        def __init__(self):
            self.status_code = 200
            self.content = content

        def raise_for_status(self):
            return None

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            calls.append(url)
            return _Response()

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())

    manifest = {}
    url = "https://schemas.wmo.int/iwxxm/2025-2/examples/sample.xml"

    await service._download_file(url, service.current_version_dir / "examples", manifest)
    await service._download_file(url, service.current_version_dir / "examples", manifest)

    assert calls == [url]
    assert manifest["examples/sample.xml"] == {
        "url": url,
        "sha256": hashlib.sha256(content).hexdigest(),
        "size_bytes": len(content),
    }


@pytest.mark.asyncio
async def test_download_directory_skip_404_and_parse_error_handling(monkeypatch, tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)

    class _NotFoundResponse:
        status_code = 404
        text = ""

        def raise_for_status(self):
            raise AssertionError("should not be called for skip_on_404")

    class _BrokenResponse:
        status_code = 200
        text = None

        def raise_for_status(self):
            return None

    responses = [_NotFoundResponse(), _BrokenResponse()]

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            return responses.pop(0)

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())

    await service._download_directory("https://schemas.wmo.int/iwxxm/missing/", tmp_path, {}, skip_on_404=True)
    await service._download_directory("https://schemas.wmo.int/iwxxm/broken/", tmp_path, {}, skip_on_404=True)


@pytest.mark.asyncio
async def test_mirror_schema_version_convenience_function(monkeypatch, tmp_path):
    captured = {}

    async def fake_mirror_version(
        self, version, root_xsd_url, include_examples=True, include_html=True, include_xmi=True
    ):
        captured.update(
            {
                "base_path": self.base_path,
                "version": version,
                "root_xsd_url": root_xsd_url,
                "include_examples": include_examples,
                "include_html": include_html,
                "include_xmi": include_xmi,
            }
        )
        return {"version": version, "files_mirrored": 0}

    monkeypatch.setattr(SchemaMirrorService, "mirror_version", fake_mirror_version)

    result = await mirror_schema_version(
        "2025-2",
        "https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd",
        tmp_path,
        include_examples=False,
        include_html=False,
        include_xmi=True,
    )

    assert result == {"version": "2025-2", "files_mirrored": 0}
    assert captured == {
        "base_path": tmp_path,
        "version": "2025-2",
        "root_xsd_url": "https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd",
        "include_examples": False,
        "include_html": False,
        "include_xmi": True,
    }


@pytest.mark.asyncio
async def test_process_xsd_imports_resolves_relative_and_skips_external(monkeypatch, tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)
    calls = []

    async def fake_download(url, _target_dir, _manifest):
        calls.append(url)

    monkeypatch.setattr(service, "_download_xsd_tree", fake_download)

    xsd = """
    <xs:schema xmlns:xs=\"http://www.w3.org/2001/XMLSchema\">
      <xs:import schemaLocation=\"common.xsd\"/>
      <xs:include schemaLocation=\"https://schemas.wmo.int/iwxxm/rule.sch\"/>
      <xs:include schemaLocation=\"https://www.w3.org/2001/xml.xsd\"/>
    </xs:schema>
    """

    await service._process_xsd_imports(xsd, "https://schemas.wmo.int/iwxxm/2025-2/", tmp_path, {})

    assert "https://schemas.wmo.int/iwxxm/2025-2/common.xsd" in calls
    assert "https://schemas.wmo.int/iwxxm/rule.sch" in calls
    assert all("w3.org" not in url for url in calls)


@pytest.mark.asyncio
async def test_download_directory_parses_links_and_recurses(monkeypatch, tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)

    html = '<a href="file1.xsd">file1.xsd</a><a href="sub/">sub/</a><a href="../">../</a>'

    class _Response:
        status_code = 200
        text = html

        def raise_for_status(self):
            return None

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            return _Response()

    calls = {"files": [], "dirs": []}

    async def fake_download_file(url, _target_dir, _manifest):
        calls["files"].append(url)

    async def fake_download_dir(url, _target_dir, _manifest, skip_on_404=False):
        if url.endswith("sub/"):
            calls["dirs"].append(url)
            return
        await SchemaMirrorService._download_directory(service, url, _target_dir, _manifest, skip_on_404=skip_on_404)

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())
    monkeypatch.setattr(service, "_download_file", fake_download_file)
    monkeypatch.setattr(service, "_download_directory", fake_download_dir)

    await SchemaMirrorService._download_directory(
        service, "https://schemas.wmo.int/iwxxm/", tmp_path, {}, skip_on_404=False
    )

    assert "https://schemas.wmo.int/iwxxm/file1.xsd" in calls["files"]
    assert "https://schemas.wmo.int/iwxxm/sub/" in calls["dirs"]


@pytest.mark.asyncio
async def test_update_lockfile_and_verify_integrity(tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)

    version = "2025-2"
    version_dir = tmp_path / version
    version_dir.mkdir(parents=True)
    test_file = version_dir / "iwxxm.xsd"
    content = b"<xsd/>"
    test_file.write_bytes(content)

    sha = hashlib.sha256(content).hexdigest()

    manifest_data = {
        "version": version,
        "mirrored_at": "2026-01-01T00:00:00+00:00",
        "root_url": "https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd",
        "files": {
            "iwxxm.xsd": {
                "url": "https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd",
                "sha256": sha,
                "size_bytes": len(content),
            }
        },
    }

    (version_dir / ".manifest.json").write_text(json.dumps(manifest_data), encoding="utf-8")

    await service._update_lockfile(version, manifest_data)
    lock = json.loads((tmp_path / "schemas.lock.json").read_text(encoding="utf-8"))

    assert version in lock["versions"]
    assert await service.verify_integrity(version) is True

    test_file.write_bytes(b"<changed/>")
    assert await service.verify_integrity(version) is False


@pytest.mark.asyncio
async def test_verify_integrity_returns_false_when_manifest_or_file_missing(tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)

    assert await service.verify_integrity("2025-2") is False

    version_dir = tmp_path / "2025-2"
    version_dir.mkdir()
    manifest_data = {
        "files": {
            "missing.xsd": {
                "url": "https://schemas.wmo.int/iwxxm/2025-2/missing.xsd",
                "sha256": "abc",
                "size_bytes": 1,
            }
        }
    }
    (version_dir / ".manifest.json").write_text(json.dumps(manifest_data), encoding="utf-8")

    assert await service.verify_integrity("2025-2") is False


@pytest.mark.asyncio
async def test_mirror_version_downloads_xmi_directory(monkeypatch, tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)
    calls = []

    async def fake_download_xsd_tree(_url, _target_dir, manifest):
        manifest["iwxxm.xsd"] = {"url": _url, "sha256": "abc", "size_bytes": 1}

    async def fake_download_directory(url, target_dir, manifest, skip_on_404=False):
        calls.append((url, target_dir.name, skip_on_404))

    async def fake_update_lockfile(_version, _manifest_data):
        return None

    monkeypatch.setattr(service, "_download_xsd_tree", fake_download_xsd_tree)
    monkeypatch.setattr(service, "_download_directory", fake_download_directory)
    monkeypatch.setattr(service, "_update_lockfile", fake_update_lockfile)

    await service.mirror_version(
        "2025-2",
        "https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd",
        include_examples=False,
        include_html=False,
        include_xmi=True,
    )

    assert ("https://schemas.wmo.int/iwxxm/2025-2/XMI/", "XMI", True) in calls


@pytest.mark.asyncio
async def test_download_xsd_tree_skips_already_downloaded_url(monkeypatch, tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)
    service.downloaded_files.add("https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd")

    calls = {"count": 0}

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            calls["count"] += 1
            raise AssertionError("should not download duplicate url")

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())

    await service._download_xsd_tree("https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd", tmp_path, {})
    assert calls["count"] == 0


@pytest.mark.asyncio
async def test_download_xsd_tree_uses_filename_when_no_subdirectory(monkeypatch, tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)
    body = b"<xsd/>"

    class _Response:
        status_code = 200
        content = body

        def raise_for_status(self):
            return None

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            return _Response()

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())

    async def fake_process(*_args, **_kwargs):
        return None

    monkeypatch.setattr(service, "_process_xsd_imports", fake_process)

    manifest = {}
    await service._download_xsd_tree("https://example.test/iwxxm.xsd", tmp_path, manifest)

    assert (tmp_path / "iwxxm.xsd").exists()
    assert "iwxxm.xsd" in manifest


@pytest.mark.asyncio
async def test_download_xsd_tree_non_xsd_skips_import_processing(monkeypatch, tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)
    calls = []

    class _Response:
        status_code = 200
        content = b"not-an-xsd"

        def raise_for_status(self):
            return None

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            return _Response()

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())
    monkeypatch.setattr(service, "_process_xsd_imports", lambda *_args, **_kwargs: calls.append(True))

    await service._download_xsd_tree("https://example.test/readme.txt", tmp_path, {})

    assert calls == []


@pytest.mark.asyncio
async def test_download_xsd_tree_raises_on_http_error(monkeypatch, tmp_path):
    import httpx

    service = SchemaMirrorService(base_path=tmp_path)

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            request = httpx.Request("GET", "https://example.test/missing.xsd")
            response = httpx.Response(404, request=request)
            raise httpx.HTTPStatusError("missing", request=request, response=response)

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())

    with pytest.raises(httpx.HTTPStatusError):
        await service._download_xsd_tree("https://example.test/missing.xsd", tmp_path, {})


@pytest.mark.asyncio
async def test_download_file_uses_base_path_when_version_dir_unset(monkeypatch, tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)
    service.current_version_dir = None
    payload = b"payload"

    class _Response:
        status_code = 200
        content = payload

        def raise_for_status(self):
            return None

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            return _Response()

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())

    manifest = {}
    await service._download_file("https://example.test/sample.txt", tmp_path / "misc", manifest)

    assert any(key.endswith("sample.txt") for key in manifest)


@pytest.mark.asyncio
async def test_download_file_raises_on_http_error(monkeypatch, tmp_path):
    import httpx

    service = SchemaMirrorService(base_path=tmp_path)

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            request = httpx.Request("GET", "https://example.test/file.txt")
            response = httpx.Response(500, request=request)
            raise httpx.HTTPStatusError("server error", request=request, response=response)

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())

    with pytest.raises(httpx.HTTPStatusError):
        await service._download_file("https://example.test/file.txt", tmp_path, {})


@pytest.mark.asyncio
async def test_download_directory_raises_on_non_404_http_error(monkeypatch, tmp_path):
    import httpx

    service = SchemaMirrorService(base_path=tmp_path)

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            request = httpx.Request("GET", "https://example.test/dir/")
            response = httpx.Response(500, request=request)
            raise httpx.HTTPStatusError("server error", request=request, response=response)

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())

    with pytest.raises(httpx.HTTPStatusError):
        await service._download_directory("https://example.test/dir/", tmp_path, {}, skip_on_404=True)


@pytest.mark.asyncio
async def test_download_directory_raises_on_parse_error_when_not_skipping(monkeypatch, tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)

    class _BrokenResponse:
        status_code = 200

        @property
        def text(self):
            raise RuntimeError("cannot read body")

        def raise_for_status(self):
            return None

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            return _BrokenResponse()

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())

    with pytest.raises(RuntimeError, match="cannot read body"):
        await service._download_directory("https://example.test/dir/", tmp_path, {}, skip_on_404=False)


@pytest.mark.asyncio
async def test_update_lockfile_updates_existing_version(tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)
    lockfile_path = tmp_path / "schemas.lock.json"
    lockfile_path.write_text(
        json.dumps({"format_version": "1.0", "updated_at": "old", "versions": {"2025-2": {"file_count": 1}}}),
        encoding="utf-8",
    )

    manifest_data = {
        "mirrored_at": "2026-01-01T00:00:00+00:00",
        "root_url": "https://schemas.wmo.int/iwxxm/2025-2/iwxxm.xsd",
        "base_url": "https://schemas.wmo.int/iwxxm/2025-2/",
        "files": {"a.xsd": {}, "b.xsd": {}},
        "resources": {"schemas": True},
    }

    await service._update_lockfile("2025-2", manifest_data)
    lock = json.loads(lockfile_path.read_text(encoding="utf-8"))

    assert lock["versions"]["2025-2"]["file_count"] == 2
    assert lock["updated_at"] != "old"


@pytest.mark.asyncio
async def test_download_file_uses_base_path_fallback_on_relative_to_error(monkeypatch, tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)
    service.current_version_dir = tmp_path / "2025-2"
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()

    class _Response:
        status_code = 200
        content = b"payload"

        def raise_for_status(self):
            return None

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            return _Response()

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())

    manifest = {}
    await service._download_file("https://example.test/outside.txt", outside_dir, manifest)

    assert "outside/outside.txt" in manifest


@pytest.mark.asyncio
async def test_download_xsd_tree_uses_filename_when_path_has_no_slash(monkeypatch, tmp_path):
    service = SchemaMirrorService(base_path=tmp_path)

    class _Response:
        status_code = 200
        content = b"<xsd/>"

        def raise_for_status(self):
            return None

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            return _Response()

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())

    manifest = {}
    await service._download_xsd_tree("iwxxm.xsd", tmp_path, manifest)

    assert (tmp_path / "iwxxm.xsd").exists()
    assert "iwxxm.xsd" in manifest


@pytest.mark.asyncio
async def test_download_directory_skips_404_without_raising(monkeypatch, tmp_path, caplog):
    import logging

    import httpx

    caplog.set_level(logging.DEBUG, logger="src.services.schema_mirror_service")
    service = SchemaMirrorService(base_path=tmp_path)

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            request = httpx.Request("GET", "https://example.test/missing/")
            return httpx.Response(404, request=request)

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())

    await service._download_directory("https://example.test/missing/", tmp_path, {}, skip_on_404=True)

    assert "Directory not found (skipping)" in caplog.text


@pytest.mark.asyncio
async def test_download_directory_skips_404_http_status_error(monkeypatch, tmp_path, caplog):
    import logging

    import httpx

    caplog.set_level(logging.DEBUG, logger="src.services.schema_mirror_service")
    service = SchemaMirrorService(base_path=tmp_path)

    class _Client:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, _url):
            request = httpx.Request("GET", "https://example.test/missing/")
            response = httpx.Response(404, request=request)
            raise httpx.HTTPStatusError("missing", request=request, response=response)

    monkeypatch.setattr("src.services.schema_mirror_service.httpx.AsyncClient", lambda **_kwargs: _Client())

    await service._download_directory("https://example.test/missing/", tmp_path, {}, skip_on_404=True)

    assert "Directory not found (skipping)" in caplog.text
