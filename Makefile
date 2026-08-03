SHELL := /bin/bash
COMPOSE := docker compose
UV := uv
PNPM := pnpm

PY_TREES := apps packages tests
PY_LINT := apps/backend/src apps/backend/tests \
	packages/auth/src \
	packages/shared packages/shared/tests \
	packages/tac2iwxxm/src packages/tac2iwxxm/tests \
	packages/iwxxm-validate/src packages/iwxxm-validate/tests \
	packages/tac-validate/src packages/tac-validate/tests \
	packages/dissemination/src packages/dissemination/tests \
	tests

.PHONY: install test test-unit vendor-sync \
	test-unit-workspace test-unit-workspace-py test-unit-shared-py test-unit-shared-js test-unit-workspace-js \
	test-unit-backend test-unit-frontend \
	test-unit-tac2iwxxm test-unit-iwxxm-validate test-unit-tac-validate \
	test-unit-dissemination test-unit-worker test-bugs \
	db-migrate test-alembic \
	verify-supabase-to-do-migrate migrate-supabase-to-do \
	test-sigmet-quality \
	test-va-sigmet-quality \
	test-tc-sigmet-quality \
	test-airmet-quality \
	test-vaa-quality \
	test-tca-quality \
	test-swxa-quality \
	test-quality-matrices-smoke \
	test-quality-matrices-full \
	test-product-order-smoke \
	test-report-state-matrix-smoke \
	test-wmo-quality \
	test-ahl-com-quality \
	test-metar-quality \
	test-speci-quality \
	test-taf-quality \
	test-integration-dissemination \
	compose-wis2box-up compose-wis2box-down compose-wis2box-harness \
	compose-mock-byoc-up compose-mock-byoc-down compose-mock-byoc-full-up \
	compose-mock-byoc-all-up compose-mock-byoc-all-down \
	test-mock-byoc-smoke test-mock-byoc-compose test-mock-byoc-all-sinks \
	format format-check typecheck typecheck-py typecheck-js \
	lint lint-py lint-js lint-backend lint-auth lint-frontend lint-shared \
	lint-tac2iwxxm lint-iwxxm-validate lint-tac-validate lint-dissemination \
	lint-fix lint-fix-py lint-fix-backend lint-fix-auth lint-fix-frontend \
	dev dev-kill dev-servers dev-servers-kill \
	test-e2e-playwright test-e2e-playwright-smoke test-e2e-t2-product \
	test-live-connectivity test-live-api test-live-integration test-live-e2e test-live-bulletin test-live \
	test-integration coverage coverage-backend coverage-frontend coverage-shared \
	coverage-dissemination coverage-modules coverage-all ci acci badge-audit audit-frontend \
	validate-fast validate-yaml secrets-check config-guard validate-ci env-check \
	install-hooks pre-commit-run pre-push-run ci-prepush \
	catalog-regen catalog-check \
	issue-registry-guard \
	supabase-start supabase-stop supabase-reset supabase-status supabase-push supabase-pull \

# --- Monorepo workspace ---

install:
	$(UV) sync
	corepack enable
	$(PNPM) install

install-hooks:
	# husky owns core.hooksPath (.husky/*); pre-commit framework runs from .husky/pre-commit.
	# Long unit/matrix suites: .husky/pre-push → make validate-ci + make ci-prepush.
	corepack enable
	$(PNPM) install
	$(PNPM) exec husky
	$(UV) run pre-commit install-hooks
	chmod +x .husky/pre-commit .husky/pre-push

pre-commit-run:
	$(UV) run pre-commit run --all-files

pre-push-run:
	# Same as husky pre-push (CI unit/matrix parity; not in GitHub Actions temporarily).
	make validate-ci
	make ci-prepush

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
	$(UV) run basedpyright packages/auth/src
	$(UV) run basedpyright packages/tac2iwxxm/src
	$(UV) run basedpyright packages/iwxxm-validate/src
	$(UV) run basedpyright packages/tac-validate/src
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
	$(UV) run ruff check --force-exclude packages/auth/src

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
	$(UV) run ruff check --fix --force-exclude packages/auth/src

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

# F30 / ADR-033 / TC-EV031-002 — Alembic against DATABASE_URL (idempotent upgrade head).
db-migrate:
	bash scripts/ci/alembic_upgrade.sh

# F30 / TC-EV031-001 / T5.2 — row counts + sample checksum (Supabase → DO).
# Requires MIGRATE_SOURCE_DATABASE_URL (or SUPABASE_DB_URL) and DATABASE_URL.
verify-supabase-to-do-migrate:
	$(UV) run python scripts/ops/verify_supabase_to_do_migrate.py \
		--source-url "$${MIGRATE_SOURCE_DATABASE_URL:-$${SUPABASE_DB_URL}}" \
		--target-url "$${MIGRATE_TARGET_DATABASE_URL:-$${DATABASE_URL}}"

