import { describe, it, expect } from 'vitest';
import {
  DEFAULT_OUTPUT_BASENAME,
  sanitizeOutputFilename,
  manualOutputName,
  manualDownloadXmlName,
  outputArchiveName,
  outputFilenameAfterReportLoad,
  stemFromFirstTac,
  formatArchiveTimestamp,
  ACCUMULATE_RESULT_CAP,
  appendConvertedWithinCap,
  nextFirstAccumulatedTac,
  uniquifyZipMemberNames,
  toIwxxmDownloadName,
  toTacSourceName,
  alignConversionZipPairs,
} from './outputFilename';

describe('sanitizeOutputFilename', () => {
  it('falls back to the default for blank or missing input', () => {
    expect(sanitizeOutputFilename('')).toBe(DEFAULT_OUTPUT_BASENAME);
    expect(sanitizeOutputFilename('   ')).toBe(DEFAULT_OUTPUT_BASENAME);
    expect(sanitizeOutputFilename(null)).toBe(DEFAULT_OUTPUT_BASENAME);
    expect(sanitizeOutputFilename(undefined)).toBe(DEFAULT_OUTPUT_BASENAME);
  });

  it('trims surrounding whitespace', () => {
    expect(sanitizeOutputFilename('  report  ')).toBe('report');
  });

  it('strips directory separators and keeps the last segment', () => {
    expect(sanitizeOutputFilename('my/output')).toBe('output');
    expect(sanitizeOutputFilename('a\\b\\c')).toBe('c');
    expect(sanitizeOutputFilename('../../etc/passwd')).toBe('passwd');
    expect(sanitizeOutputFilename('///')).toBe(DEFAULT_OUTPUT_BASENAME);
  });

  it('drops a user-supplied extension', () => {
    expect(sanitizeOutputFilename('weather.xml')).toBe('weather');
    expect(sanitizeOutputFilename('report.txt')).toBe('report');
  });

  it('removes illegal filename characters', () => {
    expect(sanitizeOutputFilename('bad<>:"|?*name')).toBe('badname');
  });

  it('falls back to the default when only illegal characters remain', () => {
    expect(sanitizeOutputFilename('<<>>')).toBe(DEFAULT_OUTPUT_BASENAME);
  });
});

describe('manualOutputName', () => {
  it('uses the base with a .txt extension for single-entry input', () => {
    expect(manualOutputName('report', 0, 1)).toBe('report.txt');
  });

  it('suffixes _N (1-based) for multi-line input', () => {
    expect(manualOutputName('report', 0, 3)).toBe('report_1.txt');
    expect(manualOutputName('report', 1, 3)).toBe('report_2.txt');
    expect(manualOutputName('report', 2, 3)).toBe('report_3.txt');
  });

  it('falls back to the default base when blank', () => {
    expect(manualOutputName('', 0, 1)).toBe('manual_input.txt');
    expect(manualOutputName('', 0, 2)).toBe('manual_input_1.txt');
  });

  it('sanitizes the base before applying a suffix', () => {
    expect(manualOutputName('my/out.xml', 0, 2)).toBe('out_1.txt');
  });
});

describe('toIwxxmDownloadName', () => {
  it('maps TAC input extensions to .xml (success)', () => {
    expect(toIwxxmDownloadName('bulletin_report_1.tac')).toBe('bulletin_report_1.xml');
    expect(toIwxxmDownloadName('first.txt')).toBe('first.xml');
    expect(toIwxxmDownloadName('obs.metar')).toBe('obs.xml');
    expect(toIwxxmDownloadName('Report.TAC')).toBe('Report.xml');
    expect(toIwxxmDownloadName('METARYUD.txt')).toBe('METARYUD.xml');
  });

  it('keeps existing IWXXM extensions and falls back when blank', () => {
    expect(toIwxxmDownloadName('already.xml')).toBe('already.xml');
    expect(toIwxxmDownloadName('pack.iwxxm')).toBe('pack.iwxxm');
    expect(toIwxxmDownloadName('')).toBe('download.xml');
    expect(toIwxxmDownloadName('   ')).toBe('download.xml');
  });

  it('forces .xml for extensionless or unknown extensions (failure modes)', () => {
    expect(toIwxxmDownloadName('noext')).toBe('noext.xml');
    expect(toIwxxmDownloadName('report.foo')).toBe('report.xml');
    expect(toIwxxmDownloadName('path/to/bulletin_report_1.tac')).toBe(
      'bulletin_report_1.xml',
    );
    for (const name of ['a.tac', 'b.txt', 'c.metar', 'd', 'e.foo', '']) {
      expect(toIwxxmDownloadName(name)).not.toMatch(/\.(txt|metar|tac)$/i);
      expect(toIwxxmDownloadName(name)).toMatch(/\.(xml|iwxxm)$/i);
    }
  });
});

