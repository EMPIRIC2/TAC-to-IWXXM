import { describe, it, expect } from 'vitest';
import {
  buildWorkSessionPayload,
  extractSessionTitle,
  hasConverterContent,
  resolveManualLineMetaFromResult,
} from './workSessionPayload';

describe('workSessionPayload', () => {
  it('extracts ICAO from METAR for default title', () => {
    expect(extractSessionTitle('METAR KJFK 121251Z 18012KT')).toMatch(/^KJFK · /);
  });

  it('falls back to TAC label when ICAO cannot be parsed', () => {
    expect(extractSessionTitle('free text without icao')).toMatch(/^TAC · /);
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

  it('builds API payload with status override and resolved product', () => {
    const payload = buildWorkSessionPayload(
      {
        manualInput: 'METAR EGLL 121200Z',
        pendingFiles: [{ name: 'a.txt', content: 'METAR' }],
        convertedFiles: [],
        conversionLog: { errors: ['x'], issues: [] },
        conversionParams: { iwxxmVersion: '2025-2', product: 'TAF' },
      },
      { status: 'wip' },
    );
    expect(payload.status).toBe('wip');
    expect(payload.product).toBe('taf');
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

  it('persists manual line metadata in converted_results', () => {
    const payload = buildWorkSessionPayload({
      manualInput: '',
      pendingFiles: [],
      convertedFiles: [
        {
          originalName: 'manual_input_1.txt',
          originalContent: 'METAR ONE',
          convertedContent: '<iwxxm/>',
          manualLineIndex: 1,
          manualLineTotal: 2,
        },
      ],
      conversionLog: null,
      conversionParams: {},
    });
    expect(payload.converted_results?.[0]).toMatchObject({
      manual_line_index: 1,
      manual_line_total: 2,
    });
  });

  it('restores manual line metadata from stored converted_results', () => {
    expect(
      resolveManualLineMetaFromResult(
        'manual_input_1.txt',
        { manual_line_index: 1, manual_line_total: 2 },
        ['manual_input_1.txt', 'manual_input_2.txt'],
      ),
    ).toEqual({ manualLineIndex: 1, manualLineTotal: 2 });
  });

  it('infers manual line metadata from download names when not stored', () => {
    expect(
      resolveManualLineMetaFromResult('manual_input_2.txt', {}, [
        'manual_input_1.txt',
        'manual_input_2.txt',
      ]),
    ).toEqual({ manualLineIndex: 2, manualLineTotal: 2 });
  });
});
