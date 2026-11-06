import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import jsdoc from "eslint-plugin-jsdoc";

/** ADR-056 — FE paths grandfathered for max-lines / complexity. */
const _repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const _allowlistPath = path.join(_repoRoot, "config/file-budget-allowlist.txt");
const _budgetAllowlistFe = fs.existsSync(_allowlistPath)
  ? fs
      .readFileSync(_allowlistPath, "utf8")
      .split("\n")
      .map((line) => line.split("#", 1)[0].trim())
      .filter((line) => line.startsWith("apps/frontend/"))
      .map((line) => line.slice("apps/frontend/".length))
  : [];
const _complexityAllowlistPath = path.join(
  _repoRoot,
  "config/eslint-complexity-allowlist.txt",
);
const _complexityAllowlistFe = fs.existsSync(_complexityAllowlistPath)
  ? fs
      .readFileSync(_complexityAllowlistPath, "utf8")
      .split("\n")
      .map((line) => line.split("#", 1)[0].trim())
      .filter(Boolean)
  : [];
const _feBudgetOverrides = [
  ...new Set([..._budgetAllowlistFe, ..._complexityAllowlistFe]),
];

export default tseslint.config(
  {
    ignores: [
      "dist/",
      "coverage/",
      "playwright-report/",
      "node_modules/",
      "src/generated/**",
    ],
  },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ["**/*.{ts,tsx}"],
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
      jsdoc,
    },
    settings: {
      jsdoc: {
        mode: "typescript",
      },
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/no-empty-object-type": "error",
      "@typescript-eslint/no-require-imports": "error",
      "no-console": "off",
      // ADR-056 file budget + complexity (allowlisted / ui overridden below)
      "max-lines": ["error", { max: 500, skipBlankLines: false, skipComments: false }],
      complexity: ["error", 10],
      // ADR-048 / EV-adr048-doc-linters (TC-EVDOC-009) — presence via eslint-plugin-jsdoc.
      // Executable @example remains enforced by scripts/docs/check_docs_ts.mjs + harness.
      "jsdoc/require-jsdoc": [
        "error",
        {
          publicOnly: false,
          require: {
            FunctionDeclaration: true,
            MethodDefinition: true,
            ClassDeclaration: true,
            ArrowFunctionExpression: false,
            FunctionExpression: false,
            ClassExpression: false,
          },
          contexts: [
            "TSMethodSignature",
            "MethodDefinition",
            "ClassDeclaration",
            "FunctionDeclaration",
          ],
          checkConstructors: false,
          checkGetters: true,
          checkSetters: true,
        },
      ],
      "jsdoc/require-description": [
        "error",
        {
          contexts: ["any"],
        },
      ],
    },
  },
  {
    files: ["**/*.test.{ts,tsx}", "src/test/**/*.{ts,tsx}"],
    rules: {
      "jsdoc/require-jsdoc": "off",
      "jsdoc/require-description": "off",
    },
  },
  {
    // ADR-056 — shadcn UI kit excluded from line/complexity budget
    files: ["src/app/components/ui/**/*.{ts,tsx}"],
    rules: {
      "max-lines": "off",
      complexity: "off",
    },
  },
  {
    // ADR-056 — grandfather oversize / high-complexity FE modules
    files: _feBudgetOverrides,
    rules: {
      "max-lines": "off",
      complexity: "off",
    },
  },
);
