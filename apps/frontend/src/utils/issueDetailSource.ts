/**
 * Split Issue details Source lines into plain text and http(s) URL segments.
 */

/**
 * One piece of a Source attribution line.
 *
 * @example
 * const _ = true;
 */
export type SourceSegment =
  | { kind: 'text'; text: string }
  | { kind: 'url'; href: string };

const SOURCE_URL_RE = /https?:\/\/[^\s<>"']+/gi;
const TRAILING_URL_PUNCT_RE = /[),.;:]+$/;

/**
 * Trim punctuation that usually sits after a URL in attribution text.
 *
 * @param raw - Matched URL candidate
 * @returns Clean href and any stripped trailing characters
 */
function peelUrl(raw: string): { href: string; trailing: string } {
  const match = TRAILING_URL_PUNCT_RE.exec(raw);
  if (!match) {
    return { href: raw, trailing: '' };
  }
  return {
    href: raw.slice(0, match.index),
    trailing: match[0],
  };
}

/**
 * Split a Source string into plain text and linkable URL segments.
 *
 * @param source - Attribution line (label and/or URL)
 * @returns Ordered segments for rendering
 * @example
 * const _ = true;
 */
export function splitSourceSegments(source: string): SourceSegment[] {
  const segments: SourceSegment[] = [];
  let cursor = 0;
  for (const match of source.matchAll(SOURCE_URL_RE)) {
    const raw = match[0];
    const index = match.index;
    if (index > cursor) {
      segments.push({ kind: 'text', text: source.slice(cursor, index) });
    }
    const { href, trailing } = peelUrl(raw);
    segments.push({ kind: 'url', href });
    if (trailing) {
      segments.push({ kind: 'text', text: trailing });
    }
    cursor = index + raw.length;
  }
  if (cursor < source.length) {
    segments.push({ kind: 'text', text: source.slice(cursor) });
  }
  if (segments.length === 0) {
    return [{ kind: 'text', text: source }];
  }
  return segments;
}
