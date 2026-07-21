# dissemination

MIT package for F16–F19 operator dissemination: multi-DB writer-contract, WIS2/EDIS/AMHS
sink adapters, and SSRF/allowlist helpers ([ADR-030](../../docs/adr/ADR-030-dissemination-package-architecture.md)).

**Boundaries**

- No FastAPI or Supabase imports
- HTTP routers stay in `apps/backend` (thin)

**Coverage**

- Local/CI: `make test-unit-dissemination` (95% branch gate)

**Multi-DB integration (T2.5 / TC-F16-003)**

- `pytest packages/dissemination/tests/test_writer_contract_engines.py -m integration`
- Postgres + MySQL via Testcontainers (requires Docker); SQLite in-process
- Without Docker, PG/MySQL cases skip; SQLite still runs

**Egress allowlist**

- Env: `DISSEMINATION_EGRESS_ALLOWLIST` (see `.env.example`, ADR-029)
- Empty ⇒ fail-closed
- Compose wis2box harness: `make compose-wis2box-up` / `compose-wis2box-harness` (T3.3 fills service)
