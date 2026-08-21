import { describe, it, expect } from 'vitest';
import {
  DEFAULT_OUTPUT_BASENAME,
  sanitizeOutputFilename,
  manualOutputName,
  manualDownloadXmlName,
  outputArchiveName,
  stemFromFirstTac,
  formatArchiveTimestamp,
  ACCUMULATE_RESULT_CAP,
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

  it('uses the timestamped converted_files fallback when no custom name and no firstTac', () => {
    const now = new Date(1_700_000_000_000);
    expect(outputArchiveName('', { now })).toBe(`converted_files_${now.getTime()}.zip`);
    expect(outputArchiveName('   ', { now })).toBe(
      `converted_files_${now.getTime()}.zip`,
    );
  });
});

describe('ACCUMULATE_RESULT_CAP', () => {
  it('is 200 per EV-057 / D-S067-903-cap', () => {
    expect(ACCUMULATE_RESULT_CAP).toBe(200);
  });
});
