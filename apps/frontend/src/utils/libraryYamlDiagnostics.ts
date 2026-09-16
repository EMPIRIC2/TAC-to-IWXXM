/**
 * Client-side library YAML + regex diagnostics (EVPYL Phase C).
 * Authoritative Fail/Warn still come from POST validate-yaml when signed in.
 */

export type RegexSeverity = 'ok' | 'warn' | 'fail';

export type CaptureSummary = {
  index: number;
  name: string;
};

export type RegexDiagnostic = {
  path: string;
  pattern: string;
  severity: RegexSeverity;
  message: string;
  captures: CaptureSummary[];
  sampleMatched: boolean | null;
};

const NESTED_QUANTIFIER = /[+*][?+]|\{\d+,}\+|\{0,/;
const PATTERN_LINE = /(?:pattern|regex):\s*["']([^"']+)["']/g;

/**
 * True when YAML cannot be treated as a library mapping (locks layout + Activate).
 *
 * @param raw - Editor contents
 */
export function yamlLooksInvalid(raw: string): boolean {
  const trimmed = raw.trim();
  if (!trimmed) {
    return true;
  }
  const quoteCount = (trimmed.match(/"/g) ?? []).length;
  if (quoteCount % 2 === 1) {
    return true;
  }
  if (!/^kind:\s+\S+/m.test(trimmed)) {
    return true;
  }
  if (!/^name:\s+\S+/m.test(trimmed)) {
    return true;
  }
  return false;
}

/**
 * Compile one pattern in the browser and classify ok / warn / fail.
 *
 * @param pattern - Regular expression source
 * @param sample - Optional required sample
 * @param path - Diagnostic path
 */
export function diagnoseJsRegex(
  pattern: string,
  sample?: string,
  path = 'pattern',
): RegexDiagnostic {
  let compiled: RegExp;
  const jsPattern = pattern.replaceAll('(?P<', '(?<');
  try {
    compiled = new RegExp(jsPattern);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Does not compile';
    return {
      path,
      pattern,
      severity: 'fail',
      message: `Does not compile: ${message}`,
      captures: [],
      sampleMatched: null,
    };
  }
  const names = Array.from(jsPattern.matchAll(/\(\?<([A-Za-z_][A-Za-z0-9_]*)>/g)).map(
    (match, index) => ({
      index: index + 1,
      name: match[1] ?? `group${index + 1}`,
    }),
  );
  let sampleMatched: boolean | null = null;
  if (sample !== undefined) {
    sampleMatched = compiled.test(sample);
    compiled.lastIndex = 0;
    if (!sampleMatched) {
      return {
        path,
        pattern,
        severity: 'fail',
        message: 'Required sample has no match',
        captures: names,
        sampleMatched: false,
      };
    }
  }
  const unnamedCaptures = (jsPattern.match(/\((?!\?)/g) ?? []).length > 0;
  if (NESTED_QUANTIFIER.test(pattern) || (unnamedCaptures && names.length === 0)) {
    return {
      path,
      pattern,
      severity: 'warn',
      message: 'Compiles, but may backtrack or leave unnamed groups unused',
      captures: names,
      sampleMatched,
    };
  }
  return {
    path,
    pattern,
    severity: 'ok',
    message: 'Compiles',
    captures: names,
    sampleMatched,
  };
}

/**
 * Collect diagnostics from YAML pattern/regex quoted scalars.
 *
 * @param raw - Library YAML document
 * @param sampleOverride - Optional sample applied to every pattern (drawer)
 */
export function diagnosticsFromYaml(
  raw: string,
  sampleOverride?: string,
): RegexDiagnostic[] {
  if (yamlLooksInvalid(raw)) {
    return [];
  }
  const found: RegexDiagnostic[] = [];
  const matcher = new RegExp(PATTERN_LINE.source, 'g');
  let match = matcher.exec(raw);
  let index = 0;
  while (match !== null) {
    const pattern = match[1] ?? '';
    found.push(diagnoseJsRegex(pattern, sampleOverride, `rules[${index}].pattern`));
    index += 1;
    match = matcher.exec(raw);
  }
  return found;
}

/** First-party assets and activated customs are selectable on Convert. */
export function isLibrarySelectableOnConvert(asset: {
  access: string;
  status?: string | null;
}): boolean {
  if (asset.access === 'first_party') {
    return true;
  }
  return asset.status === 'activated';
}
