#!/usr/bin/env node
/**
 * ADR-048 TypeScript documentation checker.
 *
 * Presence: every function/class/method (exported and non-exported) needs TSDoc.
 * Exported symbols also need an executable @example (run via run_ts_examples.mjs).
 * Class methods and interface/type members are included (D-EVDOC-LINT-03).
 *
 * [Corpus: adr/ADR-048]
 */
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(process.argv[2] || path.join(__dirname, "../.."));

const SKIP_PARTS = [
  "/node_modules/",
  "/dist/",
  "/build/",
  "/fixtures/",
  "/__tests__/",
  ".test.ts",
  ".test.tsx",
  ".spec.ts",
  ".spec.tsx",
  ".d.ts",
  "/generated/",
];

const SCOPE_DIRS = [
  path.join(ROOT, "apps/frontend/src"),
  // Shipping e2e helpers only (not full Playwright specs)
  path.join(ROOT, "apps/e2e/helpers"),
];

/**
 * @param {string} filePath
 */
function shouldSkip(filePath) {
  const norm = filePath.split(path.sep).join("/");
  // Skip Playwright specs under apps/e2e but keep apps/e2e/helpers
  if (norm.includes("/apps/e2e/") && !norm.includes("/apps/e2e/helpers/")) {
    return true;
  }
  return SKIP_PARTS.some((p) => norm.includes(p));
}

/**
 * @param {string} dir
 * @param {string[]} [out]
 */
function walk(dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, ent.name);
    if (ent.isDirectory()) {
      if (ent.name === "node_modules" || ent.name === "dist") continue;
      walk(full, out);
    } else if (/\.(ts|tsx)$/.test(ent.name) && !shouldSkip(full)) {
      out.push(full);
    }
  }
  return out;
}

/** @typedef {{ line: number, name: string, exported: boolean, kind: string }} SymbolHit */

/**
 * Heuristic scan for functions/classes/methods/members and preceding TSDoc.
 * @param {string} text
 * @returns {{ missingDoc: SymbolHit[], missingExample: SymbolHit[] }}
 */
