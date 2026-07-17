/**
 * Lightweight IWXXM/XML pretty-printer for the workbench preview pane (F10).
 * No external dependency — inserts newlines/indent between tags only.
 */

/**
 * Pretty-print XML for human preview. Returns the input unchanged when it does
 * not look like markup.
 *
 * @param xml - Raw XML string (may already be compact)
 * @param indent - Spaces per nesting level (default 2)
 * @returns Indented XML
 */
export function prettyPrintXml(xml: string, indent = 2): string {
  const trimmed = xml.trim();
  if (!trimmed.startsWith('<')) {
    return xml;
  }

  const pad = ' '.repeat(Math.max(0, indent));
  // Split between tags while keeping the tags themselves.
  const tokens = trimmed
    .replace(/>\s*</g, '>\n<')
    .split('\n')
    .map((t) => t.trim())
    .filter(Boolean);

  let depth = 0;
  const lines: string[] = [];
  for (const token of tokens) {
    const isClosing = /^<\//.test(token);
    const isSelfClosing = /\/>$/.test(token) || /^<\?/.test(token) || /^<!/.test(token);
    const isOpening = /^<[^/!?][^>]*>$/.test(token) && !isSelfClosing;

    if (isClosing) {
      depth = Math.max(0, depth - 1);
    }
    lines.push(`${pad.repeat(depth)}${token}`);
    if (isOpening) {
      depth += 1;
    }
  }
  return lines.join('\n');
}
