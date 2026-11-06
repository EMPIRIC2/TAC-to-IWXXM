# Documentation

Install and run the project with [ops/DEVELOPMENT.md](ops/DEVELOPMENT.md).

## Public user guide (Read the Docs format)

Operator and integrator documentation lives in [`user-docs/`](../user-docs/)
(MkDocs, Read the Docs theme, ASD-STE100 prose). Build locally:

```bash
pip install mkdocs
cd user-docs && mkdocs serve
```

Cross-page links point at the
[GitHub Wiki](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki). Optional Read the
Docs mirror: [user-docs/READTHEDOCS.md](../user-docs/READTHEDOCS.md) (project
must be created on Read the Docs; none existed yet for slug `tac-to-iwxxm`).
This site is **not** the engineering HTTP contract; use
[api-contract.md](api-contract.md) and live OpenAPI for field-level API truth.

## Operators (short sheets)

Operators who turn aviation weather text into IWXXM day to day:

- [One-pager](guides/operator-one-pager.md) — one printed sheet
- [Handbook](guides/operator-handbook.md) — sign-in, workbench use, history, troubleshooting

## HTTP API

HTTP reference index: [guides/API.md](guides/API.md).

## Deploy

Deploy and connectivity: [deploy.md](deploy.md).

## Release notes

Release notes: [CHANGELOG.md](CHANGELOG.md).
