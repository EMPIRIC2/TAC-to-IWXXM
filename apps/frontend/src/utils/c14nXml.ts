/**
 * W3C C14N-oriented XML normalize for Quality metrics (EV-055 / #982).
 *
 * Pipeline (ADR-035 / D-S064-c14n-volatile=1), matching Python
 * `iwxxm_validate.c14n.c14n_xml`:
 * 1. Strip volatile attributes (ADR-032 local-name / UUID-href / codes.wmo.int rules)
 * 2. Strip whitespace-only text nodes
 * 3. Serialize in Canonical XML 1.0 style (sorted attributes)
 *
 * No new npm dependency (`D-S064-c14n-host=1` / Gate A shared helper).
 */

const VOLATILE_ATTRS = new Set([
  'id',
  'gml:id',
  'schemaLocation',
  'translatedBulletinID',
  'translationCentreName',
  'translationCentreDesignator',
  'translationTime',
  'translatedBulletinReceptionTime',
  'translationFailedTAC',
  'permissibleUsage',
  'permissibleUsageReason',
  'permissibleUsageSupplementary',
]);

const UUID_HREF = /^#uuid\.[0-9a-f-]+$/i;
const UUID_VALUE =
  /^uuid\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function localName(name: string): string {
  if (name.includes('}')) {
    return name.slice(name.lastIndexOf('}') + 1);
  }
  if (name.includes(':')) {
    return name.slice(name.lastIndexOf(':') + 1);
  }
  return name;
}

/** @internal Vitest/helper export — Clark / prefixed local-name parity with Python. */
export function localNameForC14n(name: string): string {
  return localName(name);
}

function normText(value: string): string {
  return value.trim().split(/\s+/).join(' ');
}

function isVolatileAttr(name: string, value: string): boolean {
  const local = localName(name);
  if (VOLATILE_ATTRS.has(local)) {
    return true;
  }
  const norm = normText(value);
  if (UUID_VALUE.test(norm)) {
    return true;
  }
  if (
    local === 'href' &&
    (UUID_HREF.test(norm) ||
      norm.startsWith('http://codes.wmo.int/') ||
      norm.startsWith('https://codes.wmo.int/'))
  ) {
    return true;
  }
  return false;
}

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

function stripVolatileAttributes(el: Element): void {
  const toRemove: Attr[] = [];
  for (let i = 0; i < el.attributes.length; i += 1) {
    const attr = el.attributes.item(i);
    if (attr && isVolatileAttr(attr.name, attr.value)) {
      toRemove.push(attr);
    }
  }
  for (const attr of toRemove) {
    el.removeAttributeNode(attr);
  }
  for (const child of Array.from(el.children)) {
    stripVolatileAttributes(child);
  }
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
  attrs.sort((a, b) => (a.name < b.name ? -1 : 1));

  let out = `<${tag}`;
  for (const attr of attrs) {
    out += ` ${attr.name}="${escapeAttr(attr.value)}"`;
  }
  out += '>';

  for (const child of Array.from(el.childNodes)) {
    if (child.nodeType === Node.ELEMENT_NODE) {
      out += serializeElement(child as Element);
    } else if (child.nodeType === Node.TEXT_NODE) {
      // Whitespace-only / null text nodes are removed before serialize.
      out += escapeText(child.textContent as string);
    }
  }
  out += `</${tag}>`;
  return out;
}

/**
 * Return C14N-oriented form of XML text (volatile-stripped + whitespace-stripped).
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
  stripVolatileAttributes(root);
  stripWhitespaceTextNodes(root);
  return serializeElement(root);
}

/**
 * Compare two XML strings under C14N-oriented equality (post–volatile strip).
 *
 * @param left - First XML document
 * @param right - Second XML document
 * @returns True when canonical forms match
 */
export function c14nEqual(left: string, right: string): boolean {
  return c14nXml(left) === c14nXml(right);
}
