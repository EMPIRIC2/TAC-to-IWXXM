SHELL := /bin/bash
COMPOSE := docker compose
UV := uv
PNPM := pnpm

PY_TREES := apps packages tests
PY_LINT := apps/backend/src apps/backend/tests \
	packages/auth/src packages/auth/tests \
	packages/shared packages/shared/tests \
	packages/tac2iwxxm/src packages/tac2iwxxm/tests \
	packages/iwxxm-validate/src packages/iwxxm-validate/tests \
	packages/tac-validate/src packages/tac-validate/tests \
	packages/dissemination/src packages/dissemination/tests \
	tests

.PHONY: install test test-unit vendor-sync \
	test-unit-workspace test-unit-workspace-py test-unit-shared-py test-unit-shared-js test-unit-workspace-js \
	test-unit-backend test-unit-auth test-unit-frontend \
	test-unit-tac2iwxxm test-unit-iwxxm-validate test-unit-tac-validate \
	test-unit-dissemination test-unit-worker test-bugs \
	compose-wis2box-up compose-wis2box-down compose-wis2box-harness \
	format format-check typecheck typecheck-py typecheck-js \
	lint lint-py lint-js lint-backend lint-auth lint-frontend lint-shared \
	lint-tac2iwxxm lint-iwxxm-validate lint-tac-validate lint-dissemination \
	lint-fix lint-fix-py lint-fix-backend lint-fix-auth lint-fix-frontend \
	dev dev-kill dev-servers dev-servers-kill \
	test-e2e-playwright test-e2e-playwright-smoke test-e2e-t2-product \
	test-live-connectivity test-live-api test-live-integration test-live-e2e test-live-bulletin test-live \
	test-integration coverage coverage-backend coverage-auth coverage-frontend coverage-shared \
	coverage-dissemination coverage-modules coverage-all ci acci badge-audit audit-frontend \
	validate-fast validate-yaml secrets-check config-guard validate-ci env-check \
	install-hooks pre-commit-run \
	catalog-regen catalog-check \
	issue-registry-guard \
	supabase-start supabase-stop supabase-reset supabase-status supabase-push supabase-pull \

# --- Monorepo workspace ---

install:
	$(UV) sync
	corepack enable
	$(PNPM) install

install-hooks:
	$(UV) run pre-commit install

pre-commit-run:
	$(UV) run pre-commit run --all-files

# --- F15 issue catalog (ADR-028 / EV-011) ---

catalog-regen:
	$(UV) run python scripts/tac-validate/regen_issue_catalog.py

catalog-check: catalog-regen
	@git diff --quiet -- docs/domain/rules/ISSUE_CATALOG.md docs/domain/rules/ISSUE_CATALOG.json \
		|| (echo "ISSUE_CATALOG drift — run make catalog-regen and commit"; git diff --stat -- docs/domain/rules/ISSUE_CATALOG.md docs/domain/rules/ISSUE_CATALOG.json; exit 1)

# F15 — hard-fail on severity= literals in rule modules (T2.2a / E11-32)
issue-registry-guard:
	ISSUE_REGISTRY_GUARD_STRICT=1 $(UV) run python scripts/ci/check_issue_registry_literals.py \
		packages/tac-validate/src/tac_validate/rules.py \
		packages/tac-validate/src/tac_validate/product_rules.py

# --- Formatting ---

format:
	$(UV) run ruff format $(PY_TREES)
	$(PNPM) run format

format-check:
	$(UV) run ruff format --check $(PY_TREES)
	$(PNPM) run format:check

# --- Typechecking ---

typecheck: typecheck-py typecheck-js

typecheck-py:
	$(UV) run basedpyright packages/shared/src
	$(UV) run basedpyright packages/tac2iwxxm/src
	$(UV) run basedpyright packages/iwxxm-validate/src
	$(UV) run basedpyright packages/tac-validate/src
	cd packages/auth && $(UV) run basedpyright
	cd apps/backend && $(UV) run basedpyright

typecheck-js:
	$(PNPM) run typecheck:js

# --- Linting ---

lint: lint-py lint-js

lint-py:
	$(UV) run ruff check --force-exclude $(PY_LINT)

