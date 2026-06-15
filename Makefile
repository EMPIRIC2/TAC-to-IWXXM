SHELL := /bin/bash
COMPOSE := docker compose
UV := uv
PNPM := pnpm

.PHONY: install test test-unit vendor-sync \
	test-unit-workspace test-unit-workspace-py test-unit-shared-py test-unit-workspace-js test-unit-legacy \
	lint lint-backend lint-auth lint-frontend lint-gifts \
	lint-fix lint-fix-backend lint-fix-auth lint-fix-frontend lint-fix-gifts \
	dev dev-kill dev-servers dev-servers-kill \
	setup-backend setup-auth setup-frontend setup-gifts \
	test-unit-backend test-unit-auth test-unit-frontend test-unit-gifts \
	test-e2e-playwright test-e2e-playwright-smoke \
	test-integration coverage coverage-backend coverage-auth coverage-frontend coverage-gifts \
	coverage-modules coverage-submodules coverage-all ci acci badge-audit audit-frontend

# --- Monorepo workspace (Phase 1+, config-spec-monorepo.md) ---

install:
	$(UV) sync
	corepack enable
	$(PNPM) install

test-unit-workspace-py:
	$(UV) run pytest tests/migration/test_workspace_import_smoke.py tests/unit -v

test-unit-shared-py:
	$(UV) run pytest packages/shared/tests --cov=metar_shared \
		--cov-config=packages/shared/pyproject.toml --cov-branch --cov-fail-under=95 -v

test-unit-workspace: test-unit-workspace-py test-unit-shared-py test-unit-workspace-js

test-unit-workspace-js:
	$(PNPM) --filter @metar/shared test

test-unit: test-unit-workspace

test: test-unit

tests\:e2e:
	@if [ -f apps/e2e/package.json ]; then \
		cd apps/e2e && $(PNPM) exec playwright test; \
	else \
		$(MAKE) test-e2e-playwright; \
	fi

vendor-sync:
	bash scripts/vendor/sync-iwxxm.sh

lint: lint-backend lint-auth lint-frontend lint-gifts

lint-fix: lint-fix-backend lint-fix-auth lint-fix-frontend lint-fix-gifts

lint-backend:
	cd backend && python3 -m pip install -q ruff && python3 -m ruff check src tests

lint-auth:
	cd auth && python3 -m pip install -q ruff && python3 -m ruff check src tests

lint-frontend:
	cd frontend && npm install --legacy-peer-deps && npm run lint

lint-gifts:
	cd GIFTs && python3 -m pip install -q flake8 && flake8 gifts tests

lint-fix-backend:
	cd backend && python3 -m pip install -q ruff && python3 -m ruff check --fix src tests

lint-fix-auth:
	cd auth && python3 -m pip install -q ruff && python3 -m ruff check --fix src tests

lint-fix-frontend:
	cd frontend && npm install --legacy-peer-deps && npm run lint -- --fix

lint-fix-gifts:
	@echo "No auto-fix configured for GIFTs (flake8 is check-only). Running lint check instead."
	$(MAKE) lint-gifts

dev:
	bash ./start-dev-servers.sh

dev-kill:
	bash ./start-dev-servers.sh --kill

dev-servers: dev

dev-servers-kill: dev-kill

setup-backend:
	cd backend && python3 -m pip install -e .

setup-auth:
	cd auth && python3 -m pip install -e .

setup-frontend:
	cd frontend && npm install --legacy-peer-deps

setup-gifts:
	cd GIFTs && python3 -m pip install -e .

test-unit-legacy: test-unit-backend test-unit-auth test-unit-frontend test-unit-gifts

test-unit-backend:
	cd backend && python3 -m pytest tests/unit --cov=src --cov-config=pyproject.toml --cov-branch --cov-report=xml:coverage.xml --cov-report=term-missing --cov-fail-under=95 -v

test-unit-auth:
	cd auth && python3 -m pip install -q -e . && PYTHONPATH=src python3 -m pytest tests --cov=src --cov-config=pyproject.toml --cov-branch --cov-report=xml:coverage.xml --cov-report=term-missing --cov-fail-under=95 -v

test-unit-frontend:
	cd frontend && npm run test:coverage

audit-frontend:
	cd frontend && npm ci && npm run audit:ci

test-unit-gifts:
	cd GIFTs && python3 -m pytest tests/ --cov=gifts --cov-config=pyproject.toml --cov-report=xml:coverage.xml --cov-report=term-missing --cov-fail-under=95 -v

test-e2e-playwright:
	cd frontend && NODE_PATH=./node_modules npx playwright test

