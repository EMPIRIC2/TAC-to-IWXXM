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

.PHONY: install test test-unit vendor-sync export-iwxxm-versions openapi-refresh tip-diff-iwxxm \
	iwxxm-us-compat-smoke codelist-uri-drift \
	test-unit-workspace test-unit-workspace-py test-unit-shared-py test-unit-shared-js test-unit-workspace-js \
	test-unit-backend test-unit-auth test-unit-frontend \
	test-unit-tac2iwxxm test-unit-iwxxm-validate test-unit-tac-validate \
	test-unit-dissemination test-unit-worker test-bugs \
	test-schemathesis test-mutation test-mutation-poc test-mutation-python test-mutation-js \
	build-tac2iwxxm-native build-iwxxm-validate-native \
	test-tac2iwxxm-native test-iwxxm-validate-native rust-check \
	perf-converter-baseline test-converter-pr-gate test-unit-fast lint-fast \
	db-migrate test-alembic \
	verify-supabase-to-do-migrate migrate-supabase-to-do \
	test-sigmet-quality \
	test-va-sigmet-quality \
	test-tc-sigmet-quality \
	test-ev032-a6-2-canary \
	test-ev032-vona-canary \
	test-airmet-quality \
	test-vaa-quality \
	test-tca-quality \
	test-swxa-quality \
	test-vona-quality \
	test-provenance-quality \
	test-provenance-canary \
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
	test-e2e-f16-live-sql \
	test-live-connectivity test-live-connectivity-doks-provisional test-live-topology-doks-provisional test-live-api test-live-integration test-live-e2e test-live-e2e-doks-provisional test-live-bulletin test-live \
	test-integration test-coverage-scripts test-bats \
	coverage coverage-backend coverage-frontend coverage-shared \
	coverage-dissemination coverage-modules coverage-all ci acci badge-audit audit-frontend \
	validate-fast validate-yaml secrets-check config-guard validate-ci env-check \
	install-hooks pre-commit-run pre-push-run ci-prepush \
	catalog-regen catalog-check \
	membership-regen membership-check \
	ca-ops-harvest ca-ops-check \
	generate-quality-metrics \
	issue-registry-guard \
	supabase-start supabase-stop supabase-reset supabase-status supabase-push supabase-pull \

# --- Monorepo workspace ---

install:
	$(UV) sync
	corepack enable
	$(PNPM) install

install-hooks:
	# husky owns core.hooksPath (.husky/*).
	# EV-047: commit = lint-fast; push = test-unit-fast (heavier gates → CI / opt-in make).
	corepack enable
	$(PNPM) install
	$(PNPM) exec husky
	$(UV) run pre-commit install-hooks
	chmod +x .husky/pre-commit .husky/pre-push

# EV-047 / #833 — husky pre-commit lint/format only (shape A).
lint-fast:
	$(UV) run pre-commit run ruff-format --all-files
	$(UV) run pre-commit run ruff-check --all-files
	$(UV) run pre-commit run prettier-check --all-files
	$(UV) run pre-commit run eslint --all-files

pre-commit-run:
	# Opt-in full local parity (not husky default after EV-047).
	$(UV) run pre-commit run --all-files
	$(MAKE) validate-ci-medium

pre-push-run:
	# Same as husky pre-push (EV-047): fast units only.
	$(MAKE) test-unit-fast

# --- F15 issue catalog (ADR-028 / EV-011) ---

catalog-regen:
	$(UV) run python scripts/tac-validate/regen_issue_catalog.py

catalog-check: catalog-regen
	@git diff --quiet -- docs/domain/rules/ISSUE_CATALOG.md docs/domain/rules/ISSUE_CATALOG.json \
		packages/tac-validate/src/tac_validate/data/catalog_attribution.json \
		|| (echo "ISSUE_CATALOG drift — run make catalog-regen and commit"; git diff --stat -- docs/domain/rules/ISSUE_CATALOG.md docs/domain/rules/ISSUE_CATALOG.json packages/tac-validate/src/tac_validate/data/catalog_attribution.json; exit 1)