describe('toTacSourceName', () => {
  it('keeps TAC-safe extensions (success)', () => {
    expect(toTacSourceName('bulletin_report_1.tac')).toBe('bulletin_report_1.tac');
    expect(toTacSourceName('METARYUD.txt')).toBe('METARYUD.txt');
    expect(toTacSourceName('obs.metar')).toBe('obs.metar');
    expect(toTacSourceName('Report.TAC')).toBe('Report.TAC');
  });

  it('never returns .xml; maps IWXXM / unknown / blank to .txt (failure modes)', () => {
    expect(toTacSourceName('already.xml')).toBe('already.txt');
    expect(toTacSourceName('pack.iwxxm')).toBe('pack.txt');
    expect(toTacSourceName('noext')).toBe('noext.txt');
    expect(toTacSourceName('report.foo')).toBe('report.txt');
    expect(toTacSourceName('')).toBe('download.txt');
    expect(toTacSourceName('   ')).toBe('download.txt');
    expect(toTacSourceName('path/to/input.tac')).toBe('input.tac');
    // Trailing separators: empty pop leaf falls back to the raw path-like name.
    expect(toTacSourceName('folder/')).toBe(`${DEFAULT_OUTPUT_BASENAME}.txt`);
    expect(toIwxxmDownloadName('folder/')).toBe(`${DEFAULT_OUTPUT_BASENAME}.xml`);
    expect(toIwxxmDownloadName('dir/already.xml')).toBe('already.xml');
    expect(toIwxxmDownloadName('dir/obs.tac')).toBe('obs.xml');
    for (const name of ['a.tac', 'b.txt', 'c.xml', 'd', '']) {
      expect(toTacSourceName(name)).toMatch(/\.(txt|metar|tac)$/i);
      expect(toTacSourceName(name)).not.toMatch(/\.xml$/i);
    }
  });
});

describe('alignConversionZipPairs', () => {
  it('pairs IWXXM .xml with TAC .txt/.tac members (success)', () => {
    expect(
      alignConversionZipPairs([
        { xmlName: 'bulletin_report_1.tac', tacName: 'bulletin_report_1.tac' },
        { xmlName: 'METARYUD.txt', tacName: 'METARYUD.txt' },
      ]),
    ).toEqual([
      { xmlName: 'bulletin_report_1.xml', tacName: 'bulletin_report_1.tac' },
      { xmlName: 'METARYUD.xml', tacName: 'METARYUD.txt' },
    ]);
  });

  it('uniquifies collisions while keeping paired stems (failure / collision mode)', () => {
    expect(
      alignConversionZipPairs([
        { xmlName: 'dup.tac', tacName: 'dup.tac' },
        { xmlName: 'dup.tac', tacName: 'dup.tac' },
        { xmlName: 'dup.txt', tacName: 'dup.txt' },
      ]),
    ).toEqual([
      { xmlName: 'dup.xml', tacName: 'dup.tac' },
      { xmlName: 'dup_2.xml', tacName: 'dup_2.tac' },
      { xmlName: 'dup_3.xml', tacName: 'dup_3.txt' },
    ]);
  });

  it('rejects TAC-as-xml and XML-as-tac outcomes', () => {
    const pairs = alignConversionZipPairs([
      { xmlName: '', tacName: '' },
      { xmlName: 'x.xml', tacName: 'x.xml' },
    ]);
    for (const { xmlName, tacName } of pairs) {
      expect(xmlName).toMatch(/\.(xml|iwxxm)$/i);
      expect(xmlName).not.toMatch(/\.(txt|metar|tac)$/i);
      expect(tacName).toMatch(/\.(txt|metar|tac)$/i);
      expect(tacName).not.toMatch(/\.xml$/i);
    }
    expect(pairs[0]).toEqual({ xmlName: 'download.xml', tacName: 'download.txt' });
    expect(pairs[1]).toEqual({ xmlName: 'x.xml', tacName: 'x.txt' });
  });

  it('uses download stem when the XML basename is only an extension', () => {
    expect(alignConversionZipPairs([{ xmlName: '.xml', tacName: 'keep.tac' }])).toEqual(
      [{ xmlName: '.xml', tacName: 'download.tac' }],
    );
  });
});

describe('manualDownloadXmlName', () => {
  it('uses the current field value as .xml (not a convert-time baked name)', () => {
    expect(manualDownloadXmlName('second_name', 0, 1)).toBe('second_name.xml');
    expect(manualDownloadXmlName('first_name', 0, 1)).toBe('first_name.xml');
  });

  it('suffixes _N for multi-line batches', () => {
    expect(manualDownloadXmlName('report', 0, 2)).toBe('report_1.xml');
    expect(manualDownloadXmlName('report', 1, 2)).toBe('report_2.xml');
  });

  it('falls back to manual_input.xml when blank', () => {
    expect(manualDownloadXmlName('', 0, 1)).toBe('manual_input.xml');
  });
});

describe('stemFromFirstTac', () => {
  it('takes the first 8 non-whitespace sanitized chars', () => {
    expect(stemFromFirstTac('METAR KJFK 011200Z')).toBe('METARKJF');
  });

  it('falls back to converted when empty', () => {
    expect(stemFromFirstTac('')).toBe('converted');
    expect(stemFromFirstTac('   ')).toBe('converted');
    expect(stemFromFirstTac('<>:"|?*')).toBe('converted');
  });
});

