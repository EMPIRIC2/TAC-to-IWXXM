# Tooling config

Shared formatter and lint settings for the monorepo.

| File | Tool |
|------|------|
| `prettier.json` | Prettier options |
| `prettierignore` | Prettier ignore list (linked from repo-root `.prettierignore`) |
| `eslint.config.js` | ESLint (root `pnpm run lint:js`) |
| `yamllint.yml` | yamllint (pre-commit) |
| `gitleaks.toml` | gitleaks (pre-commit) |

Root `package.json` and `.pre-commit-config.yaml` point here. Keep a root
`.prettierignore` symlink so Prettier can apply ignore patterns from the
repository working directory.
