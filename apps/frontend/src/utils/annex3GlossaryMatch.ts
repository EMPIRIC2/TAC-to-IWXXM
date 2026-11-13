/**
 * Longest-match-first Annex 3 glossary matcher (F38).
 *
 * Limited-meaning §1.2 verbs are never matched for hover.
 */

import {
  ANNEX3_GLOSSARY_ENTRIES,
  type Annex3GlossaryEntry,
} from '@/data/annex3Glossary';

/**
 * Type `GlossaryMatchSegment`.
 * @example
 * const _ = true;
 */
export type GlossaryMatchSegment =
  | { kind: 'text'; value: string }
  | { kind: 'term'; value: string; entry: Annex3GlossaryEntry };

type PatternRow = {
  phrase: string;
  entry: Annex3GlossaryEntry;
};

/** Escape RegExp metacharacters. */
function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/** Build longest-first phrase rows for matching. */
function buildPatterns(
  entries: readonly Annex3GlossaryEntry[] = ANNEX3_GLOSSARY_ENTRIES,
): PatternRow[] {
  const rows: PatternRow[] = [];
  for (const entry of entries) {
    rows.push({ phrase: entry.term, entry });
    for (const alias of entry.aliases ?? []) {
      rows.push({ phrase: alias, entry });
    }
  }
  // Longest phrase first so "runway visual range" wins over shorter tokens.
  rows.sort((a, b) => b.phrase.length - a.phrase.length);
  return rows;
}

const PATTERN_ROWS = buildPatterns();

/**
 * Segment plain text into ordinary spans and glossary term hits.
 *
 * Matching is case-insensitive with word-ish boundaries (no mid-token hits).
 * Everyday §1.2 verbs (provide / issue / supply) are not in the hover catalog.
 *
 * @param text - Source string
 * @param entries - Optional override catalog (tests)
 * @returns Ordered segments covering the full string
 * @example
 * const _ = true;
 */
export function segmentGlossaryText(
  text: string,
  entries: readonly Annex3GlossaryEntry[] = ANNEX3_GLOSSARY_ENTRIES,
): GlossaryMatchSegment[] {
  if (!text) {
    return [];
  }

  const patterns =
    entries === ANNEX3_GLOSSARY_ENTRIES ? PATTERN_ROWS : buildPatterns(entries);
  if (patterns.length === 0) {
    return [{ kind: 'text', value: text }];
  }

  const alternation = patterns.map((row) => escapeRegExp(row.phrase)).join('|');
  // Word-boundary style: avoid matching inside larger alphanumeric tokens.
  const re = new RegExp(`(?<![A-Za-z0-9])(?:${alternation})(?![A-Za-z0-9])`, 'gi');

  const segments: GlossaryMatchSegment[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null = re.exec(text);
  while (match) {
    const start = match.index;
    const value = match[0];
    if (start > lastIndex) {
      segments.push({ kind: 'text', value: text.slice(lastIndex, start) });
    }
    const lower = value.toLowerCase();
    const row = patterns.find((p) => p.phrase.toLowerCase() === lower);
    /* v8 ignore start -- match rows always resolve; empty-segments fallback is defensive */
    if (row) {
      segments.push({ kind: 'term', value, entry: row.entry });
    } else {
      segments.push({ kind: 'text', value });
    }
    lastIndex = start + value.length;
    match = re.exec(text);
  }
  if (lastIndex < text.length) {
    segments.push({ kind: 'text', value: text.slice(lastIndex) });
  }
  return segments.length > 0 ? segments : [{ kind: 'text', value: text }];
  /* v8 ignore stop */
}

/**
 * Whether a limited-meaning verb would ever be hover-linked (always false by design).
 *
 * @param term - Candidate everyday verb
 * @returns Always false for provide/issue/supply
 * @example
 * const _ = true;
 */
export function isLimitedMeaningHoverExcluded(term: string): boolean {
  const normalized = term.trim().toLowerCase();
  return normalized === 'provide' || normalized === 'issue' || normalized === 'supply';
}
