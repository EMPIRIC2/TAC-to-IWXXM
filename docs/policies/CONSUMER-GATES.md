# Plugin-consumer gates checklist

[Corpus: quality-templates] [Corpus: adr-036] [Corpus: adr-037] [Corpus: deps] [Corpus: deploy] [Corpus: skill-integration]

For every product repo that installs the engineering-memory Cursor plugin.
Canonical enforcement lives in `spec-dev-knowledge-graph` first; copy/adapt into consumers via explicit PRs (EV-049 / #108).

## A. Security (hard-fail)

- [ ] Install OpenGrep, Checkmarx 2ms, KICS, Grype, Microsoft SBOM Tool (prefer repo `scripts/security` or Make; else pack portable scripts)
- [ ] Wire `security-scan` (or equivalent) into **CI validate** and **pre-push / push gate** — non-zero exit fails the job
- [ ] Thresholds: OpenGrep ERROR; 2ms any secret; KICS high/critical; Grype high; SBOM must generate; Supabase advisors ERROR **or** documented skip when unused
- [ ] Gitignore tool/report dirs (e.g. `.tools/security/`, `.security-reports/`)

## B. Quality (ADR-036)

- [ ] Copy/adapt `packages/agent-tooling/templates/quality/` for each Py and/or TS package
- [ ] Scripts: format check, lint, typecheck, unit coverage — all fail closed
- [ ] Coverage **100%** with documented omit allowlist only — no silent weaken
- [ ] CI fails unless all quality gates pass

## C. Exact dependency pins

- [ ] Direct deps in `package.json` / `pyproject.toml` use exact versions (no `^` / `~` / `>=`)
- [ ] Lockfiles committed (`package-lock.json`, `uv.lock`, or equivalent)
- [ ] Exact-pin verify/CI check fails on range operators except documented allowlist
- [ ] Inventory / CORPUS lists versions matching manifests
- [ ] Upgrade path: bump pin → regenerate lock → re-run security-scan + quality gates

## D. Sign-off

- [ ] CORPUS cites ADR-036 + ADR-037 (or waiver)
- [ ] Operator/session HANDOFF records rollout or AskQuestion waiver per consumer

## Out

Soft/warn-only security; 100% e2e; autonomous PRs into non-plugin repos; product-behavior changes.
