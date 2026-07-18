---
name: pypi-release-checklist
description: >
  Validates PyPI publish readiness for tac-validate, iwxxm-validate, and tac2iwxxm
  (F12–F14): OIDC trusted publishing, version tags, package boundaries, wheel
  copyright constraints, and hard perf gates at publish. Use before tagging,
  editing publish workflows, or cutting 0.1.0 releases.
---

# PyPI Release Checklist (F12–F14)

## When to Use

- Before `git tag` for `tac-validate-v*`, `iwxxm-validate-v*`, or `tac2iwxxm-v*`
- When adding/editing `.github/workflows/*publish*` / PyPI workflows
- During **12-verify-deploy** / **08-verify-build** publish gates (S014 / EV-010)
- User asks "ready to publish to PyPI?"

## Spec Sources

| Source | What to check |
|--------|----------------|
| `docs/feature-list.md` F12–F14 | Acceptance criteria |
| `docs/config-spec.md` §F11–F14 | OIDC / no long-lived token |
| `docs/deploy.md` | PyPI + Render notes |
| `docs/context/package-publish-validation.md` | Publish path + copyright |
| ADR-026 | HTTP msgspec boundary (not required for library-only tags) |
| `.cursor/rules/core/pypi-package-publish.mdc` | Tag patterns + boundaries |

## Checklist

### 1. Identity & CI

- [ ] PyPI project names: `tac-validate`, `iwxxm-validate`, `tac2iwxxm` at version `0.1.0` (or next semver)
- [ ] One GHA workflow with a **package matrix** (three packages); trigger on matching version **tags only**
- [ ] `permissions: id-token: write` present
- [ ] PyPI Trusted Publisher configured for each project (OIDC) against that matrix workflow + tag filter — **no** `PYPI_API_TOKEN` secret when OIDC is live
- [ ] Build produces sdist + wheel (maturin manylinux/macOS/win for native); smoke-install in clean venv before publish job succeeds

### 2. Tags

| Package | Tag example |
|---------|-------------|
| tac-validate | `tac-validate-v0.1.0` |
| iwxxm-validate | `iwxxm-validate-v0.1.0` |
| tac2iwxxm | `tac2iwxxm-v0.1.0` |

- [ ] Tag matches package being released (do not reuse one tag for all three)
- [ ] `tac2iwxxm[validate]` extra depends on both validators

### 3. Package boundaries

- [ ] `tac-validate`: no IWXXM/XSD/Schematron
- [ ] `iwxxm-validate`: no TAC parsing; schemas bundled from pins only
- [ ] `tac2iwxxm`: no FastAPI/Supabase imports
- [ ] No full Annex 3 / FMH copyrighted text in wheel contents (cite-only)

### 4. Quality gates at publish

- [ ] Soft benches recorded during build; **hard-fail** at publish for:
  - library lint→convert→XSD+SCH vs lxml baseline (F11/F13)
  - msgspec HTTP ≤ prior pydantic map path (if F11 shipping same cutover)
  - wheel smoke installs (UJ-023 / UJ-DEV-005)
- [ ] Parity suite green for `iwxxm-validate` vs golden corpus
- [ ] CLI smoke: `tac-validate` on fixture TAC

### 5. Docs

- [ ] Package README install/usage present
- [ ] `docs/dependency-inventory.md` lists publish-time deps (maturin/Rust if needed)
- [ ] Render redeploy planned if F11 HTTP contract changed (stages 12–13)

## Output Format

```
PyPI Release Checklist: PASS | FAIL | BLOCKED

Package: tac-validate | iwxxm-validate | tac2iwxxm
Tag: <proposed>
OIDC: ok | missing
Boundaries: ok | violations[...]
Hard gates: ok | failing[...]
Blockers: [...]
Next: tag | fix CI | fix package | AskQuestion
```

## Related

- Rule: `.cursor/rules/core/pypi-package-publish.mdc`
- Hook: `.cursor/hooks/pypi_release_guard.py`
- Skill: `api-contract-validator` (for F11 HTTP/FE type changes in the same cycle)
