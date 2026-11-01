---
name: live-tac-eval
description: >-
  Runs date-range live TAC evaluation against the live API: lint code counts,
  convert OK/fail per code, IWXXM validate OK/fail, region percentage
  breakdowns, and promote/leave recommendations. Use when the user asks for a
  live eval, date-range lint report, 7d/Nd validation analysis, or
  promote-issue analysis from live traffic.
disable-model-invocation: false
---

# Live TAC evaluation (date-range)

[Corpus: product] [Corpus: tests]

Read-only probe of staging/prod live traffic → lint → convert → IWXXM validate →
aggregate → promote/leave recommendations. **Do not** put corpus cites, ADR/EV
ids, or session paths on operator/public surfaces
([`no-internal-doc-refs-user-facing.mdc`](../../rules/core/no-internal-doc-refs-user-facing.mdc)).

## When to use

- Live eval / date-range lint report / 7d or Nd validation analysis
- Promote-issue analysis from live traffic (leave vs profile vs product-rule)

## 1. Intake

Confirm (defaults in parentheses):

| Field | Default / notes |
|-------|-----------------|
| **Date range** | `7d` (`--window-days 7`); label only — live-map retention is ~24h |
| **API** | `https://api.staging.tac-to-iwxxm.com` (override if user names prod) |
| **Data root** | Reuse EV-regional-dialect-profiles live-map path (see below) |
| **Products filter** | All `MAP_PRODUCTS`, or subset (metar/speci/taf/sigmet/…) |
| **Prefer profiles** | **On** — always `lint_with_profile(..., profile=annex3, icao=<place_key>)` |

**Data root (reuse):**

```
~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-regional-dialect-profiles/
```

- Scripts: `evidence/relint_live_map.py`, `evidence/locale_reasoning_sampler.py`,
  `evidence/resolve_municipalities.py`
- Prior tallies: `reports/live-7d-*.md` / `.json`

**Active session output root:**

```
~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/<id>/reports/
```

Copy or symlink prior JSON under the active session when reusing; do not rewrite
the EV-regional-dialect-profiles tree unless that session is the active one.

## 2. Pipeline

```
- [ ] 1. Fetch or reuse live TAC (GET /api/v1/live-map world bbox)
- [ ] 2. Filter by observed_at ≥ cutoff and products
- [ ] 3. lint_with_profile (annex3 + ICAO prefer) — never bare lint for tallies
- [ ] 4. Convert (POST /api/v1/convert or local tac2iwxxm) → OK/fail per report
- [ ] 5. IWXXM validate (package or /api/v1/validation/validate on XML) → OK/fail
- [ ] 6. Aggregate codes, regions, stations, products
- [ ] 7. Promote analysis → write reports under sessions/<id>/reports/
```

### Reuse first

Prefer extending `evidence/relint_live_map.py` (fetch + lint tallies) rather than
rewriting fetch. Add convert/validate passes as a thin follow-on script in the
**active** session `evidence/` or `reports/` — keep reusable helpers next to the
eval that produced them.

### Method caveats (always note in report header)

- Live-map cache retains ~**24h**; a `7d` window label still mostly sees recent TAC.
- Bare-`annex3` tallies **overstate** residuals vs prefer-resolved severity
  (e.g. US/CA `PROB_PERIOD_WITHOUT_TEMPO`, mil `INVALID_TX_TN`). Prefer path is
  authoritative for dispositions.
- Count churn between runs is often cache age-out, not a rule regression.

## 3. Report tables

Write markdown + JSON under `sessions/<id>/reports/`. Templates:
[reference.md](reference.md).

Required tables:

1. **code × count × description** (severity + registry description)
2. **convert pass/fail** per code (and overall)
3. **IWXXM validate pass/fail** per code (and overall)
4. **region % of total** per code (continent / country / ICAO prefix bucket)
5. **station / product rollups** (warn+error focus)

Optional companions (match prior EV naming when useful):

- `live-Nd-lint-code-counts.{md,json}`
- `live-Nd-warn-error-by-station.{md,json}`
- `live-Nd-promote-disposition.md`

## 4. Promote analysis

For each warn/error code (or user-selected set):

1. **Consistent station/region rule?** Same prefix / municipality / product, or
   singleton churn?
2. **Literature search?** Use [mine-domain-sources](../mine-domain-sources/SKILL.md)
   / domain canonicals when proposing a remapped severity or new dialect accept.
3. **Disposition** (pick one):
   - `leave` / `keep-as-error` — true positive or source quality
   - `profile` / `profile-remap` / `national-prefer` — lint profile / prefer
   - `product-rule` / `product-rule-fix` — detector / grammar fix
   - `bug-ticket` · `defer` · `soft-only-if-MISG-or-solidi` (explicit nil only)

### Hard constraints (do not violate without ADR)

| Constraint | Rule |
|------------|------|
| **No Europe blanket** | Do not invent a Europe-wide profile or soften Europe residuals en masse |
| **No `MISSING_*` soften** | Leave plain AUTO omissions as error; optional later soft **only** for explicit `VIS MISG` / `PRES MISG` / `////` |
| **No CW* VIS/QNH soften** | Canada `CW*`/`CZ*` MANOBS — do not blanket-soften `MISSING_VISIBILITY` / `MISSING_QNH` |
| **Keep `INVALID_PROB`** | Remain error unless an ADR explicitly changes it |

Cite [Corpus: product] (F15/F20/profile prefer) and [Corpus: tests] for gates; put
ticket/ADR ids only in session reports and agent text — never in UI/OpenAPI copy.

## 5. Output paths

| Artifact | Path |
|----------|------|
| Reports | `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/<id>/reports/` |
| Evidence / scripts | `…/sessions/<id>/evidence/` (or reuse EV-regional-dialect-profiles) |
| Prior baseline | `…/sessions/EV-regional-dialect-profiles/reports/live-7d-*` |

Filenames: `live-<Nd>-<slug>.{md,json}` (e.g. `live-7d-lint-code-counts.md`).

## 6. Citations & surfaces

- Agent/docs: `[Corpus: product]`, `[Corpus: tests]` (+ ADR when disposition
  needs a standing decision).
- Operator/public: plain language only — no `[Corpus:…]`, `docs/sessions/…`,
  `ADR-*`, `EV-*`, `TC-*`, `#NNN`.

## 7. Related evolves (pointers only)

Do not block this skill on these; cross-link when a disposition needs them:

| Session / theme | Why it matters |
|-----------------|----------------|
| `EV-file-budget-complexity` | File-budget ADR — keep eval scripts/reports lean; avoid mega-modules |
| `EV-lint-inherit-factory` | Inherit-factory ADR — profile `inherits` / shared `lint_with_profile` |
| `EV-severity-strict-ui` / `UX-tac-severity-tooltip` | Severity/strict UI — operator severity display vs registry log level |

Active session store: `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/<id>/`.

## Quick command (lint tallies only)

From monorepo root with `tac-validate` importable:

```bash
SESSION="$HOME/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-regional-dialect-profiles"
python "$SESSION/evidence/relint_live_map.py" \
  --window-days 7 \
  --out-prefix "$HOME/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/<id>/reports/live-7d-lint-code-counts"
```

Then run convert + IWXXM validate over the same TAC set; fill tables from
[reference.md](reference.md).

## Do not

- Soften `INVALID_PROB`, invent Europe profiles, or CW* VIS/QNH blanket softens
- Commit secrets / live TAC dumps with credentials into git
- Treat bare-annex3 counts as post-prefer truth
- Put planning ids on user-facing surfaces
