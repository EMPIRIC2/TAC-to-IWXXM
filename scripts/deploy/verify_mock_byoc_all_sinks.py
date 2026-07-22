#!/usr/bin/env python3
"""Verify preflight+send for every DisseminationDrawer sink against local mocks."""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen

from dissemination.allowlist import parse_allowlist
from dissemination.db_preflight import (
    dialect_for_sink,
    normalize_sqlalchemy_uri,
    run_db_preflight,
)
from dissemination.edis import EdisParams, edis_preflight, edis_submit
from dissemination.f19_stubs import F19Params, get_staging_sink
from dissemination.models import PreflightRequest
from dissemination.odbc import odbc_sqlserver_available, preferred_sqlserver_odbc_driver
from dissemination.transports import AiomqttClient, AiosmtpClient, HttpxDatasetClient
from dissemination.wis2 import Wis2Params, wis2_preflight, wis2_publish
from dissemination.writer_contract import CONTRACT_TABLE, apply_writer_contract
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = json.loads(
    (
        ROOT
        / "docs/sessions/S019-dissemination-upload/fixtures/mock-byoc-destinations.json"
    ).read_text(encoding="utf-8")
)
IWXXM = (
    ROOT
    / "docs/sessions/S019-dissemination-upload/fixtures/byoc-test-candidates/sample-metar.iwxxm.xml"
).read_text(encoding="utf-8")
TAC = (
    (
        ROOT
        / "docs/sessions/S019-dissemination-upload/fixtures/byoc-test-candidates/sample-metar.tac"
    )
    .read_text(encoding="utf-8")
    .strip()
)
ALLOW = parse_allowlist("wis2box,127.0.0.1,127.0.0.0/8,localhost")
RESULTS: list[tuple[str, str, str]] = []


def _record(sink: str, status: str, detail: str = "") -> None:
    RESULTS.append((sink, status, detail))
    print(f"  [{status}] {sink}" + (f" — {detail}" if detail else ""))


def _with_odbc_driver(url: str) -> str:
    driver = preferred_sqlserver_odbc_driver()
    if driver is None:
        return url
    parsed = urlparse(url)
    q = dict(parse_qsl(parsed.query, keep_blank_values=True))
    q.setdefault("driver", driver)
    q.setdefault("TrustServerCertificate", "yes")
    return urlunparse(parsed._replace(query=urlencode(q)))


async def _verify_db(key: str, *, uri_override: str | None = None) -> None:
    row = FIXTURES[key]
    sink = row["sink_type"]
    uri = uri_override or row["uri"]
    pre = await run_db_preflight(
        PreflightRequest(sink_type=sink, uri=uri, ddl=True, product="metar")
    )
    assert pre.ok and pre.connectivity_ok and pre.diffs == [], pre
    dialect = dialect_for_sink(sink)
    engine = create_async_engine(normalize_sqlalchemy_uri(uri, sink))
    upload_key = f"kv_mock_{uuid.uuid4().hex[:12]}"
    try:
        await apply_writer_contract(engine, dialect=dialect)
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    f"INSERT INTO {CONTRACT_TABLE} "
                    "(id, product, icao, observation_time, iwxxm_version, iwxxm_xml, "
                    "tac_text, upload_key) "
                    "VALUES (:id, :product, :icao, :observation_time, :iwxxm_version, "
                    ":iwxxm_xml, :tac_text, :upload_key)"
                ),
                {
                    "id": str(uuid.uuid4()),
                    "product": "metar",
                    "icao": "KJFK",
                    "observation_time": datetime(2026, 7, 21, 17, 51, tzinfo=UTC),
                    "iwxxm_version": "2025-2",
                    "iwxxm_xml": IWXXM,
                    "tac_text": TAC,
                    "upload_key": upload_key,
                },
            )
            n = (
                await conn.execute(
                    text(
                        f"SELECT COUNT(*) FROM {CONTRACT_TABLE} WHERE upload_key = :k"
                    ),
                    {"k": upload_key},
                )
            ).scalar_one()
        assert n == 1
        _record(sink, "PASS", f"upload_key={upload_key}")
    finally:
        await engine.dispose()


async def verify_sqlite() -> None:
    print("\n=== sqlite ===")
    db = ROOT / "tmp" / "mock-byoc-all-sinks.db"
    db.parent.mkdir(parents=True, exist_ok=True)
    if db.exists():
        db.unlink()
    uri = f"sqlite+aiosqlite:///{db}"
    await _verify_db("postgres_sqlite_standin", uri_override=uri)


async def verify_postgres() -> None:
    print("\n=== postgres ===")
    await _verify_db("postgres_compose")


async def verify_mysql() -> None:
    print("\n=== mysql ===")
    await _verify_db("mysql_compose")


async def verify_sqlserver() -> None:
    print("\n=== sqlserver ===")
    if not odbc_sqlserver_available():
        _record("sqlserver", "SKIP", "ODBC SQL Server driver not installed")
        return
    uri = _with_odbc_driver(FIXTURES["sqlserver_compose"]["uri"])
    await _verify_db("sqlserver_compose", uri_override=uri)


