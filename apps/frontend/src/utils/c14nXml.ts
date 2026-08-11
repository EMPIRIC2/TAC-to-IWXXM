/**
 * W3C C14N-oriented XML normalize for Quality metrics (EV-055 / #982).
 *
 * Strips whitespace-only text nodes, then serializes in Canonical XML 1.0 style
 * (sorted attributes, stable namespace decls) to peer with Python
 * `iwxxm_validate.c14n.c14n_xml` (lxml `method='c14n'` after the same strip).
 *
 * No new npm dependency (`D-S064-c14n-host=1` / Gate A shared helper).
 */

function isWhitespaceOnly(text: string): boolean {
  return text.trim().length === 0;
}

function escapeAttr(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/"/g, '&quot;')
    .replace(/\t/g, '&#x9;')
    .replace(/\n/g, '&#xA;')
    .replace(/\r/g, '&#xD;');
}

function escapeText(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\r/g, '&#xD;');
}

function stripWhitespaceTextNodes(node: Node): void {
  const children = Array.from(node.childNodes);
  for (const child of children) {
    if (child.nodeType === Node.TEXT_NODE) {
      const text = child.textContent ?? '';
      if (isWhitespaceOnly(text)) {
        node.removeChild(child);
      }
    } else if (child.nodeType === Node.ELEMENT_NODE) {
      stripWhitespaceTextNodes(child);
    }
  }
}

function serializeElement(el: Element): string {
  const tag = el.tagName;
  const attrs: Array<{ name: string; value: string }> = [];
  for (let i = 0; i < el.attributes.length; i += 1) {
    const attr = el.attributes.item(i);
    if (!attr) continue;
    attrs.push({ name: attr.name, value: attr.value });
  }
  // C14N: lexicographic attribute order (xmlns* sorted with other attrs by name)
  attrs.sort((a, b) => (a.name < b.name ? -1 : a.name > b.name ? 1 : 0));

  let out = `<${tag}`;
  for (const attr of attrs) {
    out += ` ${attr.name}="${escapeAttr(attr.value)}"`;
  }
  out += '>';

  for (const child of Array.from(el.childNodes)) {
    if (child.nodeType === Node.ELEMENT_NODE) {
      out += serializeElement(child as Element);
    } else if (child.nodeType === Node.TEXT_NODE) {
      out += escapeText(child.textContent ?? '');
    }
  }
  out += `</${tag}>`;
  return out;
}

/**
 * Return C14N-oriented form of XML text (whitespace-stripped Canonical XML 1.0 style).
 *
 * @param xmlContent - Well-formed XML document text
 * @returns Canonical serialization
 * @throws Error when XML cannot be parsed
 */
export function c14nXml(xmlContent: string): string {
  const parser = new DOMParser();
  const doc = parser.parseFromString(xmlContent, 'application/xml');
  const parseError = doc.querySelector('parsererror');
  if (parseError) {
    throw new Error(
      `XML parse failed for C14N: ${parseError.textContent ?? 'unknown'}`,
    );
  }
  const root = doc.documentElement;
  if (!root) {
    throw new Error('XML parse failed for C14N: missing document element');
  }
  stripWhitespaceTextNodes(root);
  return serializeElement(root);
}

/**
 * Compare two XML strings under C14N-oriented equality.
 *
 * @param left - First XML document
 * @param right - Second XML document
 * @returns True when canonical forms match
 */
export function c14nEqual(left: string, right: string): boolean {
  return c14nXml(left) === c14nXml(right);
}