lint-js:
	$(PNPM) run lint:js

lint-backend:
	$(UV) run ruff check --force-exclude apps/backend/src apps/backend/tests

lint-auth:
	$(UV) run ruff check --force-exclude packages/auth/src packages/auth/tests

lint-shared:
	$(UV) run ruff check --force-exclude packages/shared packages/shared/tests

lint-tac2iwxxm:
	$(UV) run ruff check --force-exclude packages/tac2iwxxm/src packages/tac2iwxxm/tests

lint-iwxxm-validate:
	$(UV) run ruff check --force-exclude packages/iwxxm-validate/src packages/iwxxm-validate/tests

lint-tac-validate:
	$(UV) run ruff check --force-exclude packages/tac-validate/src packages/tac-validate/tests

# F16–F19 — package present after T1.1; keep target for scoped lint.
lint-dissemination:
	$(UV) run ruff check --force-exclude packages/dissemination/src packages/dissemination/tests

lint-frontend:
	$(PNPM) --filter @metar/frontend run lint

lint-fix: lint-fix-py lint-fix-frontend

lint-fix-py:
	$(UV) run ruff check --fix --force-exclude $(PY_LINT)

lint-fix-backend:
	$(UV) run ruff check --fix --force-exclude apps/backend/src apps/backend/tests

lint-fix-auth:
	$(UV) run ruff check --fix --force-exclude packages/auth/src packages/auth/tests

lint-fix-frontend:
	$(PNPM) --filter @metar/frontend exec eslint src --fix

# --- Unit tests ---

test-unit-workspace-py:
	$(UV) run pytest tests/migration/test_workspace_import_smoke.py tests/unit -v

test-unit-shared-py:
	$(UV) run pytest packages/shared/tests --cov=metar_shared \
		--cov-config=packages/shared/pyproject.toml --cov-branch --cov-fail-under=98 -v

test-unit-shared-js:
	$(PNPM) --filter @metar/shared run test:coverage

test-unit-workspace-js:
	$(PNPM) --filter @metar/shared test

test-unit-workspace: test-unit-workspace-py test-unit-shared-py test-unit-shared-js

test-unit-backend:
	cd apps/backend && $(UV) run pytest tests/unit \
		--cov=src --cov-config=pyproject.toml --cov-branch \
		--cov-report=xml:coverage.xml --cov-report=term-missing \
		--cov-fail-under=98 -v

test-unit-auth:
	cd packages/auth && $(UV) run pytest tests \
		--cov=src --cov-config=pyproject.toml --cov-branch \
		--cov-report=xml:coverage.xml --cov-report=term-missing \
		--cov-fail-under=98 -v

test-unit-frontend:
	$(PNPM) --filter @metar/frontend run test:coverage

test-unit-tac2iwxxm:
	$(UV) run pytest packages/tac2iwxxm/tests --cov=tac2iwxxm \
		--cov-config=packages/tac2iwxxm/pyproject.toml --cov-branch \
		--cov-report=term-missing --cov-fail-under=95 -v

# Build optional PyO3 extension (requires rustc + maturin). ADR-017 / T4.3.
build-tac2iwxxm-native:
	cd packages/tac2iwxxm && $(UV) run maturin develop --manifest-path rust/Cargo.toml --uv

# F13 — optional PyO3 extension (requires rustc + maturin). E10-36 / T3.1.
build-iwxxm-validate-native:
	cd packages/iwxxm-validate && $(UV) run maturin develop --manifest-path rust/Cargo.toml --uv

# E10-34 — copy runtime XSD+SCH+catalogs into the package (excludes modelling/translation).
sync-iwxxm-validate-schemas:
	$(UV) run python packages/iwxxm-validate/scripts/sync_runtime_schemas.py

test-tac2iwxxm-native: build-tac2iwxxm-native
	TAC2IWXXM_REQUIRE_RUST=1 $(UV) run pytest \
		packages/tac2iwxxm/tests/test_native_scaffold.py \
		packages/tac2iwxxm/tests/test_pyo3_hotspots.py -v --no-cov