# S059 / EV-050 / AC1 — offline WMO membership harvest (no live codes.wmo.int HTML)
# Prettier after dump so short arrays match workspace format-check (json.dumps expands them).
membership-regen:
	$(UV) run python scripts/iwxxm/harvest_wmo_membership.py
	pnpm exec prettier --write packages/tac-validate/src/tac_validate/data/wmo_membership.json

# EV-054 / F7.q — regenerate precomputed Quality metrics corpus artifact
generate-quality-metrics:
	$(UV) run python scripts/ci/generate_quality_metrics.py

membership-check: membership-regen
	@git diff --quiet -- packages/tac-validate/src/tac_validate/data/wmo_membership.json \
		|| (echo "wmo_membership.json drift — run make membership-regen and commit"; \
		git diff --stat -- packages/tac-validate/src/tac_validate/data/wmo_membership.json; exit 1)

# EV-072 M2 / #1036 — offline CA_ECCC MSC datamart ops corpus (pin-date harvest)
ca-ops-harvest:
	$(UV) run python scripts/iwxxm/harvest_ca_eccc_ops.py --pin-date 2026-08-24
	$(UV) run python scripts/iwxxm/harvest_ca_eccc_vaac_tac.py --pin-date 2026-08-24

ca-ops-check: ca-ops-harvest
	@git diff --quiet -- packages/tac2iwxxm/tests/fixtures/profiles/CA_ECCC/ops_manifest.json \
		|| (echo "ops_manifest.json drift — run make ca-ops-harvest and commit"; \
		git diff --stat -- packages/tac2iwxxm/tests/fixtures/profiles/CA_ECCC/ops_manifest.json; exit 1)

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
		--cov-config=packages/shared/pyproject.toml --cov-branch \
		--cov-report=json:packages/shared/coverage.json --cov-fail-under=100 -v
	$(UV) run python scripts/ci/check_per_file_coverage.py packages/shared/coverage.json

test-unit-shared-js:
	$(PNPM) --filter @metar/shared run test:coverage

test-unit-workspace-js:
	$(PNPM) --filter @metar/shared test

test-unit-workspace: test-unit-workspace-py test-unit-shared-py test-unit-shared-js

test-unit-backend:
	(cd apps/backend && $(UV) run pytest tests/unit \
		--cov=src --cov-config=pyproject.toml --cov-branch \
		--cov-report=xml:coverage.xml --cov-report=json:coverage.json \
		--cov-report=term-missing \
		--cov-fail-under=100 -v)
	$(UV) run python scripts/ci/check_per_file_coverage.py apps/backend/coverage.json

# F34 / EV-059 / #727 — Schemathesis OpenAPI property suite (TC-F34-001..002 / TC-F34-007).
# Knobs: SCHEMATHESIS_MAX_EXAMPLES (≤25), Hypothesis seed via --hypothesis-seed.
# Budget ceiling locked — do not raise max-examples above 25 without AskQuestion.
test-schemathesis:
	(cd apps/backend && SCHEMATHESIS_MAX_EXAMPLES=$${SCHEMATHESIS_MAX_EXAMPLES:-25} \
		$(UV) run pytest tests/contract/test_schemathesis_openapi.py \
		-m schemathesis --override-ini addopts= -v \
		--tb=short)

# F34 / EV-059 / #874 — Mutation testing (TC-F34-003..005). Nightly/manual only.
# Usage: make test-mutation-python TARGET=poc-shared-env
#        make test-mutation-js TARGET=frontend
#        make test-mutation-poc   # narrow Python + docs note
# Knobs: MUTATION_TIMEOUT_SEC (default 1200), GREMLIN_EXTRA_ARGS
test-mutation-python:
	@test -n "$(TARGET)" || (echo "Set TARGET=backend|worker|auth|shared|tac-validate|tac2iwxxm|iwxxm-validate|dissemination|poc-shared-env" >&2; exit 2)
	bash scripts/ci/run_mutation_python.sh "$(TARGET)"

