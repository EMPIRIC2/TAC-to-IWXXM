/**
 * TC-EV055-003 — FE C14N helper parity with Python iwxxm_validate.c14n.
 */
import { describe, expect, it } from 'vitest';

import { c14nEqual, c14nXml, localNameForC14n } from './c14nXml';

describe('c14nXml (TC-EV055-003)', () => {
  const pretty = `<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2">
  <iwxxm:observation>
    <iwxxm:cloudAmount>FEW</iwxxm:cloudAmount>
  </iwxxm:observation>
</iwxxm:METAR>
`;
  const compact =
    '<?xml version="1.0" encoding="UTF-8"?>' +
    '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2">' +
    '<iwxxm:observation>' +
    '<iwxxm:cloudAmount>FEW</iwxxm:cloudAmount>' +
    '</iwxxm:observation>' +
    '</iwxxm:METAR>';

  const pythonGolden =
    '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"><iwxxm:observation><iwxxm:cloudAmount>FEW</iwxxm:cloudAmount></iwxxm:observation></iwxxm:METAR>';

  it('matches Python C14N golden for pretty/compact peers', () => {
    expect(c14nXml(pretty)).toBe(pythonGolden);
    expect(c14nXml(compact)).toBe(pythonGolden);
    expect(c14nEqual(pretty, compact)).toBe(true);
  });

  it('keeps semantic differences unequal', () => {
    expect(
      c14nEqual('<r xmlns="urn:x"><v>1</v></r>', '<r xmlns="urn:x"><v>2</v></r>'),
    ).toBe(false);
  });

  it('throws on malformed XML', () => {
    expect(() => c14nXml('<not-closed>')).toThrow(/XML parse failed/);
  });

  it('ignores volatile gml:id differences (D-S064-c14n-volatile=1)', () => {
    const a =
      '<r xmlns="urn:x" xmlns:gml="http://www.opengis.net/gml/3.2">' +
      '<n gml:id="uuid.aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"><v>1</v></n></r>';
    const b =
      '<r xmlns="urn:x" xmlns:gml="http://www.opengis.net/gml/3.2">' +
      '<n gml:id="uuid.bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"><v>1</v></n></r>';
    expect(c14nEqual(a, b)).toBe(true);
  });

  it('strips bare UUID attrs and codes.wmo.int / #uuid hrefs', () => {
    const a =
      '<r xmlns:xlink="http://www.w3.org/1999/xlink">' +
      '<n uuidAttr="uuid.aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa" ' +
      'xlink:href="http://codes.wmo.int/common/nil" stable="yes"><v>1</v></n></r>';
    const b =
      '<r xmlns:xlink="http://www.w3.org/1999/xlink">' +
      '<n uuidAttr="uuid.bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb" ' +
      'xlink:href="https://codes.wmo.int/common/nil" stable="yes"><v>1</v></n></r>';
    expect(c14nEqual(a, b)).toBe(true);
    expect(c14nXml(a)).toContain('stable="yes"');

    expect(
      c14nEqual(
        '<r xmlns:xlink="http://www.w3.org/1999/xlink"><n xlink:href="#uuid.aaa"/></r>',
        '<r xmlns:xlink="http://www.w3.org/1999/xlink"><n xlink:href="#uuid.bbb"/></r>',
      ),
    ).toBe(true);
  });

  it('escapes special characters in attributes and text', () => {
    const xml = '<r note="a&amp;b&lt;c&quot;d"><t>x&amp;y&lt;z&gt;w</t></r>';
    const out = c14nXml(xml);
    expect(out).toContain('&amp;');
    expect(out).toContain('&lt;');
  });

  it('escapes control whitespace in attribute and text nodes', () => {
    const parser = new DOMParser();
    const doc = parser.parseFromString('<r note="x">y</r>', 'application/xml');
    const root = doc.documentElement;
    root.setAttribute('note', 'a\tb\nc\rd');
    root.textContent = 'x\ry';
    const serialized = new XMLSerializer().serializeToString(doc);
    const out = c14nXml(serialized);
    expect(out).toContain('&#x9;');
    expect(out).toContain('&#xA;');
    expect(out).toContain('&#xD;');
  });

  it('rejects documents without a root element', () => {
    expect(() => c14nXml('<?xml version="1.0"?>')).toThrow(
      /missing document element|XML parse failed/,
    );
  });

  it('localNameForC14n handles Clark, prefixed, and plain names', () => {
    expect(localNameForC14n('{http://www.opengis.net/gml/3.2}id')).toBe('id');
    expect(localNameForC14n('gml:id')).toBe('id');
    expect(localNameForC14n('id')).toBe('id');
  });
});