export function analyze(text) {
  const lines = text.split(/\r?\n/);
  /** @type {SymbolHit[]} */
  const missingDoc = [];
  /** @type {SymbolHit[]} */
  const missingExample = [];

  const topLevel = [
    { re: /^export\s+(?:async\s+)?function\s+(\w+)/, exported: true, kind: "function" },
    {
      re: /^export\s+const\s+(\w+)\s*=\s*(?:async\s*)?(?:\(|function)/,
      exported: true,
      kind: "const-fn",
    },
    { re: /^export\s+(?:abstract\s+)?class\s+(\w+)/, exported: true, kind: "class" },
    { re: /^export\s+(?:type|interface)\s+(\w+)/, exported: true, kind: "type" },
    { re: /^(?:async\s+)?function\s+(\w+)/, exported: false, kind: "function" },
    { re: /^(?:abstract\s+)?class\s+(\w+)/, exported: false, kind: "class" },
  ];

  const CONTROL = new Set([
    "if",
    "for",
    "while",
    "switch",
    "catch",
    "return",
    "throw",
    "super",
    "new",
    "typeof",
    "await",
    "yield",
    "case",
    "default",
    "else",
    "try",
    "finally",
    "function",
    "class",
    "const",
    "let",
    "var",
    "import",
    "export",
    "from",
    "of",
    "in",
    "as",
    "do",
    "void",
    "delete",
    "with",
  ]);

  // Class methods: name(...) { or name(...): T {
  const methodRe =
    /^\s+(?:(?:public|private|protected|static|async|override|readonly|get|set)\s+)*([A-Za-z_]\w*)\s*\([^;]*\)\s*(?::[^{]+)?\{/;

  /** @type {"none"|"class"|"iface"} */
  let block = "none";
  let blockIndent = 0;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    if (/^(?:export\s+)?(?:abstract\s+)?class\s+\w+/.test(trimmed)) {
      block = "class";
      blockIndent = line.match(/^\s*/)?.[0].length ?? 0;
    } else if (/^(?:export\s+)?(?:type|interface)\s+\w+/.test(trimmed)) {
      block = "iface";
      blockIndent = line.match(/^\s*/)?.[0].length ?? 0;
    } else if (block !== "none" && trimmed === "}") {
      const indent = line.match(/^\s*/)?.[0].length ?? 0;
      if (indent <= blockIndent) block = "none";
    }

    let matched = false;
    for (const { re, exported, kind } of topLevel) {
      const m = line.match(re);
      if (!m) continue;
      record(lines, i, m[1], exported, kind, missingDoc, missingExample);
      matched = true;
      break;
    }
    if (matched) continue;

    if (block === "class") {
      const m = line.match(methodRe);
      if (m && m[1] && m[1] !== "constructor" && !CONTROL.has(m[1])) {
        const indent = line.match(/^\s*/)?.[0].length ?? 0;
        if (indent > blockIndent) {
          record(lines, i, m[1], false, "method", missingDoc, missingExample);
        }
      }
    } else if (block === "iface") {
      // Interface method signatures: name(...): Type  (not call sites like foo(false);)
      const methodSig = line.match(
        /^\s+(?:readonly\s+)?([A-Za-z_]\w*)\s*\([^)]*\)\s*:/,
      );
      const name = methodSig?.[1];
      if (name && name !== "constructor" && !CONTROL.has(name)) {
        const indent = line.match(/^\s*/)?.[0].length ?? 0;
        if (indent > blockIndent && !trimmed.startsWith("//") && !trimmed.startsWith("*")) {
          record(lines, i, name, false, "member", missingDoc, missingExample);
        }
      }
    }
  }
  return { missingDoc, missingExample };
}

/**
 * @param {string[]} lines
 * @param {number} i
 * @param {string} name
 * @param {boolean} exported
 * @param {string} kind
 * @param {SymbolHit[]} missingDoc
 * @param {SymbolHit[]} missingExample
 */
function record(lines, i, name, exported, kind, missingDoc, missingExample) {
  const jsdoc = precedingJsdoc(lines, i);
  if (!jsdoc) {
    missingDoc.push({ line: i + 1, name, exported, kind });
  } else if (exported && !/@example\b/.test(jsdoc)) {
    missingExample.push({ line: i + 1, name, exported, kind });
  }
}

/**
 * @param {string[]} lines
 * @param {number} lineIdx
 */
function precedingJsdoc(lines, lineIdx) {
  const chunk = [];
  let i = lineIdx - 1;
  while (i >= 0) {
    const stripped = lines[i].trim();
    if (stripped === "") {
      if (chunk.length) break;
      i -= 1;
      continue;
    }
    const isDoc =
      stripped.startsWith("/**") ||
      stripped.startsWith("*") ||
      stripped.startsWith("*/") ||
      stripped.endsWith("*/");
    if (!isDoc) break;
    chunk.unshift(lines[i]);
    if (stripped.startsWith("/**")) break;
    i -= 1;
  }
  if (!chunk.length) return null;
  const text = chunk.join("\n");
  return /\/\*\*[\s\S]*?\*\//.test(text) ? text : null;
}

function main() {
  const files = SCOPE_DIRS.flatMap((d) => walk(d));
  /** @type {string[]} */
  const violations = [];
  for (const file of files) {
    const text = fs.readFileSync(file, "utf8");
    const { missingDoc, missingExample } = analyze(text);
    const rel = path.relative(ROOT, file);
    for (const hit of missingDoc) {
      violations.push(`${rel}:${hit.line} ${hit.kind} ${hit.name}: missing TSDoc`);
    }
    for (const hit of missingExample) {
      violations.push(`${rel}:${hit.line} ${hit.kind} ${hit.name}: missing @example`);
    }
  }

  console.log(`check-docs-ts scanned_files=${files.length} violations=${violations.length}`);
  for (const v of violations.slice(0, 80)) console.log(v);
  if (violations.length > 80) console.log(`... and ${violations.length - 80} more`);

  if (violations.length) {
    process.exitCode = 1;
    return;
  }

  const harness = path.join(__dirname, "run_ts_examples.mjs");
  const result = spawnSync(process.execPath, [harness, ROOT], { stdio: "inherit" });
  if (result.status !== 0) {
    process.exitCode = result.status || 1;
  }
}

const isMain =
  process.argv[1] &&
  path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);

if (isMain) {
  main();
}
