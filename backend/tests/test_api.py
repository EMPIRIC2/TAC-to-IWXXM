from backend.api import app
import io
import zipfile
import sys
import pathlib
from fastapi.testclient import TestClient

# Ensure src layout path precedence for imports
ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_SRC = ROOT / "backend" / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))


client = TestClient(app)

SAMPLE_METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
SAMPLE_METAR_2 = "METAR KLAX 231753Z 25008KT 10SM FEW020 18/12 A2992"


def test_health_status():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in {"healthy", "degraded"}
    assert "version" in data
    assert isinstance(data["gifts_available"], bool)


def test_manual_conversion():
    r = client.post("/api/convert", data={"manual_text": SAMPLE_METAR})
    assert r.status_code == 200
    data = r.json()
    assert data["successful"] == 1
    assert data["failed"] == 0
    assert len(data["results"]) == 1
    content = data["results"][0]["content"]
    assert "<iwxxm:METAR" in content


def test_multiple_files_conversion():
    files = [
        ("files", ("m1.tac", SAMPLE_METAR, "text/plain")),
        ("files", ("m2.tac", SAMPLE_METAR_2, "text/plain")),
    ]
    r = client.post("/api/convert", files=files)
    assert r.status_code == 200
    data = r.json()
    assert data["successful"] == 2
    assert data["failed"] == 0
    assert len(data["results"]) == 2


def test_error_empty_files():
    files = [
        ("files", ("empty1.tac", "", "text/plain")),
        ("files", ("empty2.tac", "", "text/plain")),
    ]
    r = client.post("/api/convert", files=files)
    assert r.status_code == 400
    detail = r.json()
    assert "detail" in detail
    assert detail["detail"]["total_errors"] == 2


def test_zip_conversion():
    files = [
        ("files", ("m1.tac", SAMPLE_METAR, "text/plain")),
        ("files", ("m2.tac", SAMPLE_METAR_2, "text/plain")),
    ]
    r = client.post("/api/convert-zip", files=files)
    assert r.status_code == 200
    assert r.headers.get("content-type") == "application/zip"
    zbytes = io.BytesIO(r.content)
    with zipfile.ZipFile(zbytes) as zf:
        names = set(zf.namelist())
        assert any(n.endswith(".xml") for n in names)
        xml_files = [n for n in names if n.endswith(".xml")]
        assert len(xml_files) >= 2
