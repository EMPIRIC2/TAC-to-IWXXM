/**
 * Internal planning-vocabulary guard for operator-visible FE strings (EV-048 / #951).
 *
 * [Corpus: tests] TC-EV048-003/005 · [Corpus: product §F7] · D-S057-04-guard-ext=1
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
  { name: 'EV', pattern: /\bEV-\d+\b/g },
  { name: 'S0', pattern: /\bS0\d+\b/g },
  { name: 'TC', pattern: /\bTC-[A-Z0-9-]+\b/g },
  { name: 'E##', pattern: /\bE\d{2}-\d+\b/g },
  // `(?<!\w)#` — `\b#` misses `#702` after spaces/slashes.
  { name: '#NNN', pattern: /(?<!\w)#\d{3,}\b/g },
  // Product feature ids (D-S057-qa003=2 — privacy / OpenAPI operator surfaces).
  { name: 'Fn', pattern: /\bF\d+\b/g },
];

/** Empty unless a proven domain false positive is documented. */
export const INTERNAL_DOC_REF_ALLOWLIST = new Set<string>();

export type InternalDocRefHit = { name: string; token: string };

/**
 * Find planning-vocabulary tokens in a user-visible string.
 *
 * @param text - Operator-visible copy
 * @returns Matching pattern name + token pairs
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