# F30 / TC-EV031-001 / T5.3 — SQL export dry-run (default) or apply cut.
# MODE=dry-run|apply  VERIFY=1 to run T5.2 verify after apply.
# Target MUST be DO Postgres (script refuses same-DB source/target).
migrate-supabase-to-do:
	$(UV) run python scripts/ops/run_supabase_to_do_migrate.py \
		--source-url "$${MIGRATE_SOURCE_DATABASE_URL:-$${SUPABASE_DB_URL}}" \
		--target-url "$${MIGRATE_TARGET_DATABASE_URL:-$${DATABASE_URL}}" \
		--mode "$${MODE:-dry-run}" \
		$$( [ "$${VERIFY:-0}" = "1" ] && echo --verify || true )

test-alembic:
	$(UV) run pytest tests/unit/test_alembic_layout_tc_ev031_002.py \
		tests/integration/test_alembic_upgrade_idempotent.py -v --no-cov

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

# F24/F25 / EV-020 — combined WMO quality pack (E20-F3=3): SIGMET keep-green + AIRMET + METAR/SPECI/TAF
# Extended F26/F27 / EV-021 (S02.L1): + VAA + TCA keyword filters
test-wmo-quality:
	bash scripts/ci/run_wmo_quality.sh

# EV-029 / E29-T4=2 — AHL / COM / shared bulletin pack (M1 / TC-EV029-003)
test-ahl-com-quality:
	bash scripts/ci/run_ahl_com_quality.sh

# EV-029 / E29-T4=2 — METAR quality pack (M2 / TC-EV029-007 + F15 deepen)
test-metar-quality:
	bash scripts/ci/run_metar_quality.sh

# EV-029 / E29-T4=2 — SPECI quality pack (M3 / TC-EV029-007 + F20 deepen)
test-speci-quality:
	bash scripts/ci/run_speci_quality.sh

# EV-029 / E29-T4=2 — TAF quality pack (M4 / TC-EV029-007 + F20 deepen)
test-taf-quality:
	bash scripts/ci/run_taf_quality.sh

# EV-029 / E29-T4=2 — general SIGMET quality pack (M5 / TC-EV029-007 + F23 deepen)
# Replaces the EV-020 thin alias that redirected to test-wmo-quality.
test-sigmet-quality:
	bash scripts/ci/run_sigmet_quality.sh

# EV-029 / E29-T4=2 — VA SIGMET quality pack (M6 / TC-EV029-007 + F23 deepen)
test-va-sigmet-quality:
	bash scripts/ci/run_va_sigmet_quality.sh

# EV-029 / E29-T4=2 — TC SIGMET quality pack (M7 / TC-EV029-004 + F23 deepen / #738)
test-tc-sigmet-quality:
	bash scripts/ci/run_tc_sigmet_quality.sh

# EV-029 / E29-T4=2 — AIRMET quality pack (M8 / TC-EV029-007 + F24 deepen)
test-airmet-quality:
	bash scripts/ci/run_airmet_quality.sh

# EV-029 / E29-T4=2 — VAA quality pack (M9 / TC-EV029-005 + F26 deepen / #820)
test-vaa-quality:
	bash scripts/ci/run_vaa_quality.sh

# EV-029 / E29-T4=2 — TCA quality pack (M10 / TC-EV029-005 + F27 deepen / #820)
test-tca-quality:
	bash scripts/ci/run_tca_quality.sh

# EV-029 / E29-T4=2 — SWXA quality pack (M11 / TC-F28 + F28 deepen / #740/#823)
test-swxa-quality:
	bash scripts/ci/run_swxa_quality.sh

# EV-030 / E30-T7 — F29 quality matrices PR smoke (inventory + ready; excludes full ×20)
test-quality-matrices-smoke:
	bash scripts/ci/run_quality_matrices_smoke.sh

# EV-030 / E30-T7 — F29 full pilot matrices (optional / nightly; includes needs-fixture skips)
test-quality-matrices-full:
	bash scripts/ci/run_quality_matrices_full.sh

# EV-029 / T12.1 — Product-order regression smoke (TC-EV029-007 / M12)
test-product-order-smoke:
	bash scripts/ci/run_product_order_smoke.sh

# EV-029 / T12.2 — Report-state matrix smoke (TC-EV029-006 / M12)
test-report-state-matrix-smoke:
	bash scripts/ci/run_report_state_matrix_smoke.sh

# EV-023 / TC-EV023-005 — Amd79 informative suite (T5.1+T5.2; soft xfail strict=False / E23-T4=2)
test-iwxxm-translation-informative:
	$(UV) run pytest packages/tac2iwxxm/tests \
		-m iwxxm_translation_informative -v --tb=short --no-cov

