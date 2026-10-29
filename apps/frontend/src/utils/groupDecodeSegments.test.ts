/**
 * UX-2026-10-29-live-decode-phrases — FE phrase grouping for Live decode.
 */

import { describe, expect, it } from 'vitest';
import { groupDecodeSegments, type DecodeSegmentLike } from './groupDecodeSegments';

function seg(
  start: number,
  end: number,
  code: string,
  explanation: string,
): DecodeSegmentLike {
  return { start, end, code, explanation };
}

describe('groupDecodeSegments', () => {
  it('leaves unmatched tokens as one row each', () => {
    const input = [
      seg(0, 5, 'METAR', 'Report type'),
      seg(6, 10, 'KJFK', 'ICAO station'),
    ];
    expect(groupDecodeSegments(input)).toEqual(input);
  });

  it('groups TC + cyclone name into one phrase', () => {
    const phrases = groupDecodeSegments([
      seg(78, 80, 'TC', 'Tropical cyclone'),
      seg(81, 86, 'IN-FA', 'Tropical cyclone (IN-FA)'),
      seg(87, 90, 'OBS', 'Observed'),
    ]);
    expect(phrases[0]).toMatchObject({
      start: 78,
      end: 86,
      code: 'TC IN-FA',
      explanation: 'Tropical cyclone IN-FA',
    });
    expect(phrases[1]?.code).toBe('OBS');
  });

  it('groups OBS AT time lat lon into one natural-language phrase', () => {
    const phrases = groupDecodeSegments([
      seg(87, 90, 'OBS', 'Observed'),
      seg(91, 93, 'AT', 'At (observation / forecast time)'),
      seg(94, 99, '1800Z', 'Time 18:00 UTC'),
      seg(100, 105, 'N1540', "Latitude 15°40' N"),
      seg(106, 112, 'E15620', "Longitude 156°20' E"),
      seg(113, 115, 'CB', 'Cumulonimbus'),
    ]);
    expect(phrases[0]).toMatchObject({
      start: 87,
      end: 112,
      code: 'OBS AT 1800Z N1540 E15620',
      explanation: "Observed at 18:00 UTC near 15°40'N 156°20'E",
    });
    expect(phrases).toHaveLength(2);
  });

  it('groups FCST AT time lat lon similarly', () => {
    const phrases = groupDecodeSegments([
      seg(0, 4, 'FCST', 'Forecast'),
      seg(5, 7, 'AT', 'At (observation / forecast time)'),
      seg(8, 13, '0000Z', 'Time 00:00 UTC'),
      seg(14, 19, 'N1630', "Latitude 16°30' N"),
      seg(20, 26, 'E15540', "Longitude 155°40' E"),
    ]);
    expect(phrases).toEqual([
      {
        start: 0,
        end: 26,
        code: 'FCST AT 0000Z N1630 E15540',
        explanation: "Forecast at 00:00 UTC near 16°30'N 155°40'E",
      },
    ]);
  });

  it('groups CB TOP FLnnn into one phrase', () => {
    const phrases = groupDecodeSegments([
      seg(113, 115, 'CB', 'Cumulonimbus'),
      seg(116, 119, 'TOP', 'Top'),
      seg(120, 125, 'FL510', 'Flight level 510'),
    ]);
    expect(phrases).toEqual([
      {
        start: 113,
        end: 125,
        code: 'CB TOP FL510',
        explanation: 'Cumulonimbus top at flight level 510',
      },
    ]);
  });

  it('groups FIR name + FIR marker', () => {
    const phrases = groupDecodeSegments([
      seg(66, 73, 'FUKUOKA', 'FIR name (FUKUOKA)'),
      seg(74, 77, 'FIR', 'Flight information region'),
      seg(78, 80, 'TC', 'Tropical cyclone'),
    ]);
    expect(phrases[0]).toMatchObject({
      start: 66,
      end: 77,
      code: 'FUKUOKA FIR',
      explanation: 'FUKUOKA flight information region',
    });
    expect(phrases).toHaveLength(2);
  });

  it('groups MOV + direction + speed', () => {
    const phrases = groupDecodeSegments([
      seg(172, 175, 'MOV', 'Moving'),
      seg(176, 177, 'W', 'Movement direction (West)'),
      seg(178, 182, '15KT', 'Speed 15 kt'),
    ]);
    expect(phrases).toEqual([
      {
        start: 172,
        end: 182,
        code: 'MOV W 15KT',
        explanation: 'Moving west at 15 kt',
      },
    ]);
  });

  it('passes through OBS when time token is missing', () => {
    const input = [seg(0, 3, 'OBS', 'Observed'), seg(4, 6, 'CB', 'Cumulonimbus')];
    expect(groupDecodeSegments(input)).toEqual(input);
  });

  it('groups OBS + time without AT or coordinates', () => {
    expect(
      groupDecodeSegments([
        seg(0, 3, 'OBS', 'Observed'),
        seg(4, 9, '1800Z', 'Time 18:00 UTC'),
      ]),
    ).toEqual([
      {
        start: 0,
        end: 9,
        code: 'OBS 1800Z',
        explanation: 'Observed at 18:00 UTC',
      },
    ]);
  });

  it('groups OBS + time + lat only (no lon)', () => {
    expect(
      groupDecodeSegments([
        seg(0, 3, 'OBS', 'Observed'),
        seg(4, 9, '1800Z', 'Time 18:00 UTC'),
        seg(10, 15, 'N1540', "Latitude 15°40' N"),
      ]),
    ).toEqual([
      {
        start: 0,
        end: 15,
        code: 'OBS 1800Z N1540',
        explanation: "Observed at 18:00 UTC near 15°40'N",
      },
    ]);
  });

  it('does not group incomplete CB TOP without flight level', () => {
    const input = [
      seg(0, 2, 'CB', 'Cumulonimbus'),
      seg(3, 6, 'TOP', 'Top'),
      seg(7, 9, 'NC', 'No change'),
    ];
    expect(groupDecodeSegments(input)).toEqual(input);
  });

  it('does not group CB when the next token is not Top', () => {
    const input = [
      seg(0, 2, 'CB', 'Cumulonimbus'),
      seg(3, 5, 'NC', 'No change'),
      seg(6, 11, 'FL510', 'Flight level 510'),
    ];
    expect(groupDecodeSegments(input)).toEqual(input);
  });

  it('does not group CB TOP when trailing segments are missing', () => {
    expect(
      groupDecodeSegments([seg(0, 2, 'CB', 'Cumulonimbus'), seg(3, 6, 'TOP', 'Top')]),
    ).toEqual([seg(0, 2, 'CB', 'Cumulonimbus'), seg(3, 6, 'TOP', 'Top')]);
  });

  it('does not group Moving without a valid direction or speed', () => {
    expect(
      groupDecodeSegments([
        seg(0, 3, 'MOV', 'Moving'),
        seg(4, 5, 'X', 'Unknown token'),
        seg(6, 10, '15KT', 'Speed 15 kt'),
      ]),
    ).toEqual([
      seg(0, 3, 'MOV', 'Moving'),
      seg(4, 5, 'X', 'Unknown token'),
      seg(6, 10, '15KT', 'Speed 15 kt'),
    ]);
    expect(
      groupDecodeSegments([
        seg(0, 3, 'MOV', 'Moving'),
        seg(4, 5, 'W', 'Movement direction (West)'),
        seg(6, 8, 'NC', 'No change'),
      ]),
    ).toEqual([
      seg(0, 3, 'MOV', 'Moving'),
      seg(4, 5, 'W', 'Movement direction (West)'),
      seg(6, 8, 'NC', 'No change'),
    ]);
  });

  it('skips sparse undefined holes without throwing', () => {
    const sparse: DecodeSegmentLike[] = [];
    sparse.length = 1;
    expect(groupDecodeSegments(sparse)).toEqual([]);
  });

  it('does not group TC without a named cyclone follow-on', () => {
    const input = [seg(0, 2, 'TC', 'Tropical cyclone'), seg(3, 6, 'OBS', 'Observed')];
    expect(groupDecodeSegments(input)).toEqual(input);
  });

  it('reduces the SIGMET sample run to fewer phrase rows', () => {
    const input = [
      seg(66, 73, 'FUKUOKA', 'FIR name (FUKUOKA)'),
      seg(74, 77, 'FIR', 'Flight information region'),
      seg(78, 80, 'TC', 'Tropical cyclone'),
      seg(81, 86, 'IN-FA', 'Tropical cyclone (IN-FA)'),
      seg(87, 90, 'OBS', 'Observed'),
      seg(91, 93, 'AT', 'At (observation / forecast time)'),
      seg(94, 99, '1800Z', 'Time 18:00 UTC'),
      seg(100, 105, 'N1540', "Latitude 15°40' N"),
      seg(106, 112, 'E15620', "Longitude 156°20' E"),
      seg(113, 115, 'CB', 'Cumulonimbus'),
      seg(116, 119, 'TOP', 'Top'),
      seg(120, 125, 'FL510', 'Flight level 510'),
      seg(126, 128, 'NC', 'No change'),
      seg(129, 133, 'FCST', 'Forecast'),
      seg(134, 136, 'AT', 'At (observation / forecast time)'),
      seg(137, 142, '0000Z', 'Time 00:00 UTC'),
      seg(143, 148, 'N1630', "Latitude 16°30' N"),
      seg(149, 155, 'E15540', "Longitude 155°40' E"),
      seg(156, 158, 'CB', 'Cumulonimbus'),
      seg(159, 162, 'TOP', 'Top'),
      seg(163, 168, 'FL500', 'Flight level 500'),
      seg(172, 175, 'MOV', 'Moving'),
      seg(176, 177, 'W', 'Movement direction (West)'),
      seg(178, 182, '15KT', 'Speed 15 kt'),
    ];
    const phrases = groupDecodeSegments(input);
    expect(phrases.length).toBeLessThan(input.length);
    expect(phrases.map((p) => p.code)).toEqual([
      'FUKUOKA FIR',
      'TC IN-FA',
      'OBS AT 1800Z N1540 E15620',
      'CB TOP FL510',
      'NC',
      'FCST AT 0000Z N1630 E15540',
      'CB TOP FL500',
      'MOV W 15KT',
    ]);
  });
});
