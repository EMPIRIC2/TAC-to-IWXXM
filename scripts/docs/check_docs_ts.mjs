#!/usr/bin/env node
/**
 * ADR-048 TypeScript documentation checker.
 *
 * Presence: every function/class/method (exported and non-exported) needs TSDoc.
 * Exported symbols also need an executable @example (run via run_ts_examples.mjs).
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
  "/e2e/",
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

function shouldSkip(filePath) {
  const norm = filePath.split(path.sep).join("/");
  return SKIP_PARTS.some((p) => norm.includes(p));
}

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
 * Heuristic scan for functions/classes/methods and preceding TSDoc.
 * @param {string} text
 * @returns {{ missingDoc: SymbolHit[], missingExample: SymbolHit[] }}
 */
function analyze(text) {
  const lines = text.split(/\r?\n/);
  /** @type {SymbolHit[]} */
  const missingDoc = [];
  /** @type {SymbolHit[]} */
  const missingExample = [];

  const patterns = [
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

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const { re, exported, kind } of patterns) {
      const m = line.match(re);
      if (!m) continue;
      const name = m[1];
      if (!name) continue;
      const jsdoc = precedingJsdoc(lines, i);
      if (!jsdoc) {
        missingDoc.push({ line: i + 1, name, exported, kind });
      } else if (exported && !/@example\b/.test(jsdoc)) {
        missingExample.push({ line: i + 1, name, exported, kind });
      }
      break;
    }
  }
  return { missingDoc, missingExample };
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

  // Executable harness (same target)
  const harness = path.join(__dirname, "run_ts_examples.mjs");
  const result = spawnSync(process.execPath, [harness, ROOT], { stdio: "inherit" });
  if (result.status !== 0) {
    process.exitCode = result.status || 1;
  }
}

main();
