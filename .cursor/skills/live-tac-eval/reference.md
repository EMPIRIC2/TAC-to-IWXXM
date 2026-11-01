# Live TAC eval — report templates

Copy into `sessions/<id>/reports/`. Replace placeholders. Keep JSON companions
with the same stem for machine reuse.

Agent/docs may cite `[Corpus: product]` / `[Corpus: tests]`. Do **not** paste
those cites into operator UI, OpenAPI, or HTTP `detail`.

---

## A. Lint code counts — `live-Nd-lint-code-counts.md`

```markdown
# Live API quality report — last Nd days

- API: `https://api.staging.tac-to-iwxxm.com`
- Source: `GET /api/v1/live-map` world bbox, products=<list>
- Window: `observed_at` ≥ <ISO-Z> (Nd label; live-map retention ~24h)
- Lint: `lint_with_profile(..., profile=annex3)` with ICAO station prefer
- Reports linted: <N> (places=<P>)
- Convert / IWXXM: <ran | skipped — reason>

## Severity (log level) totals

| Severity | Occurrences |
|----------|-------------|
| error | |
| warning | |
| info | |

## Codes × count × description

| Code | Severity | Count | Description |
|------|----------|-------|-------------|
| `CODE` | error | N | <registry / plain description> |

## Convert pass/fail (per lint code)

| Code | Convert OK | Convert fail | Fail rate |
|------|------------|--------------|-----------|
| `CODE` | | | |
| _(all reports)_ | | | |

## IWXXM validate pass/fail (per lint code)

| Code | Validate OK | Validate fail | Fail rate |
|------|-------------|---------------|-----------|
| `CODE` | | | |
| _(all reports)_ | | | |

## Region % of total (per code)

| Code | Region bucket | Occurrences | % of code total |
|------|---------------|-------------|-----------------|
| `CODE` | North America / Europe / … | | |

## Station / product rollups

See `live-Nd-warn-error-by-station.md` and product breakdown below.

### By product (warn+error)

| Code | Product | Count |
|------|---------|-------|
| `CODE` | metar | |
```

JSON stem: same fields as `relint_live_map.py` summary (`severity_totals`,
`codes[]`, plus optional `convert`, `iwxxm_validate`, `regions`).

---

## B. Warn/error by station — `live-Nd-warn-error-by-station.md`

```markdown
# Warn/error codes by station (live-map)

- API: `…`
- Window: observed_at ≥ `<ISO>` (Nd label; retention ~24h)
- Lint: `lint_with_profile` + ICAO prefer
- Reports linted: <N>

## `CODE` (severity) — <occ> occ / <places> places

Products: {metar: …, taf: …}

| Station | Occurrences |
|---------|-------------|
| `ICAO` | N |
```

---

## C. Promote disposition — `live-Nd-promote-disposition.md`

```markdown
# Live-map remaining warn/error codes — disposition

- Tallies: `reports/live-Nd-lint-code-counts.json`
- Locale / region: `reports/…` (if present)
- Lint path: prefer-resolved (`lint_with_profile`)
- [Corpus: product] [Corpus: tests]

## Action legend

`keep-as-error` · `leave` · `profile-remap` · `national-prefer` ·
`product-rule-fix` · `bug-ticket` · `defer` · `soft-only-if-MISG-or-solidi`

## Per-code dispositions

### `CODE` — severity · products · occ / places

| Field | Content |
|-------|---------|
| **Locales** | region % + example stations |
| **Why** | dialect / source quality / true defect |
| **Convert / IWXXM** | OK/fail rates for reports carrying this code |
| **Action** | leave \| profile \| product-rule \| … |
| **Constraints check** | no Europe blanket; no MISSING_* / CW* VIS-QNH soften; INVALID_PROB kept |
| **Priority** | P1–P3 |
| **Next step** | ticket / ADR / monitor |

## Summary table

| Code | Action | Priority | Notes |
|------|--------|----------|-------|
| `CODE` | keep-as-error | P2 | |
```

### Disposition decision checklist

```
For each code:
- [ ] Station/region consistency measured (% + unique places)
- [ ] Sample TAC captured (or noted aged-out of cache)
- [ ] Literature / domain canonical checked if proposing remap
- [ ] Disposition ∈ leave | profile | product-rule (+ bug/defer)
- [ ] Constraints: no Europe blanket; no MISSING_* soften; no CW* VIS/QNH
      soften; keep INVALID_PROB unless ADR says otherwise
- [ ] Convert + IWXXM fail rates recorded (or N/A with reason)
```

---

## D. Minimal JSON shape (optional machine companion)

```json
{
  "api": "https://api.staging.tac-to-iwxxm.com",
  "window_days": 7,
  "cutoff_utc": "",
  "generated_at": "",
  "prefer": true,
  "reports_in_window": 0,
  "severity_totals": {"error": 0, "warning": 0, "info": 0},
  "codes": [
    {
      "code": "MISSING_VISIBILITY",
      "severity": "error",
      "count": 0,
      "description": "",
      "convert_ok": 0,
      "convert_fail": 0,
      "iwxxm_ok": 0,
      "iwxxm_fail": 0,
      "regions": [{"bucket": "North America", "count": 0, "pct": 0.0}],
      "by_product": {"metar": 0},
      "stations": [{"place_key": "KHLC", "occurrences": 0}]
    }
  ]
}
```

---

## E. Script reuse map

| Need | Prefer |
|------|--------|
| Fetch live-map + lint tallies | `EV-regional-dialect-profiles/evidence/relint_live_map.py` |
| Station TAC samples | `…/evidence/locale_reasoning_sampler.py` |
| Municipality / country | `…/evidence/resolve_municipalities.py` |
| Convert | `POST /api/v1/convert` or `tac2iwxxm` local |
| IWXXM validate | `iwxxm-validate` package or validation router |

Do not commit large TAC dumps to the product git tree; keep under session
`evidence/` / `reports/`.
