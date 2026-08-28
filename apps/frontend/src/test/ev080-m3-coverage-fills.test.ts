/**
 * EV-080 M3 — remaining branch/statement fills for utilities and file-input helpers.
 */
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';

import {
  applyWebkitDirectoryAttrs,
  clearFileInputValue,
} from '@/utils/fileInputHelpers';
import { buildExportCandidates } from '@/utils/exportSelection';
import { formatCatalogEntryCopy } from '@/utils/lintIssueCatalog';
import { sanitizeOutputFilename } from '@/utils/outputFilename';
import {
  convertBulletin,
  convertMetarToIwxxm,
  fetchQualityMetrics,
  ingestCollect,
  lintTac,
  validateIwxxm,
} from '@/utils/api';

describe('EV-080 fileInputHelpers', () => {
  it('applyWebkitDirectoryAttrs no-ops on null and sets attrs on input', () => {
    applyWebkitDirectoryAttrs(null);
    const input = document.createElement('input');
    applyWebkitDirectoryAttrs(input);
    expect(input.getAttribute('webkitdirectory')).toBe('');
    expect(input.getAttribute('directory')).toBe('');
  });

  it('clearFileInputValue no-ops on null and clears value', () => {
    clearFileInputValue(null);
    const input = document.createElement('input');
    Object.defineProperty(input, 'value', {
      value: 'x',
      writable: true,
      configurable: true,
    });
    clearFileInputValue(input);
    expect(input.value).toBe('');
  });
});

describe('EV-080 exportSelection / lintIssueCatalog / outputFilename edges', () => {
  it('buildExportCandidates defaults missing sessionOutputs', () => {
    const list = buildExportCandidates({
      droppedFiles: [
        {
          id: 'd1',
          name: 'a.xml',
          source: 'drop',
          product: 'metar',
          iwxxmXml: '<x/>',
        },
      ],
    });
    expect(list.some((c) => c.id === 'd1')).toBe(true);
  });

  it('formatCatalogEntryCopy omits url when source_url absent', () => {
    const text = formatCatalogEntryCopy({
      code: 'X',
      severity: 'info',
      message_template: 'msg',
      product: 'metar',
      tags: [],
      source_id: 'SRC1',
    });
    expect(text).toContain('source: SRC1');
    expect(text).not.toMatch(/https?:/);
  });

  it('formatCatalogEntryCopy includes source_url when present', () => {
    const text = formatCatalogEntryCopy({
      code: 'Y',
      severity: 'info',
      message_template: 'msg',
      product: null,
      tags: [],
      source_id: 'SRC2',
      source_url: 'https://example.test/doc',
    });
    expect(text).toContain('https://example.test/doc');
  });

  it('sanitizeOutputFilename keeps last path segment', () => {
    expect(sanitizeOutputFilename('dir\\sub/name.xml')).toBe('name');
    expect(sanitizeOutputFilename('')).toBe('manual_input');
  });
});

describe('EV-080 api.json catch fallbacks and quality metrics defaults', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Boom',
        json: vi.fn().mockRejectedValue(new Error('bad json')),
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('convertMetarToIwxxm uses statusText when json fails', async () => {
    await expect(convertMetarToIwxxm({ manualText: 'METAR' })).rejects.toThrow(
      /Boom|HTTP 500/,
    );
  });

  it('convertBulletin uses statusText when json fails', async () => {
    await expect(
      convertBulletin({
        manualText: 'SAUS31 KZNY 121200\nMETAR KJFK=',
        product: 'METAR',
      }),
    ).rejects.toThrow(/Boom|HTTP 500/);
  });

  it('ingestCollect non-501 error uses statusText when json fails', async () => {
    await expect(ingestCollect({ manualText: '<collect/>' })).rejects.toThrow(
      /Boom|HTTP 500/,
    );
  });

  it('lintTac uses statusText when json fails', async () => {
    await expect(lintTac({ manualText: 'METAR' })).rejects.toThrow(/Boom|HTTP 500/);
  });

  it('validateIwxxm uses statusText when json fails', async () => {
    await expect(validateIwxxm({ xmlContent: '<x/>' })).rejects.toThrow(
      /Boom|HTTP 500/,
    );
  });

  it('ingestCollect 501 uses empty body fallbacks', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 501,
        statusText: 'NI',
        json: vi.fn().mockRejectedValue(new Error('bad json')),
      }),
    );
    await expect(ingestCollect({ manualText: '<collect/>' })).rejects.toThrow(
      /not implemented/i,
    );
  });

  it('fetchQualityMetrics defaults missing summaries and files', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: vi.fn().mockResolvedValue({ generated_at: 't', iwxxm_pin: 'p' }),
      }),
    );
    const body = await fetchQualityMetrics();
    expect(body.summaries).toEqual([]);
    expect(body.files).toEqual([]);
  });
});

describe('EV-080 convertBulletin detail message branches', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('prefers detail string when detail is not an object with message', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        statusText: 'Bad',
        json: vi.fn().mockResolvedValue({ detail: 'plain-detail', message: 'msg' }),
      }),
    );
    await expect(
      convertBulletin({
        manualText: 'SAUS31 KZNY 121200\nMETAR=',
        product: 'METAR',
      }),
    ).rejects.toThrow('plain-detail');
  });

  it('falls through to error.message when detail is absent', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 502,
        statusText: 'Bad Gateway',
        json: vi.fn().mockResolvedValue({ message: 'upstream' }),
      }),
    );
    await expect(
      convertBulletin({
        manualText: 'SAUS31 KZNY 121200\nMETAR=',
        product: 'METAR',
      }),
    ).rejects.toThrow('upstream');
  });

  it('falls through to HTTP status when detail and message are absent', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 502,
        statusText: 'Bad Gateway',
        json: vi.fn().mockResolvedValue({}),
      }),
    );
    await expect(
      convertBulletin({
        manualText: 'SAUS31 KZNY 121200\nMETAR=',
        product: 'METAR',
      }),
    ).rejects.toThrow('HTTP 502');
  });

  it('ingestCollect prefers nested detail.message then message then HTTP', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        statusText: 'Bad',
        json: vi.fn().mockResolvedValue({ detail: { message: 'nested' } }),
      }),
    );
    await expect(ingestCollect({ manualText: '<collect/>' })).rejects.toThrow('nested');

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        statusText: 'Bad',
        json: vi.fn().mockResolvedValue({ message: 'top' }),
      }),
    );
    await expect(ingestCollect({ manualText: '<collect/>' })).rejects.toThrow('top');

    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 418,
        statusText: 'Teapot',
        json: vi.fn().mockResolvedValue({}),
      }),
    );
    await expect(ingestCollect({ manualText: '<collect/>' })).rejects.toThrow(/418/);
  });
});
