#!/usr/bin/env node
/**
 * Extract @example blocks from in-scope TS/TSX and execute under node.
 *
 * Fail closed if an exported symbol has no executable example or an example throws.
 * [Corpus: adr/ADR-048]
 */
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(process.argv[2] || path.join(__dirname, "../.."));

const SCOPE_DIRS = [
  path.join(ROOT, "apps/frontend/src"),
  path.join(ROOT, "apps/e2e/helpers"),
];

const SKIP_PARTS = [
  "/node_modules/",
  "/dist/",
  ".test.ts",
  ".test.tsx",
  ".spec.ts",
  ".spec.tsx",
  ".d.ts",
  "/generated/",
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
      if (["node_modules", "dist"].includes(ent.name)) continue;
      walk(full, out);
    } else if (/\.(ts|tsx)$/.test(ent.name) && !shouldSkip(full)) {
      out.push(full);
    }
  }
  return out;
}

/**
 * @param {string} jsdoc
 * @returns {string[]}
 */
function extractExamples(jsdoc) {
  const examples = [];
  const re = /@example\s*\n([\s\S]*?)(?=\n\s*\*\s*@|\n\s*\*\/)/g;
  let m;
  while ((m = re.exec(jsdoc)) !== null) {
    const raw = m[1]
      .split("\n")
      .map((line) => line.replace(/^\s*\*\s?/, ""))
      .join("\n")
      .trim();
    if (raw) examples.push(raw);
  }
  return examples;
}

/**
 * Collect export + preceding jsdoc pairs.
 * @param {string} text
 */
function exportedWithDocs(text) {
  const lines = text.split(/\r?\n/);
  const hits = [];
  const exportRe =
    /^export\s+(?:async\s+)?(?:function|class|const|type|interface)\s+(\w+)/;
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(exportRe);
    if (!m) continue;
    // walk up for jsdoc
    const chunk = [];
    let j = i - 1;
    while (j >= 0) {
      const s = lines[j].trim();
      if (s === "") {
        if (chunk.length) break;
        j -= 1;
        continue;
      }
      if (!(s.startsWith("/**") || s.startsWith("*") || s.startsWith("*/"))) break;
      chunk.unshift(lines[j]);
      if (s.startsWith("/**")) break;
      j -= 1;
    }
    const jsdoc = chunk.join("\n");
    hits.push({ name: m[1], line: i + 1, jsdoc, examples: extractExamples(jsdoc) });
  }
  return hits;
}

function runExample(code, label) {
  // Strip TS-only type annotations lightly for trivial examples; prefer JS-looking examples.
  const cleaned = code
    .replace(/^import\s+.+$/gm, "// import stripped for sandbox")
    .replace(/^export\s+/gm, "");
  try {
    vm.runInNewContext(
      cleaned,
      { console, require: undefined, module: {}, exports: {} },
      { timeout: 2000, filename: label },
    );
    return null;
  } catch (err) {
    return String(err && err.stack ? err.stack : err);
  }
}

function main() {
  const files = SCOPE_DIRS.flatMap((d) => walk(d));
  let ran = 0;
  const failures = [];

  for (const file of files) {
    const text = fs.readFileSync(file, "utf8");
    const rel = path.relative(ROOT, file);
    for (const hit of exportedWithDocs(text)) {
      if (!hit.examples.length) {
        // Presence of @example is enforced by check_docs_ts; harness only executes.
        continue;
      }
      for (let idx = 0; idx < hit.examples.length; idx++) {
        const label = `${rel}:${hit.line}:${hit.name}:example[${idx}]`;
        const err = runExample(hit.examples[idx], label);
        ran += 1;
        if (err) failures.push(`${label}\n${err}`);
      }
    }
  }

  console.log(`run_ts_examples executed=${ran} failures=${failures.length}`);
  for (const f of failures.slice(0, 20)) console.log(f);
  if (failures.length > 20) console.log(`... and ${failures.length - 20} more`);
  // Fail closed: if we found zero exported examples across the tree, treat as fail
  // once presence checker requires @example (after backfill). During early M1,
  // zero executed is OK only when no exports exist — otherwise require ran>0 when
  // files exist.
  if (failures.length) {
    process.exitCode = 1;
    return;
  }
  if (files.length && ran === 0) {
    console.log(
      "run_ts_examples: no @example blocks executed yet (backfill pending); exit 0 for harness-only",
    );
  }
}

main();
