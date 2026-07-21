# wis2box Compose harness (F17 / T3.3)

Lightweight **test harness** for TC-F17-001 — MQTT broker + HTTP dataset PUT/GET.
Not a long-lived Render service (E14-04=B). Not the full WMO wis2box release stack.

| Surface | Port (container) | Host default                    |
| ------- | ---------------- | ------------------------------- |
| MQTT    | 1883             | `WIS2BOX_MQTT_HOST_PORT` (1883) |
| HTTP    | 8080             | `WIS2BOX_HTTP_HOST_PORT` (9080) |

```bash
# from repo root
make compose-wis2box-up
curl -s http://127.0.0.1:9080/health
make compose-wis2box-harness   # CI hook (up + probe + optional wis2* pytest)
make compose-wis2box-down
```

Allowlist Compose/CI hosts when exercising the sink (ADR-029), e.g.
`DISSEMINATION_EGRESS_ALLOWLIST=wis2box,127.0.0.1,localhost`.
