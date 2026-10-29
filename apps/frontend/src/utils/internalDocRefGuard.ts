/**
 * Internal planning-vocabulary guard for operator-visible FE strings (EV-048 / #951).
 *
 * [Corpus: tests] TC-EV048-003/005 · [Corpus: product §F7] · D-S057-04-guard-ext=1
 * Extended: UJ journey ids, Fn+theme crumbs, vague filler (UX-2026-10-29-scrub-vague-jargon).
 */

/** Locked patterns (D-S057-guard-s0=1, D-S057-04-guard-ext=1). */
export const INTERNAL_DOC_REF_PATTERNS: ReadonlyArray<{
  name: string;
  pattern: RegExp;
}> = [
  { name: 'Corpus', pattern: /\[Corpus:/g },
  { name: 'docs/sessions', pattern: /docs\/sessions\//g },
  { name: 'docs/feature-list', pattern: /docs\/feature-list/g },
  { name: 'ADR', pattern: /\bADR-\d+\b/g },
  { name: 'EV', pattern: /\bEV-\d+\b/gi },
  // Compact evolve cycle tags (e.g. catalog tag `ev030`) — no hyphen.
  { name: 'evTag', pattern: /\bev\d+\b/gi },
  { name: 'S0', pattern: /\bS0\d+\b/g },
  { name: 'TC', pattern: /\bTC-[A-Z0-9-]+\b/gi },
  { name: 'E##', pattern: /\bE\d{2}-\d+\b/g },
  // `(?<!\w)#` — `\b#` misses `#702` after spaces/slashes.
  { name: '#NNN', pattern: /(?<!\w)#\d{3,}\b/g },
  // Journey ids (operator surfaces — not docs/tests).
  { name: 'UJ', pattern: /\bUJ-\d+\b/gi },
  // Scrub compound feature+theme crumbs before bare Fn (e.g. `F26 theme V1`).
  {
    name: 'FnTheme',
    pattern: /\(?\bF\d+\s+theme\s+[A-Za-z]{0,2}\d+\)?/gi,
  },
  // Product feature ids (D-S057-qa003=2 — privacy / OpenAPI operator surfaces).
  { name: 'Fn', pattern: /\bF\d+\b/g },
  // Leftover research theme crumbs after Fn removal (`theme V1` / `theme SX1`).
  { name: 'theme', pattern: /\btheme\s+[A-Za-z]{0,2}\d+\b/gi },
];

/**
 * Vague filler that must not appear as operator chrome (not grammatical articles).
 */
export const OPERATOR_VAGUE_FILLER_PATTERNS: ReadonlyArray<{
  name: string;
  pattern: RegExp;
}> = [{ name: 'stuff', pattern: /\bstuff\b/gi }];

/** Empty unless a proven domain false positive is documented. */
export const INTERNAL_DOC_REF_ALLOWLIST = new Set<string>();

/**
 * Type `InternalDocRefHit`.
 * @example
 * const _ = true;
 */
export type InternalDocRefHit = { name: string; token: string };

/**
 * Find planning-vocabulary tokens in a user-visible string.
 *
 * @param text - Operator-visible copy
 * @returns Matching pattern name + token pairs
 * @example
 * const _ = true;
 */
export function findInternalDocRefs(text: string): InternalDocRefHit[] {
  const hits: InternalDocRefHit[] = [];
  for (const { name, pattern } of INTERNAL_DOC_REF_PATTERNS) {
    pattern.lastIndex = 0;
    let match: RegExpExecArray | null;
    while ((match = pattern.exec(text)) !== null) {
      const token = match[0];
      if (INTERNAL_DOC_REF_ALLOWLIST.has(token)) {
        continue;
      }
      hits.push({ name, token });
    }
  }
  return hits;
}

/**
 * Find vague filler tokens in operator-visible copy.
 *
 * @param text - Operator-visible copy
 * @returns Matching pattern name + token pairs
 */
export function findVagueFiller(text: string): InternalDocRefHit[] {
  const hits: InternalDocRefHit[] = [];
  for (const { name, pattern } of OPERATOR_VAGUE_FILLER_PATTERNS) {
    pattern.lastIndex = 0;
    let match: RegExpExecArray | null;
    while ((match = pattern.exec(text)) !== null) {
      hits.push({ name, token: match[0] });
    }
  }
  return hits;
}

/**
 * Remove planning-vocabulary tokens and vague filler from operator-visible copy.
 *
 * Does not strip grammatical articles (`a` / `an` / `the`).
 *
 * @param text - Raw message, tag list, or attribution
 * @returns Scrubbed text (original when scrubbing would empty the string)
 * @example
 * const _ = true;
 */
export function scrubInternalDocRefs(text: string): string {
  let cleaned = text ?? '';
  for (const { pattern } of INTERNAL_DOC_REF_PATTERNS) {
    pattern.lastIndex = 0;
    cleaned = cleaned.replace(pattern, '');
  }
  for (const { pattern } of OPERATOR_VAGUE_FILLER_PATTERNS) {
    pattern.lastIndex = 0;
    cleaned = cleaned.replace(pattern, '');
  }
  cleaned = cleaned.replace(/\(\s*\)/g, '');
  // Collapse leftover " - / " or " / " separators after token removal.
  cleaned = cleaned.replace(/\s+\/\s+/g, ' ');
  cleaned = cleaned.replace(/\s{2,}/g, ' ');
  cleaned = cleaned.replace(/^\s*[-–—;/]+\s*/g, '');
  let previous = '';
  while (previous !== cleaned) {
    previous = cleaned;
    cleaned = cleaned.replace(/\s*[-–—;/]+\s*$/g, '').trim();
  }
  return cleaned || text;
}

/**
 * True when a catalog tag is planning shorthand (evolve / feature / theme crumbs).
 *
 * Matches ``ev030``, ``f26``, ``v1``, ``t1``, ``sx1``, ``r8``, ``c1`` — not domain
 * words like ``volcano`` or ``sigmet``.
 *
 * @param tag - One catalog tag
 * @returns Whether the tag must stay off operator surfaces
 * @example
 * const _ = true;
 */
export function isPlanningEvolveTag(tag: string): boolean {
  const trimmed = tag.trim();
  // Compact evolve ids, feature ids, and 1–2 letter research theme codes.
  return /^(?:ev\d+|[a-z]{1,2}\d+)$/i.test(trimmed);
}