test-mutation-js:
	@test -n "$(TARGET)" || (echo "Set TARGET=frontend|shared" >&2; exit 2)
	bash scripts/ci/run_mutation_js.sh "$(TARGET)"

test-mutation-poc:
	MUTATION_TIMEOUT_SEC=$${MUTATION_TIMEOUT_SEC:-300} bash scripts/ci/run_mutation_python.sh poc-shared-env

test-mutation: test-mutation-poc
	@echo "Full matrix: workflow .github/workflows/mutation.yml (schedule / workflow_dispatch)"
	@echo "Chunked local: make test-mutation-python TARGET=… / make test-mutation-js TARGET=…"

# F31 / EV-047 — auth package + per-file ≥95%.
test-unit-auth:
	$(UV) run pytest tests/unit/auth --cov=metar_auth \
		--cov-config=packages/auth/pyproject.toml --cov-branch \
		--cov-report=json:packages/auth/coverage.json \
		--cov-report=term-missing --cov-fail-under=100 -v
	$(UV) run python scripts/ci/check_per_file_coverage.py packages/auth/coverage.json

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
		--cov-report=json:packages/tac2iwxxm/coverage.json \
		--cov-report=term-missing --cov-fail-under=100 -v
	$(UV) run python scripts/ci/check_per_file_coverage.py packages/tac2iwxxm/coverage.json

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

# EV-045 / TC-EV045-005 — local mirror of CI: fmt + clippy + cargo test both crates + maturin smokes.
# PYO3_PYTHON pins uv's interpreter so host 3.14+ does not break PyO3 build scripts.
rust-check:
	@PYO3_PYTHON="$$($(UV) run python -c 'import sys; print(sys.executable)')"; \
	export PYO3_PYTHON; \
	(cd packages/tac2iwxxm/rust && cargo fmt --check && cargo clippy -- -D warnings && cargo test) && \
	(cd packages/iwxxm-validate/rust && cargo fmt --check && cargo clippy -- -D warnings && cargo test)
	$(MAKE) test-tac2iwxxm-native
	$(MAKE) test-iwxxm-validate-native

# EV-047 / #834 — re-record converter PR baselines (explicit; never on gate failure).
# On CI: make perf-converter-baseline HOST=ubuntu-latest STATUS=ci_recorded
perf-converter-baseline:
	PYTHONPATH=. $(UV) run python scripts/bench/record_converter_pr_baselines.py \
		--host "$(or $(HOST),$(shell uname -s))" \
		--status "$(or $(STATUS),ci_recorded)"

# EV-047 hard gate suite (TC-EV047-005..008).
test-converter-pr-gate:
	$(UV) run pytest tests/perf/test_converter_pr_gate.py -v --no-cov

# EV-047 / #833 — husky pre-push fast unit subset (shape A).
test-unit-fast: test-unit-workspace test-unit-tac2iwxxm

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

# S046 / EV-038 / #851 — Python SoT → FE generated JSON (D-S046-sot)
export-iwxxm-versions:
	$(UV) run python scripts/iwxxm/export_iwxxm_versions.py

# EV-052 / #900 — FastAPI OpenAPI snapshot + openapi-typescript FE types (D-S061-openapi-src)
openapi-refresh:
	$(UV) run python scripts/openapi/export_openapi.py
	$(PNPM) --filter @metar/frontend run openapi:generate

# S046 / EV-038 / #852 — XSD/SCH/example stem deltas between vendor pins
tip-diff-iwxxm:
	$(UV) run python scripts/vendor/tip_diff_iwxxm.py --from 2023-1 --to 2025-2

# S046 / EV-038 / #853 — iwxxm-us gate report + annex3/US smoke (D-S046-853)
iwxxm-us-compat-smoke:
	$(UV) run python scripts/iwxxm/iwxxm_us_compat_gate.py --smoke

# S046 / EV-038 / #859 — SCH RDF ↔ codelist CSV URI drift (D-S046-859; non-flake)
codelist-uri-drift:
	$(UV) run python scripts/iwxxm/codelist_uri_drift.py

