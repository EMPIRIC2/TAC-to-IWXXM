import { c14nXml } from '@/utils/c14nXml';

/**
 * Prefer C14N form for Quality metrics display/diff; fall back to raw when XML
 * cannot be parsed.
 *
 * @param xml - Raw XML text
 * @returns C14N text or original when empty/invalid
 */
export function qualityMetricsDisplayXml(xml: string): string {
  const trimmed = xml?.trim() ?? '';
  if (!trimmed) {
    return '';
  }
  try {
    return c14nXml(xml);
  } catch {
    return xml;
  }
}
