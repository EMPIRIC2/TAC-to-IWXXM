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
});
