# Bug report: dissemination missing sink_type returns 501

**ID:** BUG-2026-09-09-dissemination-missing-sink-type-501  
**Date:** 2026-09-09  
**PR:** pending  
**Session:** HF-adv-sink-type-title-sanitize  
**Source:** EV-staging-adversarial-e2e F-ADV-01

## Error description

`POST /api/v1/dissemination/preflight` and `/send` return HTTP **501** with
`sink_type None not implemented in this milestone` when `sink_type` is omitted or
null (and send has no preflight handle). Clients should get **422** for a missing
required field; **501** is reserved for known-but-unimplemented sink types.

## Error logs

```text
POST https://api.staging.tac-to-iwxxm.com/api/v1/dissemination/preflight
HTTP 501
{"detail":"sink_type None not implemented in this milestone"}

POST https://api.staging.tac-to-iwxxm.com/api/v1/dissemination/send
HTTP 501
{"detail":"sink_type None not implemented in this milestone"}
```

Evidence: `EV-staging-adversarial-e2e/evidence/03-adversarial-console.log`
(`ssrf_preflight_0` … `ssrf_send_3`).

## Investigation

1. Router treats `sink_type not in _DB_SINKS` as 501; `None` is not in the set.
2. `SendRequest.sink_type` is optional (`None` default) for handle-based send.
3. Prefer 422 when `sink_type` is missing/`None` and no handle supplied the type.

**Root cause:** Missing/`None` sink_type conflated with unimplemented sink types.

## Repro test

- Path: `tests/bugs/test_bug_2026_09_09_dissemination_missing_sink_type_501.py`
- Status: green

## Fix

Short-circuit `None`/missing `sink_type` to HTTP 422 before the unimplemented-sink 501 branch.
Keep 501 for values like `wis2`.

## Interview record

- Operator asked to proceed with F-ADV-01/02 polish after staging adversarial plunge held.
- Severity: Info / soft advisory (not critical).
