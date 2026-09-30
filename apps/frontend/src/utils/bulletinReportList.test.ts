/**
 * Bulletin report list for the live panes.
 */

import { describe, expect, it } from 'vitest';
import { listBulletinReports, replaceBulletinReport } from './bulletinReportList';

const bulletin = [
  'SAUS31 KZNY 121200',
  'METAR KJFK 121251Z 18004KT=',
  'METAR KLAX 121251Z 25008KT=',
].join('\n');

describe('bulletinReportList', () => {
  it('lists TAC reports and skips the heading', () => {
    expect(listBulletinReports('')).toEqual([]);
    expect(listBulletinReports('   ')).toEqual([]);
    expect(listBulletinReports(bulletin)).toEqual([
      { tac: 'METAR KJFK 121251Z 18004KT=', title: 'METAR KJFK 121251Z 18004KT=' },
      { tac: 'METAR KLAX 121251Z 25008KT=', title: 'METAR KLAX 121251Z 25008KT=' },
    ]);
    expect(
      listBulletinReports('KZWY SIGMET 1 VALID 301200/301600 KWBC-\nTEST='),
    ).toEqual([
      {
        tac: 'KZWY SIGMET 1 VALID 301200/301600 KWBC-\nTEST=',
        title: 'KZWY SIGMET 1 VALID',
      },
    ]);
  });

  it('replaces one report and leaves unknown indexes unchanged', () => {
    const next = replaceBulletinReport(bulletin, 1, 'METAR KLAX 121251Z 00000KT=');
    expect(next).toContain('METAR KJFK 121251Z 18004KT=');
    expect(next).toContain('METAR KLAX 121251Z 00000KT=');
    expect(next).not.toContain('25008KT');
    expect(replaceBulletinReport(bulletin, 4, 'METAR XX=')).toBe(bulletin);
  });
});