async def verify_wis2() -> None:
    print("\n=== wis2 ===")
    raw = FIXTURES["wis2_compose_host"]["params"]
    params = Wis2Params(
        mqtt_host=raw["mqtt_host"],
        mqtt_port=int(raw["mqtt_port"]),
        mqtt_topic=raw["mqtt_topic"],
        dataset_url=raw["dataset_url"],
        centre_id=raw["centre_id"],
        mqtt_username=None,
        mqtt_password=None,
        use_tls=False,
    )
    mqtt = AiomqttClient(host=params.mqtt_host, port=params.mqtt_port)
    http = HttpxDatasetClient()
    pre = await wis2_preflight(params, allowlist=ALLOW, mqtt=mqtt, http=http)
    assert pre.ok and pre.connectivity_ok, pre
    mqtt2 = AiomqttClient(host=params.mqtt_host, port=params.mqtt_port)
    pub = await wis2_publish(
        params,
        iwxxm_xml=IWXXM,
        allowlist=ALLOW,
        mqtt=mqtt2,
        http=http,
    )
    assert pub.ok, pub
    body = await http.get_dataset(params.dataset_url)
    assert b"METAR" in body or b"iwxxm" in body.lower()
    _record("wis2", "PASS", f"dataset={params.dataset_url}")


async def verify_edis() -> None:
    print("\n=== edis ===")
    raw = FIXTURES["edis_mailhog"]["params"]
    params = EdisParams(
        smtp_host=raw["smtp_host"],
        smtp_port=int(raw["smtp_port"]),
        mail_from=raw["mail_from"],
        mail_to=raw["mail_to"],
        username=None,
        password=None,
        use_tls=False,
        tt=raw["tt"],
        aa=raw["aa"],
        ii=raw["ii"],
        cccc=raw["cccc"],
        yygggg=raw["yygggg"],
    )
    smtp = AiosmtpClient(
        hostname=params.smtp_host, port=params.smtp_port, use_tls=False
    )
    pre = await edis_preflight(params, allowlist=ALLOW, smtp=smtp)
    assert pre.ok, pre
    before = json.loads(urlopen("http://127.0.0.1:18025/api/v2/messages").read())[
        "total"
    ]
    smtp2 = AiosmtpClient(
        hostname=params.smtp_host, port=params.smtp_port, use_tls=False
    )
    sub = await edis_submit(params, tac_body=TAC, allowlist=ALLOW, smtp=smtp2)
    assert sub.ok, sub
    after = json.loads(urlopen("http://127.0.0.1:18025/api/v2/messages").read())[
        "total"
    ]
    assert after == before + 1
    _record("edis", "PASS", f"ahl={sub.ahl}")


async def verify_f19(sink: str) -> None:
    print(f"\n=== {sink} ===")
    raw = FIXTURES["f19_compose"]["params_by_sink"][sink]
    # Package staging stub (allowlist + contract)
    adapter = get_staging_sink(sink)
    params = F19Params(
        sink_type=sink,  # type: ignore[arg-type]
        host=raw["host"],
        port=int(raw["port"]),
        username=raw.get("username"),
        password=raw.get("password"),
        endpoint=raw.get("endpoint"),
    )
    pre = await adapter.preflight(params=params, allowlist=ALLOW)
    assert pre.ok and pre.connectivity_ok, pre
    stub = await adapter.send(params=params, allowlist=ALLOW, iwxxm_xml=IWXXM)
    assert stub.ok and stub.kv_upload_key, stub

    # HTTP mock harness receive (real mock destination)
    url = f"http://{raw['host']}:{raw['port']}{raw['endpoint']}"
    req = Request(url, data=IWXXM.encode("utf-8"), method="POST")
    req.add_header("Content-Type", "application/xml")
    with urlopen(req, timeout=10) as resp:
        payload = json.loads(resp.read())
    assert resp.status == 201 and payload.get("ok") is True, payload
    _record(
        sink, "PASS", f"stub={stub.kv_upload_key} harness={payload['kv_upload_key']}"
    )


async def main() -> None:
    print("Mock BYOC all-sinks verification")
    await verify_sqlite()
    await verify_postgres()
    await verify_mysql()
    await verify_sqlserver()
    await verify_wis2()
    await verify_edis()
    for sink in ("amhs", "swim", "afs"):
        await verify_f19(sink)

    print("\n=== SUMMARY ===")
    fails = 0
    for sink, status, detail in RESULTS:
        line = f"{status:4}  {sink}"
        if detail:
            line += f"  ({detail})"
        print(line)
        if status == "FAIL":
            fails += 1
    passed = sum(1 for _, s, _ in RESULTS if s == "PASS")
    skipped = sum(1 for _, s, _ in RESULTS if s == "SKIP")
    print(f"\npassed={passed} skipped={skipped} failed={fails} total={len(RESULTS)}")
    if fails:
        raise SystemExit(1)
    # Require every drawer sink covered
    covered = {s for s, _, _ in RESULTS}
    expected = {
        "sqlite",
        "postgres",
        "mysql",
        "sqlserver",
        "wis2",
        "edis",
        "amhs",
        "swim",
        "afs",
    }
    missing = expected - covered
    if missing:
        raise SystemExit(f"missing sinks in report: {sorted(missing)}")


if __name__ == "__main__":
    asyncio.run(main())