test-unit-iwxxm-validate:
	$(UV) run pytest packages/iwxxm-validate/tests --cov=iwxxm_validate \
		--cov-config=packages/iwxxm-validate/pyproject.toml --cov-branch \
		--cov-report=json:packages/iwxxm-validate/coverage.json \
		--cov-report=term-missing --cov-fail-under=100 -v
	$(UV) run python scripts/ci/check_per_file_coverage.py packages/iwxxm-validate/coverage.json

test-unit-tac-validate:
	$(UV) run pytest packages/tac-validate/tests --cov=tac_validate \
		--cov-config=packages/tac-validate/pyproject.toml --cov-branch \
		--cov-report=json:packages/tac-validate/coverage.json \
		--cov-report=term-missing --cov-fail-under=100 -v
	$(UV) run python scripts/ci/check_per_file_coverage.py packages/tac-validate/coverage.json

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
# EV-032 / E32-T7 — includes #835 A6-2-TC ADR-032 equality + catalog wmoPass (long pack).
# Fast canary: scripts/ci/run_ev032_a6_2_tc_canary.sh (path-filtered pre-commit).
test-tc-sigmet-quality:
	bash scripts/ci/run_tc_sigmet_quality.sh

# EV-032 / E32-T7 / T1.5 — path-filtered pre-commit canary (A6-2 equality + catalog)
test-ev032-a6-2-canary:
	bash scripts/ci/run_ev032_a6_2_tc_canary.sh

# EV-032 / E32-T7 / T2.8 — path-filtered pre-commit canary (VONA ADR-032 + product enum)
test-ev032-vona-canary:
	bash scripts/ci/run_ev032_vona_canary.sh

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

# EV-032 / E32-T7 / T2.8 — VONA quality pack (M2 / TC-F32 + F32 deepen / #741)
test-vona-quality:
	bash scripts/ci/run_vona_quality.sh

# EV-035 / EV-037 — rule-source provenance (TC-EV035-001..006 + TC-EV037)
test-provenance-quality:
	bash scripts/ci/run_provenance_quality.sh

# EV-035/037 — path-filtered pre-commit canary (dig inventory + gap gate)
test-provenance-canary:
	bash scripts/ci/run_provenance_canary.sh

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
# Use a dedicated compose project so `down -v` cannot tear down backend/frontend (EV-039 / AC4).
BYOC_COMPOSE_PROJECT := metar-iwxxm-mock-byoc
BYOC_COMPOSE := $(COMPOSE) -p $(BYOC_COMPOSE_PROJECT) \
	-f docker-compose.yml -f docker-compose.mock-byoc.yml --profile mock-byoc

compose-mock-byoc-up:
	@set -e; \
	if [ "$(F16_SKIP_SQLSERVER)" = "1" ] || [ "$(F16_LIVE_SQL_SERVER)" = "0" ]; then \
		$(BYOC_COMPOSE) up -d --build --wait byoc-postgres byoc-mysql byoc-mailhog byoc-f19; \
	else \
		$(BYOC_COMPOSE) up -d --build --wait byoc-postgres byoc-mysql byoc-sqlserver byoc-mailhog byoc-f19; \
	fi

compose-mock-byoc-down:
	@$(BYOC_COMPOSE) down -v --remove-orphans || true

compose-mock-byoc-full-up:
	$(COMPOSE) -p $(BYOC_COMPOSE_PROJECT) -f docker-compose.yml -f docker-compose.mock-byoc.yml -f docker-compose.wis2box.yml \
		--profile mock-byoc --profile wis2box up -d --build --wait \
		byoc-postgres byoc-mysql byoc-sqlserver byoc-mailhog byoc-f19 wis2box

compose-mock-byoc-all-up: compose-mock-byoc-full-up

compose-mock-byoc-all-down: compose-mock-byoc-down compose-wis2box-down

