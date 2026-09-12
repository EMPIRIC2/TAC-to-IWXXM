# BUG-2026-09-12 — Staging adversarial load findings (F-ADV-LOAD-01/02/03)

**Status:** fixed (branch `fix/staging-adv-load-findings`)  
**Source:** EV-staging-adv-load-e2e  
**Corpus:** [Corpus: tests] [Corpus: deploy] [Corpus: api]

## Error description

1. **F-ADV-LOAD-01** — Locust 15 users / 3 min against staging produced intermittent **502** (0.45%). Single API replica + default ingress timeouts.
2. **F-ADV-LOAD-02** — `apps/backend/tests/load/locustfile.py` registered no Locust User classes → `No User class found!`.
3. **F-ADV-LOAD-03** — `POST /api/v1/validation/validate` ignored `content_type` / `layers` and always ran TAC ICAO/syntax on the body (XML looked like ICAO `HTTP`).

## Error logs

```
Error report
1  GET /api/v1/translation/centre-info: 502
3  POST /api/v1/convert: Unexpected status 502
2  POST /api/v1/validation/validate: Unexpected status 502

[locust] No User class found!

{"name":"validate_xml_schema","status":200,"snip":"...Unknown ICAO code: HTTP...layers_validated\":[\"airport_icao\",\"tac_syntax\"]..."}
```

## Investigation

| Finding | Root cause |
|---------|------------|
| 502 | Staging `metar-api` at 1 replica with tight memory; nginx default upstream timeout |
| Locust | Entrypoint imported metrics/config only — scenarios User classes never loaded |
| Validate | Router always called `validate_all_layers(tac_text=request.content)` |

## Repro test

`tests/bugs/test_bug_2026_09_12_staging_adv_load_findings.py` (+ router unit tests)

## Fix

- Locust: import User classes from `tests.load.scenarios`
- Validation router: honor `content_type` (`tac`|`xml`|`iwxxm`) and `layers`; XML → orchestrator
- Staging DOKS: API `replicas: 2`, raised memory requests/limits; ingress proxy timeouts 120s
