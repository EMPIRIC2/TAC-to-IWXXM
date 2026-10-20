# QA gap fills

Session: EV-qa-gap-fills. Scale: standard. Gate: closed.

[Corpus: tests] [Corpus: api] [Corpus: deploy] [Corpus: decisions]

## Goal

Make the four regression tests from the 2026-10-19 QA scan pass without weakening them and without lowering the 100% coverage floor.

## What is already true

Frontend and Python package reports on disk are at 100% where a report exists. Playwright smell review found no silent-pass failure. Staging deploy uses the DOKS hosts `https://api.staging.tac-to-iwxxm.com` and `https://app.staging.tac-to-iwxxm.com`. The live-signoff example in `docs/deploy.md` still names Render hosts. The staging-smoke job sets `STAGING_SMOKE_PYTEST` to `0`, and a bad CORS preflight does not fail the script.

The OpenAPI checker in the working tree exits 0 with a provenance fixture (`consumer-tests` + `covered_by`). The Playwright coverage collector runs suite callbacks under a V8 harness (stub fixtures, no browser) and writes `apps/e2e/coverage/coverage-final.json` at 100% statements with branch data.

## Must not break

Public convert, lint, and validate behavior. The 100% unit floor. Promote path: full Playwright on a pull request into `main`, production deploy only from a deploy tag.

## Out of scope

New product features, a Pact broker, assertion rewrites for the open Playwright smell issues, and any change to operator-facing API behavior.

## Open question

Closed 2026-10-19: G1 uses provenance. Each interaction names `covered_by`. The fixture source is not the OpenAPI document. See [ev-qa-gap-fills.md](../decisions/ev-qa-gap-fills.md).
