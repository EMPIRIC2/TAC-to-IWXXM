# Tooling config

Shared formatter and lint settings for the monorepo.

| File | Tool |
|------|------|
| `prettier.json` | Prettier options |
| `prettierignore` | Reference ignore list (scripts use `.gitignore` plus path globs) |
| `eslint.config.js` | ESLint (root `pnpm run lint:js`) |
| `yamllint.yml` | yamllint (pre-commit) |
| `gitleaks.toml` | gitleaks (pre-commit) |
| `importlinter.ini` | import-linter layer contracts |
| `knip.json` | Knip unused files/deps (`pnpm run check:knip`) |
| `.dependency-cruiser.cjs` | dependency-cruiser import rules (`pnpm run check:depcruise`) |

### JS dependency hygiene (Knip + dependency-cruiser)

Reports go to `.quality-reports/` (git-ignored). Known allowlists in `knip.json`:

- `apps/frontend/src/generated/**` stays out of ESLint, Prettier, coverage, and
  the depcruise graph (OpenAPI codegen output). Knip does not see it (`.d.ts`).
- Unused shadcn/Figma Make kit files under `apps/frontend/src/app/components/ui/`
  are listed in `ignore`; delete a file there and drop its entry when removing it.
- `apps/frontend` `ignoreDependencies` lists packages that only the unused kit
  (or CSS `@import`) uses. Remove the package and its entry together.
- Unused exports/types in `apps/frontend/src/**` are not gated yet
  (`ignoreIssues`; about 200 findings). Other workspaces fail on unused exports.

Root `package.json` and `.pre-commit-config.yaml` point here. Do not add new
copies of these files at the repository root.