test-iwxxm-validate-native: build-iwxxm-validate-native
	IWXXM_VALIDATE_REQUIRE_RUST=1 $(UV) run pytest \
		packages/iwxxm-validate/tests/test_native_scaffold.py \
		packages/iwxxm-validate/tests/test_tc_f13_001_parity.py -v --no-cov

# M1 — layer cost matrix harness (T1.1–T1.3). Script lands in build; stub until then.
bench-validation-stack:
	@if [ ! -f scripts/bench/validation_stack.py ]; then \
		echo "error: scripts/bench/validation_stack.py missing (execution plan T1.1–T1.2)"; \
		exit 1; \
	fi
	$(UV) run python scripts/bench/validation_stack.py

# F11 / ADR-027 — xsdata codegen from pinned XSD (T3.6).
codegen-iwxxm-xsd:
	$(UV) run python scripts/codegen/iwxxm_xsd.py

test-unit-iwxxm-validate:
	$(UV) run pytest packages/iwxxm-validate/tests --cov=iwxxm_validate \
		--cov-config=packages/iwxxm-validate/pyproject.toml --cov-branch \
		--cov-report=term-missing --cov-fail-under=95 -v

test-unit-tac-validate:
	$(UV) run pytest packages/tac-validate/tests --cov=tac_validate \
		--cov-config=packages/tac-validate/pyproject.toml --cov-branch \
		--cov-report=term-missing --cov-fail-under=95 -v

# F16–F19 / T0.1 — coverage paths; skips until packages/dissemination exists (T1.1/T1.2).
test-unit-dissemination:
	bash scripts/ci/run_dissemination_coverage.sh

# F17 / E14-04 — wis2box Compose harness (overlay); real service in T3.3.
compose-wis2box-up:
	@if ! grep -Eq '^[[:space:]]*wis2box:[[:space:]]*$$' docker-compose.wis2box.yml 2>/dev/null; then \
		echo "skip: wis2box service not defined yet (T3.3) — see docker-compose.wis2box.yml"; \
	else \
		$(COMPOSE) -f docker-compose.yml -f docker-compose.wis2box.yml --profile wis2box up -d; \
	fi

compose-wis2box-down:
	@$(COMPOSE) -f docker-compose.yml -f docker-compose.wis2box.yml --profile wis2box down --remove-orphans || true

compose-wis2box-harness:
	bash scripts/ci/run_wis2box_harness.sh

test-unit-worker:
	$(UV) run pytest apps/worker/tests -v --no-cov

test-bugs:
	$(UV) run pytest tests/bugs -m "not live and not live_api" --no-cov -v

test-unit: test-unit-workspace test-unit-backend test-unit-auth test-unit-frontend \
	test-unit-tac2iwxxm test-unit-iwxxm-validate test-unit-tac-validate \
	test-unit-dissemination test-unit-worker test-bugs

test: test-unit

tests\:e2e:
	cd apps/e2e && $(PNPM) exec playwright test

vendor-sync:
	bash scripts/vendor/sync-iwxxm.sh

dev:
	bash ./start-dev-servers.sh

dev-kill:
	bash ./start-dev-servers.sh --kill

dev-servers: dev

dev-servers-kill: dev-kill

audit-frontend:
	$(PNPM) --filter @metar/frontend run audit:ci

test-e2e-playwright:
	cd apps/e2e && $(PNPM) exec playwright test

test-e2e-playwright-smoke:
	cd apps/e2e && METAR_CONFIG_ENV=local $(PNPM) exec playwright test \
		auth-service-integration.e2e.spec.ts \
		tac-file-conversion.e2e.spec.ts

test-e2e-t2-product:
	cd apps/e2e && METAR_CONFIG_ENV=local $(PNPM) exec playwright test tac-file-conversion.e2e.spec.ts
	cd apps/e2e && METAR_CONFIG_ENV=e2e DISABLE_AUTH=false PLAYWRIGHT_API_BASE_URL=http://localhost:18001 \
		$(PNPM) exec playwright test auth.e2e.spec.ts

# --- Live E2E harness (H3–H6, manual signoff) ---

