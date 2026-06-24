import { describe, it, expect } from 'vitest';
import {
  buildWorkSessionPayload,
  extractSessionTitle,
  hasConverterContent,
} from './workSessionPayload';

describe('workSessionPayload', () => {
  it('extracts ICAO from METAR for default title', () => {
    expect(extractSessionTitle('METAR KJFK 121251Z 18012KT')).toMatch(/^KJFK · /);
  });

  it('falls back to METAR label when ICAO cannot be parsed', () => {
    expect(extractSessionTitle('free text without icao')).toMatch(/^METAR · /);
  });

  it('detects converter content', () => {
    expect(
      hasConverterContent({
        manualInput: '',
        pendingFiles: [],
        convertedFiles: [],
        conversionLog: null,
        conversionParams: {},
      }),
    ).toBe(false);
    expect(
      hasConverterContent({
        manualInput: 'METAR KJFK',
        pendingFiles: [],
        convertedFiles: [],
        conversionLog: null,
        conversionParams: {},
      }),
    ).toBe(true);
  });

  it('builds API payload with status override', () => {
    const payload = buildWorkSessionPayload(
      {
        manualInput: 'METAR EGLL 121200Z',
        pendingFiles: [{ name: 'a.txt', content: 'METAR' }],
        convertedFiles: [],
        conversionLog: { errors: ['x'], issues: [] },
        conversionParams: { iwxxmVersion: '2025-2' },
      },
      { status: 'wip' },
    );
    expect(payload.status).toBe('wip');
    expect(payload.errors).toEqual(['x']);
    expect(payload.pending_files).toHaveLength(1);
  });

  it('includes kv upload key when provided', () => {
    const payload = buildWorkSessionPayload(
      {
        manualInput: 'METAR',
        pendingFiles: [],
        convertedFiles: [],
        conversionLog: null,
        conversionParams: {},
      },
      { kvUploadKey: 'kv-123' },
    );
    expect(payload.kv_upload_key).toBe('kv-123');
  });

  it('detects converter content from pending files and converted results', () => {
    expect(
      hasConverterContent({
        manualInput: '',
        pendingFiles: [{ name: 'a.txt', content: 'METAR' }],
        convertedFiles: [],
        conversionLog: null,
        conversionParams: {},
      }),
    ).toBe(true);
    expect(
      hasConverterContent({
        manualInput: '',
        pendingFiles: [],
        convertedFiles: [
          {
            originalName: 'a.xml',
            originalContent: 'METAR',
            convertedContent: '<iwxxm/>',
          },
        ],
        conversionLog: null,
        conversionParams: {},
      }),
    ).toBe(true);
  });
});
