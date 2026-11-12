# Tooling config

Shared formatter and lint settings for the monorepo.

| File | Tool |
|------|------|
| `prettier.json` | Prettier options |
| `prettierignore` | Reference ignore list (scripts use `.gitignore` plus path globs) |
| `eslint.config.js` | ESLint (root `pnpm run lint:js`) |
| `yamllint.yml` | yamllint (pre-commit) |
| `gitleaks.toml` | gitleaks (pre-commit) |

Root `package.json` and `.pre-commit-config.yaml` point here. Do not add new
copies of these files at the repository root.