define load_dotenv
	set -a; \
	for env_file in .env apps/frontend/.env; do \
		if [ -f "$$env_file" ]; then \
			. "$$env_file"; \
		fi; \
	done; \
	set +a; \
	export LIVE_API_URL="$${LIVE_API_URL:-https://metar-to-iwxxm-api.onrender.com}"; \
	export LIVE_FRONTEND_URL="$${LIVE_FRONTEND_URL:-https://metar-to-iwxxm-frontend-v4-web.onrender.com}"; \
	export RUN_LIVE_TESTS=1; \
	export PLAYWRIGHT_BASE_URL="$${PLAYWRIGHT_BASE_URL:-$$LIVE_FRONTEND_URL}"; \
	export VITE_API_BASE_URL="$$LIVE_API_URL"; \
	export STAGING_API_URL="$$LIVE_API_URL"; \
	export STAGING_FRONTEND_ORIGIN="$$LIVE_FRONTEND_URL"; \
	export STAGING_FRONTEND_URL="$$LIVE_FRONTEND_URL"
endef

test-live-connectivity:
	@$(load_dotenv); \
	bash scripts/deploy/verify_connectivity.sh

test-live-api:
	@$(load_dotenv); \
	$(UV) run pytest apps/backend/tests/infrastructure/test_live_api_health.py -m live_api -v --tb=short --no-cov

test-live-integration:
	@$(load_dotenv); \
	$(UV) run pytest tests/integration/test_live_stack.py -m live -v --tb=short --no-cov

test-live-e2e:
	@$(load_dotenv); \
	export PLAYWRIGHT_BASE_URL="$$LIVE_FRONTEND_URL"; \
	export PLAYWRIGHT_API_BASE_URL="$$LIVE_API_URL"; \
	cd apps/e2e && DISABLE_AUTH=false PLAYWRIGHT_BASE_URL="$$PLAYWRIGHT_BASE_URL" \
		PLAYWRIGHT_API_BASE_URL="$$PLAYWRIGHT_API_BASE_URL" \
		$(PNPM) exec playwright test

# H7 — live bulletin gate (TC-LIVE-F6-030 / Q10=A)
test-live-bulletin:
	@$(load_dotenv); \
	$(UV) run pytest tests/live/test_tc_live_f6_030_bulletin.py -m live_api -v --tb=short --no-cov

test-live: test-live-connectivity test-live-api test-live-integration test-live-bulletin test-live-e2e

coverage-backend:
	cd apps/backend && $(UV) run pytest tests/unit \
		--cov=src --cov-config=pyproject.toml --cov-branch \
		--cov-report=xml:coverage.xml --cov-report=term-missing -v

coverage-auth:
	cd packages/auth && $(UV) run pytest tests \
		--cov=src --cov-config=pyproject.toml --cov-branch \
		--cov-report=xml:coverage.xml --cov-report=term-missing -v

coverage-frontend:
	$(PNPM) --filter @metar/frontend run test:coverage

coverage-shared:
	$(UV) run pytest packages/shared/tests --cov=metar_shared \
		--cov-config=packages/shared/pyproject.toml --cov-report=term-missing -v

coverage-dissemination: test-unit-dissemination

coverage-modules: coverage-backend coverage-auth coverage-frontend coverage-shared \
	coverage-dissemination

coverage-all: coverage-modules

