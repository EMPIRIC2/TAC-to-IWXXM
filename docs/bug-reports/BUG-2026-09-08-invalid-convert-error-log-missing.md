# Bug report: invalid convert error log missing on staging

**ID:** BUG-2026-09-08-invalid-convert-error-log-missing  
**Date:** 2026-09-08  
**PR:** pending  
**Session:** EV-staging-adversarial-e2e

## Error description

On the staging converter, a hard convert with invalid TAC shows a generic `Conversion Error`
state but does not render the visible `Conversion error log` panel. The operator therefore
loses the structured validation and lint details that the API already returns for the failure.

## Error logs

```text
POST https://api.staging.tac-to-iwxxm.com/api/v1/convert
HTTP 400

detail.message = "All conversions failed"
detail.errors = ["manual_input: Validation failed - 1 validation issue(s) found"]
detail.issues[0].code = "VALIDATION_FAILED"
detail.issues[1].code = "ICAO_VALIDATION_FAILED"
detail.issues[3].code = "MISSING_CCCC"
```

Targeted live repro:

```text
cd apps/e2e
PLAYWRIGHT_BASE_URL=https://app.staging.tac-to-iwxxm.com \
PLAYWRIGHT_API_BASE_URL=https://api.staging.tac-to-iwxxm.com \
pnpm exec playwright test issue-555-ux-delta.e2e.spec.ts --grep "failed convert shows error log panel"
```

Result: red on staging; `getByLabel(/conversion error log/i)` not found.

## Investigation

1. Staging `config.json` points at `https://api.staging.tac-to-iwxxm.com`.
2. Direct API probe shows hard-convert invalid TAC returns HTTP 400 with structured
   `detail.errors` and `detail.issues`.
3. First pass: `apps/frontend/src/utils/api.ts` now preserves structured convert failures via
   `ConvertApiError`, and `FileConverter` populates `conversionLog` from that error.
4. Live Playwright still failed after that deploy because the panel asserted
   `All conversions failed`, while the catch path only stored `error.errors` and omitted the
   top-level `error.message`.
5. Follow-up: merge the primary convert message into the visible error log, keep blank
   messages out of the panel, and harden `openPublicConverter()` with one navigation retry
   for intermittent staging shell-load flakes.
6. Stage CI then blocked deploy on frontend branch coverage 99.94% until the blank-message
   merge branches were covered.

**Root cause:** hard-convert catch path omitted the top-level convert failure message from
the visible error-log panel; live flakes separately hit a brittle first-load wait in the
shared Playwright helper.

## Repro test

- Path: `apps/frontend/src/utils/api.test.ts`
- Path: `apps/frontend/src/app/components/FileConverter.test.tsx`
- Path: `apps/e2e/issue-555-ux-delta.e2e.spec.ts`
- Status: unit/component green locally; live staging re-verify green on
  `ea8ef014` (invalid convert + previously flaky shell-load specs)

## Fix

1. Preserve structured `errors` / `issues` in `ConvertApiError`.
2. Merge `error.message` into the visible conversion log for hard-convert failures.
3. Retry one public-converter navigation in Playwright before failing heading waits.
4. Cover blank-message merge branches so frontend coverage stays at the 100% branch gate.

## Interview record

- Build gate: Open Build and proceed with fixes now.
- First bug: Missing visible conversion error log on invalid convert.
- Remediation path: Fix locally, redeploy to stage, and re-run live tests.
- Severity: High.
- Repro confirmation: confirmed from targeted staging Playwright repro.
- Root cause confirmation: approved dual fix (error-log message merge + page-open retry).
- Flake scope: address flakes in the same pass if actionable.
- Live verification: issue-555 + four flake specs passed against staging after
  `ea8ef014` deploy.

## Prevention & countermeasures

- Add API-client regression coverage so non-2xx convert responses keep structured details.
- Add converter regression coverage so hard-convert failures still render `ErrorLogPanel`.

## Cursor rule

- No new rule proposed yet; existing bug-investigation and TDD rules covered the workflow.