# Smoke subset: runs only the spec files that require no admin credentials.
# Safe to use in CI or local when PLAYWRIGHT_ADMIN_EMAIL / PLAYWRIGHT_ADMIN_PASSWORD
# are not available.  Covers startup health, auth service integration, front-end
# rendering and all mock-session conversion flows.
test-e2e-playwright-smoke:
	cd frontend && NODE_PATH=./node_modules npx playwright test \
		auth-service-integration.e2e.spec.ts \
		tac-file-conversion.e2e.spec.ts

coverage-backend:
	cd backend && python3 -m pytest tests/unit --cov=src --cov-config=pyproject.toml --cov-branch --cov-report=xml:coverage.xml --cov-report=term-missing -v

coverage-auth:
	cd auth && python3 -m pip install -q -e . && PYTHONPATH=src python3 -m pytest tests --cov=src --cov-config=pyproject.toml --cov-branch --cov-report=xml:coverage.xml --cov-report=term-missing -v

coverage-frontend:
	cd frontend && npm run test:coverage

coverage-gifts:
	cd GIFTs && python3 -m pytest tests/ --cov=gifts --cov-config=pyproject.toml --cov-report=xml:coverage.xml --cov-report=term-missing -v

coverage-modules: coverage-backend coverage-auth coverage-frontend coverage-gifts

coverage-submodules:
	@set -e; \
	for dir in data/iwxxm-translation schemas/iwxxm schemas/iwxxm-codelists schemas/iwxxm-modelling; do \
		if [ ! -d "$$dir" ]; then \
			echo "Skipping $$dir (directory not found)"; \
			continue; \
		fi; \
		echo "Running coverage for $$dir"; \
		if [ -f "$$dir/Makefile" ] && grep -qE '^coverage:' "$$dir/Makefile"; then \
			$(MAKE) -C "$$dir" coverage; \
		elif [ -f "$$dir/pyproject.toml" ]; then \
			(cd "$$dir" && python3 -m pytest --cov=. --cov-report=term-missing -v); \
		elif [ -f "$$dir/package.json" ]; then \
			(cd "$$dir" && npm ci && npm run test:coverage); \
		else \
			echo "Skipping $$dir (no supported coverage command found)"; \
		fi; \
	done

coverage-all: coverage-modules coverage-submodules

test-integration:
	python3 -m pip install -q pytest requests httpx
	@set -a; \
	for env_file in .env frontend/.env auth/.env backend/.env; do \
		if [ -f "$$env_file" ]; then \
			while IFS= read -r line || [ -n "$$line" ]; do \
				line="$${line%$$'\r'}"; \
				[[ -z "$$line" || "$$line" =~ ^[[:space:]]*# ]] && continue; \
				export "$$line"; \
			done < "$$env_file"; \
		fi; \
	done; \
	set +a; \
	required_vars="SUPABASE_URL SUPABASE_ANON_KEY VITE_SUPABASE_URL VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY"; \
	missing=""; \
	for var in $$required_vars; do \
		if [ -z "$${!var}" ]; then \
			missing="$$missing $$var"; \
		fi; \
	done; \
	if [ -n "$$missing" ]; then \
		echo "Missing required environment variables for integration tests:"; \
		for var in $$missing; do echo "- $$var"; done; \
		echo "Set these variables in your shell or .env file before running make test-integration."; \
		exit 1; \
	fi
	-$(COMPOSE) down --remove-orphans
	$(COMPOSE) up -d auth backend frontend
	@echo "Waiting for services to become ready..."
	@for i in $$(seq 1 45); do \
		if wget --quiet --tries=1 --timeout=2 -O /dev/null http://localhost:18003/health \
			&& wget --quiet --tries=1 --timeout=2 -O /dev/null http://localhost:18001/health \
			&& wget --quiet --tries=1 --timeout=2 -O /dev/null http://localhost:18000/; then \
			echo "All services are reachable."; \
			break; \
		fi; \
		if [ "$$i" -eq 45 ]; then \
			echo "Services did not become ready in time."; \
			$(COMPOSE) ps; \
			$(COMPOSE) logs --tail=120 auth backend frontend; \
			exit 1; \
		fi; \
		sleep 2; \
	done
	PYTHONPATH=auth/src python3 -m pytest tests/test_backend_auth_integration.py tests/test_backend_frontend_integration.py tests/test_auth_frontend_integration.py tests/test_gifts_backend_integration.py tests/test_integration.py -v
	$(COMPOSE) down

coverage: coverage-modules

badge-audit:
	python3 .github/scripts/badge_audit.py

ci: lint test-unit-legacy test-integration badge-audit

# All CI checks in one command: linting, unit tests, integration tests,
# smoke E2E, frontend dependency audit, and badge verification.
acci: lint test-unit-legacy test-integration test-e2e-playwright-smoke audit-frontend badge-audit