test-integration:
	@set -a; \
	for env_file in .env apps/frontend/.env; do \
		if [ -f "$$env_file" ]; then \
			while IFS= read -r line || [ -n "$$line" ]; do \
				line="$${line%$$'\r'}"; \
				[[ -z "$$line" || "$$line" =~ ^[[:space:]]*# ]] && continue; \
				export "$$line"; \
			done < "$$env_file"; \
		fi; \
	done; \
	set +a; \
	required_vars="SUPABASE_PUBLISHABLE_KEY DATABASE_URL"; \
	legacy_ok=""; \
	if [ -n "$${SUPABASE_ANON_KEY:-}" ] && [ -z "$${SUPABASE_PUBLISHABLE_KEY:-}" ]; then \
		export SUPABASE_PUBLISHABLE_KEY="$$SUPABASE_ANON_KEY"; \
	fi; \
	if [ -n "$${VITE_SUPABASE_URL:-}" ]; then \
		legacy_ok="yes"; \
	fi; \
	if [ -n "$${VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY:-}" ] && [ -z "$${SUPABASE_PUBLISHABLE_KEY:-}" ]; then \
		export SUPABASE_PUBLISHABLE_KEY="$$VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY"; \
	fi; \
	export VITE_SUPABASE_URL="$${VITE_SUPABASE_URL:-$$(python3 -c 'import json;print(json.load(open("config/local.json"))["supabase"]["url"])')}"; \
	export VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY="$${VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY:-$$SUPABASE_PUBLISHABLE_KEY}"; \
	export VITE_API_BASE_URL="$${VITE_API_BASE_URL:-$$(python3 -c 'import json;print(json.load(open("config/local.json"))["api"]["baseUrl"])')}"; \
	export VITE_APP_URL="$${VITE_APP_URL:-$$(python3 -c 'import json;print(json.load(open("config/local.json"))["api"]["frontendUrl"])')}"; \
	missing=""; \
	for var in $$required_vars; do \
		if [ -z "$${!var}" ]; then \
			missing="$$missing $$var"; \
		fi; \
	done; \
	if [ -n "$$missing" ]; then \
		echo "Missing required environment variables for integration tests:"; \
		for var in $$missing; do echo "- $$var"; done; \
		exit 1; \
	fi
	-$(COMPOSE) down --remove-orphans
	$(COMPOSE) up -d backend frontend
	@echo "Waiting for services to become ready..."
	@for i in $$(seq 1 45); do \
		if wget --quiet --tries=1 --timeout=2 -O /dev/null http://localhost:18001/health \
			&& wget --quiet --tries=1 --timeout=2 -O /dev/null http://localhost:18000/; then \
			echo "All services are reachable."; \
			break; \
		fi; \
		if [ "$$i" -eq 45 ]; then \
			echo "Services did not become ready in time."; \
			$(COMPOSE) ps; \
			$(COMPOSE) logs --tail=120 backend frontend; \
			exit 1; \
		fi; \
		sleep 2; \
	done
	$(UV) run pytest tests/test_backend_auth_integration.py tests/test_backend_frontend_integration.py tests/test_auth_frontend_integration.py tests/test_integration.py -v
	cd apps/backend && $(UV) run pytest tests/integration/test_h0i_connectivity.py -v --no-cov
	cd apps/backend && $(UV) run pytest tests/infrastructure/test_smoke.py -k "cor or conversion or workflow" -q --no-cov
	$(COMPOSE) down

coverage: coverage-modules

badge-audit:
	python3 .github/scripts/badge_audit.py

# --- Fast validation (pre-commit + CI validate job) ---

secrets-check:
	$(UV) run pre-commit run gitleaks --all-files

validate-yaml:
	$(UV) run pre-commit run actionlint --all-files
	$(UV) run pre-commit run yamllint --all-files

validate-fast: format-check typecheck lint secrets-check validate-yaml catalog-check issue-registry-guard

config-guard:
	$(UV) run pytest tests/test_config_placeholders.py tests/smoke/test_h5_runtime_config.py -v

env-check:
	bash scripts/env/verify-sync.sh

# --- Supabase local stack (repo root supabase/) ---

supabase-start:
	bash scripts/supabase/local-dev.sh start

supabase-stop:
	bash scripts/supabase/local-dev.sh stop

supabase-reset:
	bash scripts/supabase/local-dev.sh reset

supabase-status:
	bash scripts/supabase/local-dev.sh status

supabase-push:
	bash scripts/supabase/db-push.sh

supabase-pull:
	bash scripts/supabase/db-pull.sh $(NAME)

validate-ci: validate-fast config-guard env-check audit-frontend

ci: format-check typecheck lint test-unit-workspace test-unit-backend test-unit-auth test-unit-frontend \
	test-unit-tac2iwxxm test-unit-iwxxm-validate test-unit-tac-validate test-unit-dissemination \
	test-unit-worker test-bugs test-integration badge-audit

acci: ci test-e2e-playwright-smoke audit-frontend