describe('outputFilenameAfterReportLoad', () => {
  it('fills an empty field from the report and keeps a typed name', () => {
    expect(outputFilenameAfterReportLoad('', false, 'METAR KJFK 011200Z')).toBe(
      'METARKJF',
    );
    expect(outputFilenameAfterReportLoad('myreport', true, 'METAR EGLL 121650Z')).toBe(
      'myreport',
    );
    expect(outputFilenameAfterReportLoad('METARKJF', false, 'TAF YUDO 151800Z')).toBe(
      'TAFYUDO1',
    );
    expect(outputFilenameAfterReportLoad('', false, '   ')).toBe('');
    expect(outputFilenameAfterReportLoad('', false, '')).toBe('');
    expect(outputFilenameAfterReportLoad('', false, '<>')).toBe('');
  });
});

describe('formatArchiveTimestamp', () => {
  it('formats as yyyyMMddHHmmss', () => {
    const d = new Date(2026, 7, 15, 9, 30, 45); // Aug 15 2026 local
    expect(formatArchiveTimestamp(d)).toBe('20260815093045');
  });
});

describe('outputArchiveName', () => {
  it('uses <base>.zip when a custom name is provided', () => {
    expect(outputArchiveName('report')).toBe('report.zip');
    expect(outputArchiveName('  weather.xml ')).toBe('weather.zip');
  });

  it('uses first-TAC stem + yyyyMMddHHmmss when custom name is empty (#903)', () => {
    const now = new Date(2026, 7, 15, 9, 30, 45);
    expect(outputArchiveName('', { firstTac: 'METAR KJFK 011200Z', now })).toBe(
      'METARKJF_20260815093045.zip',
    );
  });

  it('uses the timestamped converted_files fallback when firstTac is empty', () => {
    const now = new Date(1_700_000_000_000);
    expect(outputArchiveName('', { firstTac: '', now })).toBe(
      `converted_files_${now.getTime()}.zip`,
    );
  });

  it('uses the timestamped converted_files fallback when no custom name and no firstTac', () => {
    const now = new Date(1_700_000_000_000);
    expect(outputArchiveName('', { now })).toBe(`converted_files_${now.getTime()}.zip`);
    expect(outputArchiveName('   ', { now })).toBe(
      `converted_files_${now.getTime()}.zip`,
    );
  });

  it('falls back to wall-clock Date when now is omitted', () => {
    expect(outputArchiveName('')).toMatch(/^converted_files_\d+\.zip$/);
  });
});

describe('ACCUMULATE_RESULT_CAP', () => {
  it('is 200 per EV-057 / D-S067-903-cap', () => {
    expect(ACCUMULATE_RESULT_CAP).toBe(200);
  });
});

describe('appendConvertedWithinCap', () => {
  it('places the newest batch first and rejects over-cap batches', () => {
    expect(appendConvertedWithinCap([1], [2], 3)).toEqual({
      files: [2, 1],
      overCap: false,
    });
    expect(appendConvertedWithinCap([1, 2], [3], 2)).toEqual({
      files: [1, 2],
      overCap: true,
    });
  });
});

describe('nextFirstAccumulatedTac', () => {
  it('keeps an existing stem and falls back through original content', () => {
    expect(nextFirstAccumulatedTac('kept', 'new')).toBe('kept');
    expect(nextFirstAccumulatedTac(null, 'first')).toBe('first');
    expect(nextFirstAccumulatedTac(null, null)).toBe(null);
    expect(nextFirstAccumulatedTac(null, undefined)).toBe(null);
  });
});

describe('uniquifyZipMemberNames (TC-EV-beta-002)', () => {
  it('keeps unique names and suffixes collisions', () => {
    expect(
      uniquifyZipMemberNames([
        'test.xml',
        'test.xml',
        'test.xml',
        'other.xml',
        'test.xml',
      ]),
    ).toEqual(['test.xml', 'test_2.xml', 'test_3.xml', 'other.xml', 'test_4.xml']);
  });

  it('handles names without an extension', () => {
    expect(uniquifyZipMemberNames(['a', 'a'])).toEqual(['a', 'a_2']);
  });

  it('avoids colliding with an already-present _N suffix', () => {
    expect(uniquifyZipMemberNames(['foo.xml', 'foo_2.xml', 'foo.xml'])).toEqual([
      'foo.xml',
      'foo_2.xml',
      'foo_3.xml',
    ]);
  });

  it('defaults blank names to download.xml and uniquifies them', () => {
    expect(uniquifyZipMemberNames(['', '  ', 'download.xml'])).toEqual([
      'download.xml',
      'download_2.xml',
      'download_3.xml',
    ]);
  });

  it('handles unicode and long basenames without collision (TC-EV-verify-003)', () => {
    const long = `${'a'.repeat(180)}.xml`;
    expect(uniquifyZipMemberNames(['café.xml', 'café.xml', long, long])).toEqual([
      'café.xml',
      'café_2.xml',
      long,
      long.replace(/\.xml$/, '_2.xml'),
    ]);
  });
});
