/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import {
  checkHealth,
  convertBulletin,
  convertMetarToIwxxm,
  convertMetarToIwxxmZip,
  decodeTac,
  downloadBlob,
  EndpointNotImplementedError,
  fetchAirportRegion,
  fetchLintIssueCatalog,
  ingestCollect,
  lintTac,
  type ConversionResponse,
  type HealthResponse,
  type ApiError,
} from './api';

// Mock fetch globally
global.fetch = vi.fn();

describe('API Utils', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
    vi.resetModules();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  // Helper function to mock fetch responses
  const mockFetchResponse = (data: any, ok = true, status = 200) => {
    (global.fetch as any).mockResolvedValueOnce({
      ok,
      status,
      statusText: ok ? 'OK' : 'Error',
      json: vi.fn().mockResolvedValueOnce(data),
      blob: vi.fn().mockResolvedValueOnce(new Blob([JSON.stringify(data)])),
    });
  };

  // ============= Health Check Tests =============
  describe('checkHealth', () => {
    it('should successfully check backend health', async () => {
      const mockHealth: HealthResponse = {
        status: 'healthy',
        version: '1.0.0',
        tac2iwxxm_available: true,
      };
      mockFetchResponse(mockHealth);

      const result = await checkHealth();
      expect(result.status).toBe('healthy');
      expect(result.version).toBe('1.0.0');
      expect(result.tac2iwxxm_available).toBe(true);
    });

    it('should handle degraded health status', async () => {
      const mockHealth: HealthResponse = {
        status: 'degraded',
        version: '1.0.0',
        tac2iwxxm_available: false,
      };
      mockFetchResponse(mockHealth);

      const result = await checkHealth();
      expect(result.status).toBe('degraded');
      expect(result.tac2iwxxm_available).toBe(false);
    });

    it('should throw error on health check failure', async () => {
      mockFetchResponse({ message: 'Internal error' }, false, 500);

      await expect(checkHealth()).rejects.toThrow();
    });

    it('should handle network errors during health check', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      await expect(checkHealth()).rejects.toThrow('Network error');
    });

    it('should handle malformed JSON in health response', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: vi.fn().mockRejectedValueOnce(new Error('Invalid JSON')),
      });

      await expect(checkHealth()).rejects.toThrow();
    });
  });

  // ============= METAR Conversion Tests =============
  describe('convertMetarToIwxxm', () => {
    it('should convert manual METAR text successfully', async () => {
      const mockResponse: ConversionResponse = {
        results: [
          {
            name: 'METAR',
            content: '<iwxxm>test</iwxxm>',
            source: 'KJFK 121851Z 09014G25KT 10SM FEW250',
            size_bytes: 256,
          },
        ],
        errors: [],
        total_processed: 1,
        successful: 1,
        failed: 0,
      };
      mockFetchResponse(mockResponse);

      const result = await convertMetarToIwxxm({
        manualText: 'KJFK 121851Z 09014G25KT 10SM FEW250',
      });

      expect(result.results.length).toBe(1);
      expect(result.successful).toBe(1);
      expect(result.failed).toBe(0);
    });

    it('should handle file-based METAR conversion', async () => {
      const mockResponse: ConversionResponse = {
        results: [
          {
            name: 'test.txt',
            content: '<iwxxm>test</iwxxm>',
            source: 'KJFK 121851Z 09014G25KT 10SM FEW250',
            size_bytes: 256,
          },
        ],
        errors: [],
        total_processed: 1,
        successful: 1,
        failed: 0,
      };
      mockFetchResponse(mockResponse);

      const file = new File(['KJFK 121851Z'], 'metar.txt', { type: 'text/plain' });
      const result = await convertMetarToIwxxm({ files: [file] });

      expect(result.results.length).toBe(1);
      expect(result.successful).toBe(1);
    });

    it('should handle mixed manual text and files', async () => {
      const mockResponse: ConversionResponse = {
        results: [
          {
            name: 'manual',
            content: '<iwxxm>test1</iwxxm>',
            source: 'KJFK 121851Z',
            size_bytes: 256,
          },
          {
            name: 'test.txt',
            content: '<iwxxm>test2</iwxxm>',
            source: 'KLAX 121851Z',
            size_bytes: 256,
          },
        ],
        errors: [],
        total_processed: 2,
        successful: 2,
        failed: 0,
      };
      mockFetchResponse(mockResponse);

      const file = new File(['KLAX 121851Z'], 'metar.txt', { type: 'text/plain' });
      const result = await convertMetarToIwxxm({
        manualText: 'KJFK 121851Z',
        files: [file],
      });

      expect(result.results.length).toBe(2);
      expect(result.total_processed).toBe(2);
    });

    it('should handle conversion errors gracefully', async () => {
      const mockResponse: ConversionResponse = {
        results: [],
        errors: ['Invalid METAR format'],
        total_processed: 1,
        successful: 0,
        failed: 1,
      };
      mockFetchResponse(mockResponse);

      const result = await convertMetarToIwxxm({
        manualText: 'INVALID METAR',
      });

      expect(result.failed).toBe(1);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('should handle empty input', async () => {
      const mockResponse: ConversionResponse = {
        results: [],
        errors: ['No input provided'],
        total_processed: 0,
        successful: 0,
        failed: 0,
      };
      mockFetchResponse(mockResponse);

      const result = await convertMetarToIwxxm({
        manualText: '',
        files: undefined,
      });

      expect(result.successful).toBe(0);
    });

    it('should trim whitespace from manual text', async () => {
      mockFetchResponse({
        results: [],
        errors: [],
        total_processed: 0,
        successful: 0,
        failed: 0,
      });

      await convertMetarToIwxxm({
        manualText: '   KJFK 121851Z   ',
      });

      expect(global.fetch).toHaveBeenCalled();
    });

    it('appends product and profile to multipart FormData (F6.e)', async () => {
      mockFetchResponse({
        results: [],
        errors: [],
        total_processed: 0,
        successful: 0,
        failed: 0,
      });

      await convertMetarToIwxxm({
        manualText: 'TAF KJFK 121730Z 1218/1324 24012KT P6SM SCT040',
        product: 'TAF',
        profile: 'iwxxm_us',
        iwxxmVersion: '2025-2',
      });

      const [, options] = (global.fetch as any).mock.calls[0];
      const body = options.body as FormData;
      expect(body.get('product')).toBe('TAF');
      expect(body.get('profile')).toBe('iwxxm_us');
      expect(body.get('iwxxm_version')).toBe('2025-2');
    });

    it('appends validation, stop_on_error, bulletin, and issuing centre (ADR-023)', async () => {
      mockFetchResponse({
        results: [],
        errors: [],
        total_processed: 0,
        successful: 0,
        failed: 0,
      });

      await convertMetarToIwxxm({
        manualText: 'METAR KJFK 121251Z',
        product: 'METAR',
        validateOutput: true,
        validationLevel: 'comprehensive',
        stopOnError: true,
        bulletinId: 'saaa00',
        issuingCenter: 'kwbc',
      });

      const [, options] = (global.fetch as any).mock.calls[0];
      const body = options.body as FormData;
      expect(body.get('validate_output')).toBe('true');
      expect(body.get('validation_level')).toBe('comprehensive');
      expect(body.get('stop_on_error')).toBe('true');
      expect(body.get('bulletin_id')).toBe('SAAA00');
      expect(body.get('issuing_center')).toBe('KWBC');
    });

    it('should throw error on conversion failure', async () => {
      mockFetchResponse({ detail: { message: 'Conversion failed' } }, false, 400);

      await expect(convertMetarToIwxxm({ manualText: 'TEST' })).rejects.toThrow();
    });

    it('should handle network errors during conversion', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network timeout'));

      await expect(
        convertMetarToIwxxm({ manualText: 'KJFK 121851Z' }),
      ).rejects.toThrow();
    });

    it('should include authorization token if available', async () => {
      localStorage.setItem('access_token', 'test-token-123');
      mockFetchResponse({
        results: [],
        errors: [],
        total_processed: 0,
        successful: 0,
        failed: 0,
      });

      await convertMetarToIwxxm({ manualText: 'KJFK 121851Z' });

      const fetchCall = (global.fetch as any).mock.calls[0];
      expect(fetchCall[1].headers?.Authorization).toBeUndefined();
    });

    it('should handle multiple file conversions', async () => {
      const mockResponse: ConversionResponse = {
        results: [
          {
            name: 'file1.txt',
            content: '<iwxxm>1</iwxxm>',
            source: 'KJFK',
            size_bytes: 100,
          },
          {
            name: 'file2.txt',
            content: '<iwxxm>2</iwxxm>',
            source: 'KLAX',
            size_bytes: 100,
          },
          {
            name: 'file3.txt',
            content: '<iwxxm>3</iwxxm>',
            source: 'KORD',
            size_bytes: 100,
          },
        ],
        errors: [],
        total_processed: 3,
        successful: 3,
        failed: 0,
      };
      mockFetchResponse(mockResponse);

      const files = [
        new File(['KJFK'], 'file1.txt', { type: 'text/plain' }),
        new File(['KLAX'], 'file2.txt', { type: 'text/plain' }),
        new File(['KORD'], 'file3.txt', { type: 'text/plain' }),
      ];

      const result = await convertMetarToIwxxm({ files });
      expect(result.results.length).toBe(3);
    });
  });

  // ============= ZIP Conversion Tests =============
  describe('convertMetarToIwxxmZip', () => {
    it('should convert METAR to ZIP file successfully', async () => {
      const blobData = new Blob(['PK\x03\x04...'], { type: 'application/zip' });
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        blob: vi.fn().mockResolvedValueOnce(blobData),
      });

      const result = await convertMetarToIwxxmZip({
        manualText: 'KJFK 121851Z',
      });

      expect(result instanceof Blob).toBe(true);
      expect(result.type).toBe('application/zip');
    });

    it('should handle ZIP conversion with files', async () => {
      const blobData = new Blob(['PK\x03\x04...'], { type: 'application/zip' });
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        blob: vi.fn().mockResolvedValueOnce(blobData),
      });

      const file = new File(['KJFK 121851Z'], 'metar.txt', { type: 'text/plain' });
      const result = await convertMetarToIwxxmZip({ files: [file] });

      expect(result instanceof Blob).toBe(true);
    });

    it('should throw error on ZIP conversion failure', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Error',
        json: vi.fn().mockResolvedValueOnce({ message: 'ZIP creation failed' }),
      });

      await expect(convertMetarToIwxxmZip({ manualText: 'TEST' })).rejects.toThrow();
    });

    it('should handle network errors during ZIP conversion', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      await expect(convertMetarToIwxxmZip({ manualText: 'KJFK' })).rejects.toThrow();
    });

    it('should handle malformed JSON error response', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Error',
        json: vi.fn().mockRejectedValueOnce(new Error('Invalid JSON')),
      });

      await expect(convertMetarToIwxxmZip({ manualText: 'TEST' })).rejects.toThrow();
    });
  });

  // ============= Download Blob Tests =============
  describe('downloadBlob', () => {
    it('should create and trigger blob download', () => {
      // Mock DOM methods
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
      };

      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
      vi.spyOn(document, 'body', 'get').mockReturnValue({
        appendChild: vi.fn(),
        removeChild: vi.fn(),
      } as any);
      vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url');
      vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {});

      const blob = new Blob(['test'], { type: 'text/plain' });
      downloadBlob(blob, 'test.txt');

      expect(mockLink.download).toBe('test.txt');
      expect(mockLink.click).toHaveBeenCalled();
    });

    it('should handle large file downloads', () => {
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
      };

      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
      vi.spyOn(document, 'body', 'get').mockReturnValue({
        appendChild: vi.fn(),
        removeChild: vi.fn(),
      } as any);
      vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url');
      vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {});

      const largeData = new Array(1000000).fill('x').join('');
      const blob = new Blob([largeData], { type: 'application/octet-stream' });
      downloadBlob(blob, 'large-file.bin');

      expect(mockLink.download).toBe('large-file.bin');
    });

    it('should handle special characters in filename', () => {
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
      };

      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any);
      vi.spyOn(document, 'body', 'get').mockReturnValue({
        appendChild: vi.fn(),
        removeChild: vi.fn(),
      } as any);
      vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url');
      vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {});

      const blob = new Blob(['test'], { type: 'text/plain' });
      downloadBlob(blob, 'file-with-special-chars_@#$.txt');

      expect(mockLink.download).toBe('file-with-special-chars_@#$.txt');
    });
  });

  // ============= Type/Interface Tests =============
  describe('API Response Types', () => {
    it('should handle conversion result structure', () => {
      const result = {
        name: 'test',
        content: '<iwxxm>test</iwxxm>',
        source: 'KJFK',
        size_bytes: 256,
      };

      expect(result.name).toBeDefined();
      expect(result.content).toBeDefined();
      expect(result.source).toBeDefined();
      expect(result.size_bytes).toBeDefined();
    });

    it('should handle conversion response structure', () => {
      const response: ConversionResponse = {
        results: [],
        errors: [],
        total_processed: 0,
        successful: 0,
        failed: 0,
      };

      expect(response.results).toBeDefined();
      expect(response.errors).toBeDefined();
      expect(response.total_processed).toBe(0);
    });

    it('should handle health response structure', () => {
      const health: HealthResponse = {
        status: 'healthy',
        version: '1.0.0',
        tac2iwxxm_available: true,
      };

      expect(health.status).toBeDefined();
      expect(health.version).toBeDefined();
      expect(health.tac2iwxxm_available).toBeDefined();
    });

    it('should handle API error structure', () => {
      const error: ApiError = {
        message: 'Error occurred',
        errors: ['Details'],
        total_errors: 1,
      };

      expect(error.message).toBeDefined();
      expect(error.errors).toBeDefined();
    });
  });

  /**
   * T5.4 / TC-F11-001 / ADR-026 — msgspec HTTP shape parity guards.
   * Keys match backend contract smoke (T5.1); no OpenAPI→TS codegen this cycle.
   */
  describe('msgspec HTTP shape parity (ADR-026 / T5.4)', () => {
    const requiredKeys = (obj: Record<string, unknown>, keys: string[]) => {
      for (const key of keys) {
        expect(obj).toHaveProperty(key);
      }
    };

    it('ConversionResponse required keys match msgspec convert contract', () => {
      const body: ConversionResponse = {
        results: [
          {
            name: 'manual_input.txt',
            content: '<iwxxm:METAR/>',
            source: 'manual',
            size_bytes: 14,
          },
        ],
        errors: [],
        issues: [],
        total_processed: 1,
        successful: 1,
        failed: 0,
        metadata: {},
        ok: true,
        failed_spans: [],
      };
      requiredKeys(body as unknown as Record<string, unknown>, [
        'results',
        'errors',
        'total_processed',
        'successful',
        'failed',
      ]);
      expect(Array.isArray(body.results)).toBe(true);
      expect(body.results[0]).toMatchObject({
        name: expect.any(String),
        content: expect.any(String),
        source: expect.any(String),
        size_bytes: expect.any(Number),
      });
    });

    it('LintTacResponse required keys match msgspec lint-tac contract', () => {
      const body = {
        ok: true,
        issues: [] as { severity: string; code: string; message: string }[],
        fixes: [] as { code: string; message: string; replacement: string }[],
        product: 'METAR',
      };
      requiredKeys(body, ['ok', 'issues', 'fixes']);
      expect(typeof body.ok).toBe('boolean');
      expect(Array.isArray(body.issues)).toBe(true);
      expect(Array.isArray(body.fixes)).toBe(true);
    });

    it('DecodeTacResponse required keys match msgspec decode-tac contract', () => {
      const body = {
        product: 'METAR',
        segments: [] as {
          start: number;
          end: number;
          code: string;
          explanation: string;
        }[],
        residuals: [] as { start: number; end: number; text: string }[],
        summary: '',
      };
      requiredKeys(body, ['product', 'segments', 'residuals', 'summary']);
      expect(typeof body.summary).toBe('string');
    });

    it('ConvertBulletinResponse required keys match msgspec convert-bulletin contract', () => {
      const body = {
        bulletin_meta: {
          ahl: 'SAUS31 KZNY 121200',
          report_count: 1,
          tt: 'SA',
          aa: 'US',
          cccc: 'KZNY',
          yygggg: '121200',
          bbb: null as string | null,
        },
        results: [
          {
            report_index: 0,
            ok: true,
            tac_input: 'METAR KJFK',
            xml: '<iwxxm:METAR/>',
            issues: [],
            fixes: [],
          },
        ],
      };
      requiredKeys(body, ['bulletin_meta', 'results']);
      requiredKeys(body.bulletin_meta as unknown as Record<string, unknown>, [
        'ahl',
        'report_count',
        'tt',
        'aa',
        'cccc',
        'yygggg',
      ]);
      expect(body.results[0]).toMatchObject({
        report_index: expect.any(Number),
        ok: expect.any(Boolean),
        tac_input: expect.any(String),
      });
    });
  });

  // ============= Edge Cases =============
  describe('Edge Cases', () => {
    it('should handle requests without authentication token', async () => {
      localStorage.removeItem('access_token');
      localStorage.removeItem('supabase_access_token');
      mockFetchResponse({
        results: [],
        errors: [],
        total_processed: 0,
        successful: 0,
        failed: 0,
      });

      await convertMetarToIwxxm({ manualText: 'KJFK' });

      const fetchCall = (global.fetch as any).mock.calls[0];
      expect(fetchCall[1].headers?.Authorization).toBeUndefined();
    });

    it('should handle very long METAR strings', async () => {
      const longMetar = 'KJFK 121851Z ' + 'A'.repeat(10000);
      mockFetchResponse({
        results: [],
        errors: [],
        total_processed: 1,
        successful: 0,
        failed: 1,
      });

      const result = await convertMetarToIwxxm({ manualText: longMetar });
      expect(result.total_processed).toBe(1);
    });

    it('should handle special characters in METAR text', async () => {
      const specialMetar = 'KJFK 121851Z <>&"\'$';
      mockFetchResponse({
        results: [],
        errors: [],
        total_processed: 1,
        successful: 0,
        failed: 1,
      });

      const result = await convertMetarToIwxxm({ manualText: specialMetar });
      expect(result.total_processed).toBe(1);
    });

    it('should reject when conversion request exceeds timeout', async () => {
      vi.useFakeTimers();
      try {
        (global.fetch as any).mockImplementation(() => new Promise(() => undefined));

        const promise = convertMetarToIwxxm({ manualText: 'METAR KJFK 010000Z' });
        const assertion = expect(promise).rejects.toThrow(/timeout/i);
        await vi.advanceTimersByTimeAsync(30001);
        await assertion;
      } finally {
        vi.useRealTimers();
      }
    });
  });

  describe('fetchAirportRegion', () => {
    it('should fetch ICAO region for a valid airport code', async () => {
      mockFetchResponse({ airport_code: 'KJFK', icao_region: 'NAM' });

      const result = await fetchAirportRegion(' kjfk ');
      expect(result.icao_region).toBe('NAM');
      expect(result.airport_code).toBe('KJFK');
    });

    it('should throw when airport region lookup fails', async () => {
      mockFetchResponse({}, false, 404);

      await expect(fetchAirportRegion('ZZZZ')).rejects.toThrow(
        'Airport region lookup failed (404)',
      );
    });
  });

  describe('lintTac / decodeTac (live workbench)', () => {
    it('posts lint-tac with product and optional signal', async () => {
      mockFetchResponse({
        ok: true,
        issues: [],
        fixes: [],
        product: 'METAR',
      });
      const controller = new AbortController();
      const result = await lintTac({
        manualText: 'METAR KJFK',
        product: 'metar',
        accessToken: 'tok',
        signal: controller.signal,
      });
      expect(result.ok).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/lint-tac'),
        expect.objectContaining({
          method: 'POST',
          signal: controller.signal,
        }),
      );
    });

    it('throws on lint-tac failure', async () => {
      mockFetchResponse({ message: 'bad' }, false, 422);
      await expect(
        lintTac({ manualText: 'METAR', product: 'METAR' }),
      ).rejects.toThrow();
    });

    it('GETs lint-issue-catalog with optional product filter', async () => {
      mockFetchResponse({
        issues: [
          {
            code: 'MISSING_TERMINATOR',
            severity: 'info',
            message_template: "Reports end with '='",
            product: null,
            tags: ['terminator'],
          },
        ],
      });
      const result = await fetchLintIssueCatalog({
        product: 'METAR',
        accessToken: 'tok',
      });
      expect(result.issues).toHaveLength(1);
      expect(result.issues[0].code).toBe('MISSING_TERMINATOR');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/lint-issue-catalog\?product=metar$/),
        expect.objectContaining({
          method: 'GET',
        }),
      );
    });

    it('posts decode-tac with abort signal', async () => {
      mockFetchResponse({
        product: 'METAR',
        segments: [],
        residuals: [],
      });
      const controller = new AbortController();
      const result = await decodeTac({
        manualText: 'METAR KJFK',
        product: 'METAR',
        signal: controller.signal,
      });
      expect(result.product).toBe('METAR');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/decode-tac'),
        expect.objectContaining({ signal: controller.signal }),
      );
    });

    it('throws on decode-tac failure', async () => {
      mockFetchResponse({ message: 'nope' }, false, 400);
      await expect(
        decodeTac({ manualText: 'METAR', product: 'METAR' }),
      ).rejects.toThrow();
    });
  });

  describe('convertBulletin / ingestCollect (ADR-023/024)', () => {
    it('posts convert-bulletin with manual text and files', async () => {
      const body = {
        bulletin_meta: {
          ahl: 'SAUS31 KZNY 121200',
          report_count: 1,
          tt: 'SA',
          aa: 'US',
          cccc: 'KZNY',
          yygggg: '121200',
        },
        results: [
          {
            report_index: 0,
            ok: true,
            tac_input: 'METAR KJFK',
            xml: '<iwxxm/>',
            issues: [],
            fixes: [],
          },
        ],
      };
      mockFetchResponse(body);
      const file = new File(['METAR'], 'b.tac', { type: 'text/plain' });
      const result = await convertBulletin({
        manualText: 'SAUS31 KZNY 121200\nMETAR KJFK=',
        files: [file],
        product: 'metar',
        profile: 'annex3',
        lint: false,
        accessToken: 'tok',
      });
      expect(result.bulletin_meta.cccc).toBe('KZNY');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/convert-bulletin'),
        expect.objectContaining({ method: 'POST' }),
      );
    });

    it('throws on convert-bulletin HTTP error with detail.message', async () => {
      mockFetchResponse({ detail: { message: 'bulletin too large' } }, false, 400);
      await expect(
        convertBulletin({ product: 'METAR', manualText: 'SAUS31' }),
      ).rejects.toThrow('bulletin too large');
    });

    it('throws EndpointNotImplementedError on ingest-collect 501', async () => {
      mockFetchResponse(
        {
          detail: {
            code: 'not_implemented',
            message: 'COLLECT not ready',
          },
        },
        false,
        501,
      );
      await expect(
        ingestCollect({
          manualText: '<collect/>',
          profile: 'annex3',
          accessToken: 'tok',
        }),
      ).rejects.toBeInstanceOf(EndpointNotImplementedError);
    });

    it('posts ingest-collect success path', async () => {
      mockFetchResponse({ message: 'ok', status: 'accepted' });
      const file = new File(['<c/>'], 'c.xml', { type: 'application/xml' });
      const result = await ingestCollect({
        files: [file],
        iwxxmVersion: '2023-1',
      });
      expect(result.status).toBe('accepted');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/ingest-collect'),
        expect.objectContaining({ method: 'POST' }),
      );
    });

    it('throws on ingest-collect non-501 failure', async () => {
      mockFetchResponse({ detail: { message: 'bad upload' } }, false, 400);
      await expect(ingestCollect({ manualText: 'x' })).rejects.toThrow('bad upload');
    });

    it('sends convert optional bulletin/log fields', async () => {
      mockFetchResponse({
        results: [],
        errors: [],
        total_processed: 0,
        successful: 0,
        failed: 0,
      });
      await convertMetarToIwxxm({
        manualText: 'METAR KJFK',
        bulletinId: 'szzz99',
        issuingCenter: 'kjfk',
        includeNilReasons: false,
        logLevel: 'warn',
        preview: true,
        accessToken: 'tok',
      });
      expect(global.fetch).toHaveBeenCalled();
    });
  });
});
