/**
 * Work-session convert versions.
 */

import { describe, expect, it } from 'vitest';
import {
  appendOutputVersion,
  readOutputVersions,
  type OutputVersion,
} from './outputVersions';

const version = (xml: string, tac = 'METAR TTPP'): OutputVersion => ({
  at: 1,
  tac,
  xml,
  conversionProfile: 'conversion · ICAO_2025',
  decodingProfile: 'decoding · ICAO_2025',
});

describe('outputVersions', () => {
  it('reads only complete version rows', () => {
    expect(readOutputVersions(undefined)).toEqual([]);
    expect(readOutputVersions({ output_versions: 'nope' })).toEqual([]);
    expect(
      readOutputVersions({
        output_versions: [
          null,
          { tac: 'METAR' },
          {
            tac: 'METAR',
            xml: '<a/>',
            at: 5,
            conversionProfile: 'c',
            decodingProfile: 'd',
          },
          { tac: 'SPECI', xml: '<b/>' },
        ],
      }),
    ).toEqual([
      {
        at: 5,
        tac: 'METAR',
        xml: '<a/>',
        conversionProfile: 'c',
        decodingProfile: 'd',
      },
      {
        at: 0,
        tac: 'SPECI',
        xml: '<b/>',
        conversionProfile: '',
        decodingProfile: '',
      },
    ]);
  });

  it('skips a repeat of the latest XML and caps the list', () => {
    expect(appendOutputVersion([], version('<a/>'))).toHaveLength(1);
    const first = version('<a/>');
    expect(appendOutputVersion([first], version('<a/>'))).toEqual([first]);
    expect(appendOutputVersion([first], version('<a/>', 'SPECI'))).toHaveLength(2);
    const many = Array.from({ length: 20 }, (_, index) => version(`<v${index}/>`));
    const next = appendOutputVersion(many, version('<new/>'));
    expect(next).toHaveLength(20);
    expect(next[0]?.xml).toBe('<v1/>');
    expect(next[19]?.xml).toBe('<new/>');
  });
});
