/**
 * Path helpers for Quality metrics shareable detail routes (F7.q / EV-056).
 *
 * Uses the History API — the shell does not depend on react-router.
 */

/** List URL for the Quality metrics primary tab. */
export const QUALITY_METRICS_LIST_PATH = '/quality';

/**
 * Build a shareable detail path for a corpus stem.
 *
 * @param stem - Corpus stem id (e.g. `metar-A3-1`)
 * @returns Path `/quality/:stem` with URI encoding
 */
export function qualityMetricsDetailPath(stem: string): string {
  const trimmed = stem.trim();
  if (!trimmed) {
    return QUALITY_METRICS_LIST_PATH;
  }
  return `${QUALITY_METRICS_LIST_PATH}/${encodeURIComponent(trimmed)}`;
}

/**
 * Parse Quality metrics list vs detail from a pathname.
 *
 * @param pathname - `window.location.pathname`
 * @returns `list` or `detail` with decoded stem; `null` when not a quality path
 */
export function parseQualityMetricsPath(
  pathname: string,
): { kind: 'list' } | { kind: 'detail'; stem: string } | null {
  const normalized = pathname.replace(/\/+$/, '') || '/';
  if (normalized === QUALITY_METRICS_LIST_PATH) {
    return { kind: 'list' };
  }
  const prefix = `${QUALITY_METRICS_LIST_PATH}/`;
  if (!normalized.startsWith(prefix)) {
    return null;
  }
  const raw = normalized.slice(prefix.length);
  if (!raw || raw.includes('/')) {
    return null;
  }
  try {
    const stem = decodeURIComponent(raw).trim();
    if (!stem) {
      return { kind: 'list' };
    }
    return { kind: 'detail', stem };
  } catch {
    return null;
  }
}