# F8 / EV-047 T2.5.4 — package + per-file ≥95% for metar_worker (unit only).
test-unit-worker:
	$(UV) run pytest apps/worker/tests -m unit \
		--cov=metar_worker --cov-config=apps/worker/pyproject.toml --cov-branch \
		--cov-report=term-missing --cov-report=json:apps/worker/coverage.json \
		--cov-fail-under=100 -v
	@if [ -f scripts/ci/check_per_file_coverage.py ]; then \
		$(UV) run python scripts/ci/check_per_file_coverage.py apps/worker/coverage.json; \
	fi

# EV-080 / #1077 — scripts Python coverage (D-TP080-3). fail_under 100 + per-file.
# Hyphenated dirs (tac-validate, test-data) are not importable subpackages — extra --cov=.
test-coverage-scripts:
	@set -e; \
	if ! find tests/scripts -type f \( -name 'test_*.py' -o -name '*_test.py' \) 2>/dev/null | grep -q .; then \
		echo "[test-coverage-scripts] error: no tests under tests/scripts/ (EV-080 M4)." >&2; \
		exit 1; \
	fi; \
	$(UV) run pytest tests/scripts \
		--cov=scripts \
		--cov=scripts/tac-validate/regen_issue_catalog.py \
		--cov=scripts/test-data/export_tc_m003_golden.py \
		--cov-config=tests/scripts/coveragerc \
		--cov-branch \
		--cov-report=term-missing \
		--cov-report=json:scripts/coverage.json \
		--cov-fail-under=100 -v; \
	$(UV) run python scripts/ci/check_per_file_coverage.py scripts/coverage.json --min-pct 100

# EV-080 / #1077 — bats-core for every scripts/**/*.sh (D-TP080-2).
test-bats:
	@set -e; \
	if ! find tests/bats -type f -name '*.bats' 2>/dev/null | grep -q .; then \
		echo "[test-bats] error: no *.bats under tests/bats/ (EV-080 M4)." >&2; \
		exit 1; \
	fi; \
	if ! command -v bats >/dev/null 2>&1; then \
		echo "[test-bats] error: bats not on PATH — install bats-core (brew/apt) or enable CI install step." >&2; \
		exit 1; \
	fi; \
	bats $$(find tests/bats -type f -name '*.bats' | sort)

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
	export LIVE_API_URL="$${LIVE_API_URL:-http://api.doks.placeholder.metar-iwxxm.local}"; \
	export LIVE_FRONTEND_URL="$${LIVE_FRONTEND_URL:-http://app.doks.placeholder.metar-iwxxm.local}"; \
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

# T7.2 / EV-031 — H0c + H4 + H5 against provisional DOKS (Host-header; no /etc/hosts)
test-live-connectivity-doks-provisional:
	@$(load_dotenv); \
	set -a; source scripts/deploy/doks_provisional_live_env.sh; set +a; \
	bash scripts/deploy/verify_connectivity.sh

# T7.3 / EV-031 — TC-EV031-003/004 live probes on provisional DOKS topology
test-live-topology-doks-provisional:
	@$(load_dotenv); \
	set -a; source scripts/deploy/doks_provisional_live_env.sh; set +a; \
	$(UV) run pytest tests/live/test_tc_ev031_doks_topology.py -m live -v --tb=short --no-cov

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
	@if [ "$(F16_LIVE_SQL)" = "1" ]; then $(MAKE) test-e2e-f16-live-sql; fi

# EV-039 / AC7 — F16 live local SQL Playwright (Compose). Default on locally; off in CI (S05.M2).
# SQL Server may be omitted via F16_SKIP_SQLSERVER=1 or F16_LIVE_SQL_SERVER=0 (S05.L1 / Apple Silicon).
F16_LIVE_SQL ?= $(if $(CI),0,1)
F16_SKIP_SQLSERVER ?= 0

