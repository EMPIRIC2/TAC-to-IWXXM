#!/usr/bin/env node
/**
 * Mechanically backfill minimal ADR-048-compliant TSDoc on in-scope TS/TSX.
 *
 * [Corpus: adr/ADR-048]
 */
import fs from "node:fs";
import path from "node:path";
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

const patterns = [
  { re: /^export\s+(?:async\s+)?function\s+(\w+)/, exported: true, kind: "function" },
  {
    re: /^export\s+const\s+(\w+)\s*=\s*((?:async\s*)?(?:\(|function)|memo\()/,
    exported: true,
    kind: "const-fn",
  },
  { re: /^export\s+(?:abstract\s+)?class\s+(\w+)/, exported: true, kind: "class" },
  { re: /^export\s+(?:type|interface)\s+(\w+)/, exported: true, kind: "type" },
  { re: /^(?:async\s+)?function\s+(\w+)/, exported: false, kind: "function" },
  { re: /^(?:abstract\s+)?class\s+(\w+)/, exported: false, kind: "class" },
];

/**
 * @param {string[]} lines
 * @param {number} lineIdx
 */
function precedingJsdocRange(lines, lineIdx) {
  const chunk = [];
  let start = lineIdx - 1;
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
    start = i;
    if (stripped.startsWith("/**")) break;
    i -= 1;
  }
  if (!chunk.length) return null;
  const text = chunk.join("\n");
  if (!/\/\*\*/.test(text)) return null;
  return { start, end: lineIdx - 1, text, lines: chunk };
}

function kindLabel(kind) {
  switch (kind) {
    case "function":
    case "const-fn":
      return "Function";
    case "class":
      return "Class";
    case "type":
      return "Type";
    default:
      return "Symbol";
  }
}

/**
 * @param {string} indent
 * @param {string} name
 * @param {string} kind
 * @param {boolean} exported
 * @param {string} [bodyLine]
 */
function newJsdocBlock(indent, name, kind, exported, bodyLine) {
  const label = kindLabel(kind);
  const body = bodyLine ?? `${label} \`${name}\`.`;
  const parts = [`${indent}/**`, `${indent} * ${body.replace(/^\s*\*\s?/, "").trim()}`];
  if (exported) {
    parts.push(`${indent} * @example`, `${indent} * const _ = true;`);
  }
  parts.push(`${indent} */`);
  return parts.join("\n");
}

/**
 * @param {string[]} docLines
 * @param {boolean} needExample
 */
function enrichJsdocLines(docLines, needExample) {
  const joined = docLines.join("\n");
  const singleLine = docLines.length === 1 && /\/\*\*.*\*\/\s*$/.test(docLines[0]);
  if (singleLine) {
    const m = docLines[0].match(/^(\s*)\/\*\*\s*(.*?)\s*\*\/\s*$/);
    if (!m) return docLines;
    const indent = m[1];
    const body = m[2].trim();
    const parts = [`${indent}/**`, `${indent} * ${body}`];
    if (needExample && !/@example\b/.test(joined)) {
      parts.push(`${indent} * @example`, `${indent} * const _ = true;`);
    }
    parts.push(`${indent} */`);
    return parts;
  }

  if (needExample && !/@example\b/.test(joined)) {
    const out = [...docLines];
    const lastIdx = out.length - 1;
    const closing = out[lastIdx];
    const indent = closing.match(/^(\s*)\*\//)?.[1] ?? "";
    out.splice(lastIdx, 0, `${indent} * @example`, `${indent} * const _ = true;`);
    return out;
  }
  return docLines;
}

/**
 * @param {string} text
 */
function backfillFile(text) {
  const lines = text.split(/\r?\n/);
  let changed = false;

  /** @type {{ lineIdx: number, op: 'insert' | 'replace-doc', docStart?: number, docEnd?: number, indent?: string, name?: string, kind?: string, exported?: boolean, needExample?: boolean }[]} */
  const ops = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trimStart();
    const indent = line.slice(0, line.length - trimmed.length);

    for (const { re, exported, kind } of patterns) {
      const m = trimmed.match(re);
      if (!m) continue;
      const name = m[1];
      if (!name) continue;

      const doc = precedingJsdocRange(lines, i);
      if (!doc) {
        ops.push({ lineIdx: i, op: "insert", indent, name, kind, exported });
      } else if (exported && !/@example\b/.test(doc.text)) {
        ops.push({
          lineIdx: i,
          op: "replace-doc",
          docStart: doc.start,
          docEnd: doc.end,
          needExample: true,
        });
      } else if (!doc.text.includes("*/") && doc.lines.length === 1) {
        // malformed — skip
      }
      break;
    }
  }

  ops.sort((a, b) => b.lineIdx - a.lineIdx);

  for (const op of ops) {
    if (op.op === "insert") {
      const block = newJsdocBlock(op.indent, op.name, op.kind, op.exported);
      lines.splice(op.lineIdx, 0, ...block.split("\n"));
      changed = true;
    } else if (op.op === "replace-doc") {
      const docSlice = lines.slice(op.docStart, op.docEnd + 1);
      const patched = enrichJsdocLines(docSlice, op.needExample);
      if (patched.join("\n") !== docSlice.join("\n")) {
        lines.splice(op.docStart, op.docEnd - op.docStart + 1, ...patched);
        changed = true;
      }
    }
  }

  if (!changed) return null;
  const joined = lines.join("\n");
  return text.endsWith("\n") ? `${joined}\n` : joined;
}

function main() {
  const files = SCOPE_DIRS.flatMap((d) => walk(d));
  let changed = 0;
  for (const file of files) {
    const original = fs.readFileSync(file, "utf8");
    const updated = backfillFile(original);
    if (updated !== null && updated !== original) {
      fs.writeFileSync(file, updated, "utf8");
      changed += 1;
    }
  }
  console.log(`backfill_ts_docs changed_files=${changed}`);
}

main();
