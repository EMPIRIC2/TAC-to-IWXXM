---
name: ci-after-push
description: >
  After every git push on TAC-to-IWXXM, watch required GitHub CI until green.
  Covers evolve→stage vs stage→main promote expectations and recurring footguns.
---
# CI after push (TAC-to-IWXXM)

[Corpus: tests] [Corpus: deploy]

Follow `.cursor/rules/optional/ci-after-push.mdc` and
`.cursor/rules/optional/ci-recurring-footguns.mdc`.

## Procedure

1. From monorepo root, after `git push`:
   ```bash
   gh run list --branch "$(git branch --show-current)" --workflow ci-cd.yml --limit 3
   gh run watch <run-id>
   ```
2. On failure: `gh run view <run-id> --log-failed`. For E2E Full, also download Playwright
   artifacts from the Actions UI / `gh run download`.
3. Map the failure to `ci-recurring-footguns.mdc` (coverage, E2E Full, Mutation pnpm,
   vendor sync, evolve lint/coverage, machine-local `.cursor` paths).
4. Fix → push → re-watch. Do not mark the session done on a red tip.

## Branch expectations

| Work | Base / path |
|------|-------------|
| Feature / evolve | PR into **`stage`** |
| Promote | **`stage`→`main`** only; E2E Full required |
| Prod | Deploy tag after `main` tip CI (not auto on merge) |

## Local parity before first push

```bash
make format-check lint typecheck test-unit
# or make validate-fast / make ci
```

Guards: `make cursor-no-home-paths-guard`, `make pnpm-action-package-manager-guard`.
