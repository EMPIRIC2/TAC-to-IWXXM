# CORPUS parity note — S038 / EV-031 (T7.4)

> Protocol: [docs/CORPUS.md](../../../CORPUS.md) §Parity check protocol  
> Features: **F30**, **F31** (+ deepen F5/F7/F8/F21/F22/M4)

| Step | Check | Result |
|------|-------|--------|
| 1 Scope | Maps to feature-list F30/F31 | PASS |
| 2 Design | ADR-033 Accepted; spec/api Auth-only + DO Postgres + hybrid sessions | PASS |
| 3 Runtime | env-contract / deploy DOKS / `DATABASE_URL` product plane | PASS (TC-F30-006) |
| 4 Verification | test-plan TC-F30/F31/EV031; UJ-045..048; H4–H5 provisional | PASS (T7.1–T7.3) |
| 5 Decisions | `D-S038-*` + ADR-033; waive real DNS (`D-S038-t63-waive`) recorded | PASS |

**Cite**: `[Corpus: product]` F30/F31 · `[Corpus: adr]` ADR-033 · `[Corpus: tech-spec]` env-contract · `[Corpus: tests]` TC-F30/F31/EV031

Residual parity gap (explicit): production public DNS / HTTPS not yet corpus-pinned — provisional placeholders until waive lifts.
