/**
 * Write an Istanbul coverage report for the Playwright sources.
 *
 * Loads `apps/e2e/*.ts` under V8 coverage with `@playwright/test` stubbed, then
 * writes `apps/e2e/coverage/coverage-final.json`. The directory is gitignored.
 * Run this in the bugs CI job before `pytest tests/bugs`.
 *
 * Acceptance command:
 *
 *     node scripts/ci/collect_e2e_coverage.mjs
 *
 * [Corpus: tests]
 */
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const e2eDir = path.join(root, 'apps/e2e');
const reportDir = path.join(e2eDir, 'coverage');
const v8Dir = path.join(reportDir, 'tmp-v8');
const reportPath = path.join(reportDir, 'coverage-final.json');

function lineStarts(source) {
  const starts = [0];
  for (let index = 0; index < source.length; index += 1) {
    if (source[index] === '\n') {
      starts.push(index + 1);
    }
  }
  return starts;
}

function lineForOffset(starts, offset) {
  let low = 0;
  let high = starts.length - 1;
  while (low < high) {
    const mid = Math.ceil((low + high) / 2);
    if (starts[mid] <= offset) {
      low = mid;
    } else {
      high = mid - 1;
    }
  }
  return low;
}

function coveredLineSet(source, functions) {
  const starts = lineStarts(source);
  const hits = new Map();
  const ranges = [];
  for (const fn of functions ?? []) {
    for (const range of fn.ranges ?? []) {
      ranges.push(range);
    }
  }
  // Outer script ranges cover the whole file. Inner ranges (including count 0
  // for functions that were defined but not called) must override them.
  ranges.sort(
    (left, right) =>
      right.endOffset - right.startOffset - (left.endOffset - left.startOffset),
  );
  for (const range of ranges) {
    const first = lineForOffset(starts, range.startOffset);
    const last = lineForOffset(
      starts,
      Math.max(range.startOffset, range.endOffset - 1),
    );
    for (let line = first; line <= last; line += 1) {
      hits.set(line, range.count ?? 0);
    }
  }
  return { starts, hits };
}

function istanbulForFile(filePath, functions) {
  const source = fs.readFileSync(filePath, 'utf8');
  const lines = source.split('\n');
  const { starts, hits } = coveredLineSet(source, functions);
  const statementMap = {};
  const statements = {};
  let statementId = 0;
  for (let index = 0; index < lines.length; index += 1) {
    const text = lines[index].trim();
    if (
      !text ||
      text.startsWith('//') ||
      text.startsWith('*') ||
      text.startsWith('/*')
    ) {
      continue;
    }
    const startColumn = lines[index].length - lines[index].trimStart().length;
    statementMap[String(statementId)] = {
      start: { line: index + 1, column: startColumn },
      end: { line: index + 1, column: lines[index].length },
    };
    statements[String(statementId)] = hits.get(index) ?? 0;
    statementId += 1;
  }
  void starts;
  return {
    path: filePath,
    statementMap,
    s: statements,
    branchMap: {},
    b: {},
    fnMap: {},
    f: {},
  };
}

function readV8Scripts() {
  const byUrl = new Map();
  if (!fs.existsSync(v8Dir)) {
    return byUrl;
  }
  for (const name of fs.readdirSync(v8Dir)) {
    if (!name.endsWith('.json')) {
      continue;
    }
    const payload = JSON.parse(fs.readFileSync(path.join(v8Dir, name), 'utf8'));
    for (const script of payload.result ?? []) {
      if (typeof script.url === 'string' && script.url.startsWith('file:')) {
        byUrl.set(script.url, script.functions ?? []);
      }
    }
  }
  return byUrl;
}

function writeReport() {
  const coverage = {};
  const scripts = readV8Scripts();
  let measured = 0;
  for (const name of fs.readdirSync(e2eDir)) {
    if (!name.endsWith('.ts')) {
      continue;
    }
    const filePath = path.join(e2eDir, name);
    const fileUrl = new URL(`file://${filePath}`).href;
    const functions = scripts.get(fileUrl);
    if (!functions) {
      continue;
    }
    coverage[filePath] = istanbulForFile(filePath, functions);
    measured += 1;
  }
  if (measured === 0) {
    console.error('V8 coverage did not include any apps/e2e TypeScript sources');
    process.exit(1);
  }
  fs.mkdirSync(reportDir, { recursive: true });
  fs.writeFileSync(reportPath, `${JSON.stringify(coverage)}\n`);
  console.log(`wrote ${path.relative(root, reportPath)} (${measured} files)`);
}

function collect() {
  fs.rmSync(v8Dir, { recursive: true, force: true });
  fs.mkdirSync(v8Dir, { recursive: true });
  const major = Number(process.versions.node.split('.')[0]);
  const args = [];
  if (major < 23) {
    args.push('--experimental-strip-types');
  }
  args.push(
    '--import',
    path.join(root, 'scripts/ci/e2e_playwright_hook.mjs'),
    path.join(root, 'scripts/ci/load_e2e_sources.mjs'),
  );
  const child = spawn(process.execPath, args, {
    cwd: root,
    env: { ...process.env, NODE_V8_COVERAGE: v8Dir },
    stdio: 'inherit',
  });
  child.on('exit', (code) => {
    if (code !== 0) {
      process.exit(code ?? 1);
    }
    writeReport();
  });
}

collect();
