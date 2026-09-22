import js from "@eslint/js";
import tseslint from "typescript-eslint";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import jsdoc from "eslint-plugin-jsdoc";

export default tseslint.config(
  { ignores: ["dist/", "coverage/", "playwright-report/", "node_modules/"] },
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
);