# F16–F19 / T0.1 — coverage paths; skips until packages/dissemination exists (T1.1/T1.2).
test-unit-dissemination:
	bash scripts/ci/run_dissemination_coverage.sh

# F16 / T2.5 — TC-F16-003 multi-DB (SQLite always; PG/MySQL via Testcontainers when Docker up).
test-integration-dissemination:
	$(UV) run pytest packages/dissemination/tests \
		-m integration -v --tb=short --no-cov

# F17 / E14-04 — wis2box Compose harness (MQTT + HTTP dataset overlay; T3.3).
compose-wis2box-up:
	$(COMPOSE) -f docker-compose.yml -f docker-compose.wis2box.yml --profile wis2box up -d --build --wait wis2box

compose-wis2box-down:
	@$(COMPOSE) -f docker-compose.yml -f docker-compose.wis2box.yml --profile wis2box stop wis2box || true
	@$(COMPOSE) -f docker-compose.yml -f docker-compose.wis2box.yml --profile wis2box rm -f wis2box || true

compose-wis2box-harness:
	bash scripts/ci/run_wis2box_harness.sh

# F16–F19 mock BYOC destinations (Postgres / MySQL / SQL Server / MailHog / F19) — local only.
compose-mock-byoc-up:
	$(COMPOSE) -f docker-compose.yml -f docker-compose.mock-byoc.yml --profile mock-byoc \
		up -d --build --wait byoc-postgres byoc-mysql byoc-sqlserver byoc-mailhog byoc-f19

compose-mock-byoc-down:
	@$(COMPOSE) -f docker-compose.yml -f docker-compose.mock-byoc.yml --profile mock-byoc \
		stop byoc-postgres byoc-mysql byoc-sqlserver byoc-mailhog byoc-f19 || true
	@$(COMPOSE) -f docker-compose.yml -f docker-compose.mock-byoc.yml --profile mock-byoc \
		rm -f byoc-postgres byoc-mysql byoc-sqlserver byoc-mailhog byoc-f19 || true

compose-mock-byoc-full-up:
	$(COMPOSE) -f docker-compose.yml -f docker-compose.mock-byoc.yml -f docker-compose.wis2box.yml \
		--profile mock-byoc --profile wis2box up -d --build --wait \
		byoc-postgres byoc-mysql byoc-sqlserver byoc-mailhog byoc-f19 wis2box

compose-mock-byoc-all-up: compose-mock-byoc-full-up

compose-mock-byoc-all-down: compose-mock-byoc-down compose-wis2box-down

test-unit-worker:
	$(UV) run pytest apps/worker/tests -v --no-cov

test-bugs:
	$(UV) run pytest tests/bugs -m "not live and not live_api" --no-cov -v

test-unit: test-unit-workspace test-unit-backend test-unit-frontend \
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
		tac-file-conversion.e2e.spec.ts

test-e2e-t2-product:
	cd apps/e2e && METAR_CONFIG_ENV=local $(PNPM) exec playwright test tac-file-conversion.e2e.spec.ts

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

# S019 T6.6 — mock BYOC smoke (no live destination credentials; gitignored .env OK)
test-mock-byoc-smoke:
	bash scripts/deploy/run_mock_byoc_smoke.sh

# Compose mock destinations (requires compose-mock-byoc-up)
test-mock-byoc-compose:
	bash scripts/deploy/run_mock_byoc_compose_smoke.sh

# All drawer sinks vs local mocks (requires compose-mock-byoc-all-up)
test-mock-byoc-all-sinks:
	bash scripts/deploy/run_mock_byoc_all_sinks.sh

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

coverage-frontend:
	$(PNPM) --filter @metar/frontend run test:coverage

coverage-shared:
	$(UV) run pytest packages/shared/tests --cov=metar_shared \
		--cov-config=packages/shared/pyproject.toml --cov-report=term-missing -v

coverage-dissemination: test-unit-dissemination

coverage-modules: coverage-backend coverage-frontend coverage-shared \
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
	$(UV) run pytest tests/test_backend_frontend_integration.py tests/test_integration.py -v
	cd apps/backend && $(UV) run pytest tests/integration/test_h0i_connectivity.py tests/unit/test_tc_f21_auth_gone_unit.py -v --no-cov
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

# Unit/matrix parity for pre-push (CI test job packages without local Compose).
# Use `make ci` / `make test-integration` when Docker ports 18000/18001 are free.
ci-prepush: format-check typecheck lint test-unit-workspace test-unit-backend \
	test-unit-frontend test-unit-tac2iwxxm test-unit-iwxxm-validate test-unit-tac-validate \
	test-unit-dissemination test-unit-worker test-bugs badge-audit

ci: ci-prepush test-integration

acci: ci test-e2e-playwright-smoke audit-frontend
