# frozen_string_literal: true
# TAC-to-IWXXM — macOS local system dependencies (Homebrew Bundle)
#
# Install / refresh:
#   brew bundle --file=Brewfile
# Check without installing:
#   brew bundle check --file=Brewfile
# Install without upgrading already-present packages:
#   brew bundle --file=Brewfile --no-upgrade
#
# Exactness notes (Homebrew is rolling-release; no Gemfile.lock-style pin):
# - Versioned formulae pin the ADR-005 major line: python@3.12, node@22.
# - Comments record Homebrew *stable* bottle versions verified 2026-08-03.
# - `version_file:` keeps `.python-version` / `.nvmrc` aligned after install.
# - Do **not** brew-install pnpm — `make install` uses corepack → package.json
#   `packageManager` pin (`pnpm@9.15.4`).
# - See docs/ops/DEVELOPMENT.md §Prerequisites and docs/deploy.md (ODBC).

# =============================================================================
# Required — make install, unit tests, native maturin / PyO3 (ADR-005, ADR-017)
# =============================================================================

# Python 3.12.13 (formula revision 4) — ADR-005 / root pyproject requires-python >=3.12
brew "python@3.12", version_file: ".python-version"

# Node.js 22.23.2 — ADR-005 / engines.node >=22; enables corepack for pnpm@9.15.4
brew "node@22", version_file: ".nvmrc"

# uv 0.12.1 — Python workspace + lockfile (`uv sync`)
brew "uv"

# rust 1.97.1 (rustc/cargo) — maturin develop for tac2iwxxm / iwxxm-validate
# crates declare rust-version = "1.74"; CI uses dtolnay/rust-toolchain@stable
brew "rust"

# =============================================================================
# Recommended — local Compose stack, Testcontainers, Postgres client tools
# =============================================================================

# Docker Desktop 4.85.0,235549 — Docker Engine + Compose v2 (docker compose)
# Optional per DEVELOPMENT.md, but required for compose / Testcontainers / wis2box harness.
cask "docker-desktop"

# libpq 18.4 — `psql` and client libs without a host Postgres server
# (Compose ships bundled Postgres; use this for host-side DB tooling.)
brew "libpq"

# =============================================================================
# Optional — F16 SQL Server BYOC (aioodbc) local / integration testing
# =============================================================================

# unixODBC 2.3.14 — ODBC driver manager for aioodbc
brew "unixodbc"

# Microsoft ODBC Driver 18 is not in homebrew/core. After ACCEPT_EULA:
#   brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
#   HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18
# See docs/deploy.md §SQL Server ODBC and packages/dissemination/README.md.

# =============================================================================
# Optional — developer CLIs (pre-commit / Actions also pin some of these)
# =============================================================================

# GitHub CLI 2.97.0 — PRs / CI inspection (`gh`)
brew "gh"
