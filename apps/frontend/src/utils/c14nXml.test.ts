/**
 * TC-EV055-003 — FE C14N helper parity with Python iwxxm_validate.c14n.
 */
import { describe, expect, it } from 'vitest';

import { c14nEqual, c14nXml } from './c14nXml';

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
});
