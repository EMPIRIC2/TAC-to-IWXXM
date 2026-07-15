# PR Review — PRR-019 (18-pr-review)

> **Generated**: 2026-07-15  
> **Skill**: 18-pr-review  
> **Session**: S011-f7-operator-ui / EV-008  
> **PR**: [#716](https://github.com/joseph-c-mcguire/metar-to-IWXXM/pull/716)  
> **Head**: `012c49025faa5a14f6a17f41f95133a5a4f6c481` (`evolve/S011-f7-operator-ui` → `main`)  
> **Scope**: full checklist + connectivity / integration emphasis  

## Verdict

**REQUEST CHANGES** (2 🔴, 3 🟡)

Self-author reviews may land as `COMMENT` with the same body.

## Local integration evidence

| Check | Result |
|-------|--------|
| `test_f7_ui_connection_integration` + TC-F7-003 + admin removed + H0c | 24 passed (`--no-cov`) |
| FE Vitest (workbench/convert/api/convertParams/inputKind) | 149 passed |
| Multi-line soft-preview span offsets | **FAIL (product bug)** — see findings |
| `make secrets-check` | PASS |
| Playwright T2 | Not run (ports 18000/18001 + disk full) |
| Remote CI Validate | FAIL — `pnpm audit` 410; Test/E2E skipped |

## Subagents

| Agent | Result |
|-------|--------|
| Bugbot | High: multi-line span offsets; Medium: SUCCESS logging on soft preview; Medium: gzip bomb |
| Security | Medium: gzip bomb; RLS/admin/CORS/credentials OK |

## Findings

### 🔴 Multi-line `failed_spans` offsets (`absorb_soft_preview`)

Confirmed: two-line `preview=true` convert returns line-local spans that highlight the wrong line in the full buffer.

### 🔴 D1 — CI red on tip

Validate failed on npm audit endpoint 410 → package Test + E2E Smoke skipped.

### 🟡 Gzip decompress unbounded until after inflate

### 🟡 Soft-preview logs/webhooks SUCCESS on partial fail

### 🟡 Browser E2E / H4–H5 still not proven on this tip

## Posted

Inline + review body on GitHub PR #716 (PRR-019).