test-e2e-f16-live-sql:
	@set -e; \
	$(MAKE) compose-mock-byoc-up F16_SKIP_SQLSERVER="$(F16_SKIP_SQLSERVER)" F16_LIVE_SQL_SERVER="$(F16_LIVE_SQL_SERVER)"; \
	trap '$(MAKE) -C "$(CURDIR)" compose-mock-byoc-down' EXIT; \
	if docker inspect metar-iwxxm-backend >/dev/null 2>&1; then \
		docker network connect metar-iwxxm-mock-byoc_metar-network metar-iwxxm-backend 2>/dev/null || true; \
	fi; \
	cd apps/e2e && F16_LIVE_SQL=1 F16_SKIP_SQLSERVER="$(F16_SKIP_SQLSERVER)" F16_LIVE_SQL_SERVER="$(F16_LIVE_SQL_SERVER)" \
		PLAYWRIGHT_SKIP_WEBSERVER=1 F16_DOCKER_API="$${F16_DOCKER_API:-1}" \
		PLAYWRIGHT_BASE_URL="$${PLAYWRIGHT_BASE_URL:-http://localhost:18000}" \
		PLAYWRIGHT_API_BASE_URL="$${PLAYWRIGHT_API_BASE_URL:-http://localhost:18001}" \
		$(PNPM) exec playwright test uj027-f16-live-sql.e2e.spec.ts

# T7.1 / EV-031 — F31 UJ-045..047 against provisional DOKS (Host-header / resolver-rules)
test-live-e2e-doks-provisional:
	@$(load_dotenv); \
	set -a; source scripts/deploy/doks_provisional_live_env.sh; set +a; \
	cd apps/e2e && DISABLE_AUTH=false \
		PLAYWRIGHT_DOKS_PROVISIONAL=1 \
		PLAYWRIGHT_BASE_URL="$$PLAYWRIGHT_BASE_URL" \
		PLAYWRIGHT_API_BASE_URL="$$PLAYWRIGHT_API_BASE_URL" \
		DOKS_LB_IP="$$DOKS_LB_IP" \
		DOKS_API_HOST="$$DOKS_API_HOST" \
		DOKS_FE_HOST="$$DOKS_FE_HOST" \
		E2E_USER_EMAIL="$$E2E_USER_EMAIL" \
		E2E_USER_PASSWORD="$$E2E_USER_PASSWORD" \
		$(PNPM) exec playwright test \
			uj045-047-f31-hybrid-sessions.e2e.spec.ts \
			auth.e2e.spec.ts \
			public-app-f21-f22.e2e.spec.ts

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
	$(COMPOSE) up -d --build backend frontend
	@echo "Waiting for services to become ready..."
	@for i in $$(seq 1 60); do \
		if curl -fsS --max-time 2 -o /dev/null http://localhost:18001/health \
			&& curl -fsS --max-time 2 -o /dev/null http://localhost:18000/; then \
			echo "All services are reachable."; \
			break; \
		fi; \
		if [ "$$i" -eq 60 ]; then \
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
	$(UV) run python scripts/deploy/validate_ingest_poller_url.py --print-fixture >/dev/null
	$(UV) run pytest apps/worker/tests/test_validate_ingest_poller_url.py \
		tests/bugs/test_bug_2026_08_04_worker_placeholder_poller_url.py -q --no-cov

env-check:
	bash scripts/env/verify-sync.sh

# EV-033 / F8 — DOKS worker poller preflight (requires kubectl + cluster context)
doks-worker-poller-preflight:
	bash scripts/deploy/doks_worker_poller_preflight.sh --probe

doks-worker-crashloop-check:
	bash scripts/deploy/check_worker_crashloop.sh

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

# Medium extras after husky/pre-commit fast hooks (validate-ci without validate-fast).
validate-ci-medium: config-guard env-check audit-frontend

validate-ci: validate-fast validate-ci-medium

# Unit/matrix suite without Compose (also run on remote CI test matrix).
# Use `make ci` / `make test-integration` when Docker ports 18000/18001 are free.
ci-prepush: format-check typecheck lint test-unit-workspace test-unit-backend \
	test-unit-frontend test-unit-tac2iwxxm test-unit-iwxxm-validate test-unit-tac-validate \
	test-unit-dissemination test-unit-worker test-bugs badge-audit

# EV-036 long local gate (husky pre-push): units + Compose integration.
ci: ci-prepush test-integration

acci: ci test-e2e-playwright-smoke audit-frontend
