import { c14nXml } from '@/utils/c14nXml';
import { prettyPrintXml } from '@/utils/prettyXml';

/**
 * Prefer C14N form for Quality metrics display/diff, then pretty-print for
 * human-readable line-oriented panes (BUG-2026-08-11). Fall back to raw when
 * XML cannot be parsed.
 *
 * @param xml - Raw XML text
 * @returns Pretty-printed C14N text, or original when empty/invalid
 */
export function qualityMetricsDisplayXml(xml: string): string {
  const trimmed = xml?.trim() ?? '';
  if (!trimmed) {
    return '';
  }
  try {
    return prettyPrintXml(c14nXml(xml));
  } catch {
    return xml;
  }
}
