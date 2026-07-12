# BUG-2026-07-12 — Conversion results Card not dismissed after Cancel/Remove

| Field | Value |
|-------|-------|
| **Status** | verified / closed |
| **Feature** | F1 (METAR → IWXXM conversion UI) |
| **Severity** | critical / blocked (user) |
| **Classification** | code bug (UI state + F5 hydrate) |
| **Remediation path** | local-first — deploy only after explicit approval |
| **Session** | S009-result-card-dismiss |
| **Branch** | fix/S009-result-card-dismiss |

## Error description

After converting TAC in the operator UI, the results `Card` for `manual_input.txt`
(Source TAC + IWXXM XML) remains on screen after the user clicks **Cancel** or the
**Remove** control (`aria-label="Remove manual_input.txt from results"`).

DOM (user report): `div[data-slot="card"]` under `FileConverter` results list;
React minified component name `Oe`. Example content included METAR FAOR COR sample
and IWXXM XML.

## Error logs

No server stack trace (UI state). User DOM evidence:

```
aria-label="Remove manual_input.txt from results"
data-slot="card" … manual_input.txt DOWNLOAD COPY SOURCE TAC METAR FAOR …
```

## Interview record

| Step | Answer |
|------|--------|
| Intent | Report new issue (2A) |
| Session | Open S009 (1A) |
| Routing | Assumed A — 14 required; 15 optional |
| symptom_type | B — Wrong output / stuck UI |
| where_seen | A — Production (Render frontend) |
| when_started | A — After last deploy |
| repro_frequency | A — Every time |
| repro_environment | A — Production only |
| user_severity | A — Critical / blocked |
| evidence_available | C — None yet (DOM path from report is the evidence) |
| Remediation path | A — Fix locally first; deploy only after approval |
| confirm_hotfix_plan | A — Proceed (2026-07-12) |
| verification_plan | success=A; checks=B; monitoring=A |

## Symptoms & reproduction

- **Environment:** Production frontend only (every time)
- **Trigger:** Convert (manual input) → results Card appears → Cancel or Remove (X)
- **Expected:** Card dismissed / results cleared
- **Actual:** Card remains visible
- **Local:** Not reproduced yet (production-only per intake)

## Investigation

### Hypotheses (2026-07-12)

| # | Hypothesis | Evidence | Status |
|---|------------|----------|--------|
| H1 | `handleClear` clears queue/input only — **not** `convertedFiles` | `FileConverter.tsx` L746–751; prior note in `docs/context/issue-555-feedback.md` | Confirmed in code; repro #1 RED |
| H2 | Remove works locally but stale `loadedWorkSession` rehydrate restores card | `useLayoutEffect` on `[loadedWorkSession]` L233–297; autosave schedules snapshot **before** debounce without including later Remove | Repro #2 RED |
| H3 | Remove `onClick` broken / no-op | Existing unit test expects Remove to work; button wiring present | Unlikely sole cause |

### Spec conformance

| Corpus | Section | Finding |
|--------|---------|---------|
| product F1 | #555 UX — replace result cards | Implementation drift: Clear does not dismiss results; Remove can be undone by hydrate |
| product F5 | Auto-save 3s debounce + hydrate | Implementation drift: hydrate from `loadedWorkSession` overwrites intentional local Remove |
| system-spec | Frontend FileConverter / F5 | No blocking contradiction — fix aligns with expected dismiss UX |
| api | N/A | No API change required |

Spec conformance: **no blocking Contradiction**; fix is code bug / UX drift vs F1 #555 intent.

## Root cause (proposed)

1. **Clear** (`handleClear`) clears pending files + manual input only — leaves `convertedFiles` / results Card.
2. **Remove** updates local state, but any later `loadedWorkSession` change (stale autosave/`onSessionSaved`) re-runs hydrate `useLayoutEffect` and restores `converted_results`.

## Repro test

| Field | Value |
|-------|-------|
| Path | `apps/frontend/src/test/bug-2026-07-12-result-card-dismiss.test.tsx` |
| CI | Frontend job (`npm test`) — not pytest `tests/bugs/` |
| Status | **GREEN** (2/2 passed) 2026-07-12; user confirmed matches symptom (A) |
| Assert 1 | Clear dismisses `manual_input.txt` Card |
| Assert 2 | After Remove, stale `loadedWorkSession` update must not restore Card |

### TDD iteration log

| Time | Action | Result |
|------|--------|--------|
| 2026-07-12 | Wrote Vitest repro (Clear + stale rehydrate) | RED — both assertions fail as expected |
| 2026-07-12 | User `repro_test_matches_symptom`=A | Confirmed |
| 2026-07-12 | User `investigation_root_cause`=A | Proceed to fix |
| 2026-07-12 | Patch applied | GREEN — 2/2 repro pass; FileConverter suites 93/93 |

## Fix

**Branch:** `fix/S009-result-card-dismiss`

**Changes** (`apps/frontend/src/app/components/FileConverter.tsx`):

1. **`handleClear`** — also clears `convertedFiles` and `conversionLog`.
2. **Work-session hydrate** — track `hydratedWorkSessionIdRef`; only full hydrate when session **id** changes, not on every autosave/`onSessionUpdated` refresh.
3. **Autosave deps** — include `convertedFiles` and `conversionLog` so Remove/Clear persist to F5 draft.

## Verification plan

| Field | Value |
|-------|-------|
| success_criterion | A — Remove/Cancel clears results Card (stuck-card gone) |
| verification_checks | B — Full main CI parity (local) + gh CI on main after merge |
| monitoring_followup | A — User watches production after deploy |

### Layer checklist (to fill during verify)

- [x] Layer 1 — Automated (bug repro green 2/2; FileConverter 93/93; main CI green post-merge)
- [x] Layer 2 — Reproduction (Vitest `bug-2026-07-12-result-card-dismiss.test.tsx` — Clear + stale rehydrate)
- [x] Layer 3 — Pre-deploy smoke (frontend unit suite green on PR branch + main)
- [x] Layer 4 — Production (Playwright prod smoke 2026-07-12: Clear + Remove dismiss results region after draft saved; deploy `dep-d9a1tql7vvec738evhmg` live `b20158b`)

**PR:** [#713](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/713) merged → `b20158b7b29d5e5b68d3cd80c9618454743713e1`

## Prevention & countermeasures

| Field | Answer |
|-------|--------|
| `prevention_recurrence_risk` | Possible on similar F5 / hydrate changes |
| `prevention_detect_earlier` | Main CI (frontend `npm test` on PR) |
| `prevention_automated` | Bug repro test (done) — runs in CI frontend job |
| `prevention_code_hardening` | No — hotfix only |
| `prevention_process` | Cursor rule for FileConverter F5 hydrate pattern |
| `prevention_when` | Now (closure commit) |
| `prevention_who` | Agent |

### Planned actions

| Action | Status |
|--------|--------|
| Vitest repro `bug-2026-07-12-result-card-dismiss.test.tsx` | Done (shipped in #713) |
| Cursor rule `.cursor/rules/optional/fileconverter-f5-hydrate.mdc` | Done |
| Hotfix report `docs/sessions/S009-result-card-dismiss/reports/hotfix.md` | Done |

### Regression prevention

- `apps/frontend/src/test/bug-2026-07-12-result-card-dismiss.test.tsx` (Clear + stale rehydrate)
- Existing `FileConverter.test.tsx` Remove assertion

## Cursor rule

`.cursor/rules/optional/fileconverter-f5-hydrate.mdc` — hydrate-on-id-change, Clear scope, autosave deps.
