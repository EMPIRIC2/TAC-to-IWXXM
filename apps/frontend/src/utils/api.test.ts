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
  fetchQualityMetrics,
  fetchQualityMetricsDetail,
  fetchSchemaStatus,
  ingestCollect,
  lintTac,
  massIngestFiles,
  validateIwxxm,
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

    it('appends CA_ECCC extensions and exchange_output (EV-073)', async () => {
      mockFetchResponse({
        results: [],
        errors: [],
        total_processed: 0,
        successful: 0,
        failed: 0,
      });

      await convertMetarToIwxxm({
        manualText: 'METAR CYUL 231800Z',
        profile: 'ca_eccc',
        extensions: ['IWXXM_CA'],
        exchangeOutput: true,
      });

      const [, options] = (global.fetch as any).mock.calls[0];
      const body = options.body as FormData;
      expect(body.getAll('extensions')).toEqual(['IWXXM_CA']);
      expect(body.get('exchange_output')).toBe('true');
    });

    it('should throw error on conversion failure', async () => {
      mockFetchResponse({ detail: { message: 'Conversion failed' } }, false, 400);

      await expect(convertMetarToIwxxm({ manualText: 'TEST' })).rejects.toThrow();
    });

    it('falls back to top-level message when convert error detail is absent', async () => {
      mockFetchResponse({ message: 'Validation rejected' }, false, 422);

      await expect(convertMetarToIwxxm({ manualText: 'TEST' })).rejects.toThrow(
        'Validation rejected',
      );
    });

    it('falls back to HTTP status when convert error body has no message fields', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 503,
        statusText: '',
        json: vi.fn().mockResolvedValueOnce({}),
      });

      await expect(convertMetarToIwxxm({ manualText: 'TEST' })).rejects.toThrow(
        'HTTP 503',
      );
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
   * Keys match backend contract smoke; OpenAPI→TS types live in openapiTypes (EV-052).
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

    it('prefers nested API details and falls back to message fields', async () => {
      mockFetchResponse({ detail: { message: 'nested lint failure' } }, false, 422);
      await expect(lintTac({ manualText: 'METAR' })).rejects.toThrow(
        'nested lint failure',
      );

      mockFetchResponse({ message: 'validation message' }, false, 422);
      await expect(validateIwxxm({ manualText: 'METAR' })).rejects.toThrow(
        'validation message',
      );

      mockFetchResponse({ detail: { message: ['not text'] }, message: '' }, false, 503);
      await expect(lintTac({ manualText: 'METAR' })).rejects.toThrow('HTTP 503');
    });

    it('posts validate with TAC/XML and returns ValidateResponse', async () => {
      mockFetchResponse({
        is_valid: true,
        version: '2025-2',
        profile: 'annex3',
        layers_run: ['ALL'],
        layers_passed: ['ALL'],
        layers_failed: [],
        total_issues: 0,
        issues: [],
        issues_by_layer: {},
        package_ok: true,
        package_issues: [],
      });
      const result = await validateIwxxm({
        manualText: 'METAR KJFK 010000Z 18010KT 10SM SKC 20/10 A2992',
        xmlContent: '<iwxxm:METAR/>',
      });
      expect(result.is_valid).toBe(true);
      expect(result.version).toBe('2025-2');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/validate'),
        expect.objectContaining({ method: 'POST' }),
      );
      const [, init] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls.at(-1)!;
      const body = init.body as FormData;
      expect(body.get('manual_text')).toContain('METAR KJFK');
      expect(body.get('xml_content')).toContain('iwxxm:METAR');
      expect(body.getAll('layers')).toEqual(['ALL']);
    });

    it('posts validate with CA_ECCC extensions (EV-073)', async () => {
      mockFetchResponse({
        is_valid: true,
        version: '3.0.0',
        profile: 'ca_eccc',
        layers_run: ['ALL'],
        layers_passed: ['ALL'],
        layers_failed: [],
        total_issues: 0,
        issues: [],
        issues_by_layer: {},
        package_ok: true,
        package_issues: [],
      });
      await validateIwxxm({
        xmlContent: '<iwxxm:METAR/>',
        profile: 'ca_eccc',
        extensions: ['IWXXM_CA'],
      });
      const [, init] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls.at(-1)!;
      const body = init.body as FormData;
      expect(body.getAll('extensions')).toEqual(['IWXXM_CA']);
    });

    it('posts validate with stop_on_error false when requested', async () => {
      mockFetchResponse({
        is_valid: true,
        version: '2025-2',
        profile: 'annex3',
        layers_run: ['ALL'],
        layers_passed: ['ALL'],
        layers_failed: [],
        total_issues: 0,
        issues: [],
        issues_by_layer: {},
        package_ok: true,
        package_issues: [],
      });
      await validateIwxxm({
        xmlContent: '<iwxxm:METAR/>',
        stopOnError: false,
      });
      const [, init] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls.at(-1)!;
      expect((init.body as FormData).get('stop_on_error')).toBe('false');
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
      expect(result.issues[0]!.code).toBe('MISSING_TERMINATOR');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/lint-issue-catalog\?product=metar$/),
        expect.objectContaining({
          method: 'GET',
        }),
      );
    });

    it('GETs lint-issue-catalog with optional family filter', async () => {
      mockFetchResponse({
        issues: [
          {
            code: 'XML_SCHEMA',
            severity: 'error',
            message_template: 'XSD',
            family: 'iwxxm',
            tags: ['xsd'],
          },
        ],
      });
      const result = await fetchLintIssueCatalog({ family: 'IWXXM' });
      expect(result.issues).toHaveLength(1);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/lint-issue-catalog\?family=iwxxm$/),
        expect.objectContaining({ method: 'GET' }),
      );
    });

    it('GETs lint-issue-catalog with issue_type and source_access filters', async () => {
      mockFetchResponse({ issues: [] });
      await fetchLintIssueCatalog({
        issue_type: 'Presence',
        source_access: 'Paywall',
      });
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringMatching(
          /\/lint-issue-catalog\?issue_type=presence&source_access=paywall$/,
        ),
        expect.objectContaining({ method: 'GET' }),
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

    it('uses FastAPI string detail on lint-issue-catalog failure', async () => {
      mockFetchResponse({ detail: 'catalog unavailable' }, false, 503);
      await expect(fetchLintIssueCatalog()).rejects.toThrow('catalog unavailable');
    });

    it('fetches quality-metrics list with product filter', async () => {
      mockFetchResponse({
        generated_at: '2026-08-10T00:00:00Z',
        iwxxm_pin: '2025-2',
        summaries: [{ product: 'metar', match_pass: 1 }],
        files: [{ stem: 'metar-A3-1', product: 'metar', tier: 'wmoPass' }],
      });
      const result = await fetchQualityMetrics({ product: 'METAR' });
      expect(result.files).toHaveLength(1);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/quality-metrics\?product=metar$/),
        expect.objectContaining({ method: 'GET' }),
      );
    });

    it('fetches quality-metrics detail by stem', async () => {
      mockFetchResponse({
        stem: 'metar-A3-1',
        product: 'metar',
        tier: 'wmoPass',
        match_status: 'equal',
        tac: 'METAR …=',
        official_xml: '<a/>',
        converted_xml: '<a/>',
        residuals: [],
        lint_issues: [],
        validate_issues: [],
      });
      const result = await fetchQualityMetricsDetail({ stem: 'metar-A3-1' });
      expect(result.match_status).toBe('equal');
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/quality-metrics\/metar-A3-1$/),
        expect.objectContaining({ method: 'GET' }),
      );
    });

    it('falls back when quality-metrics list error body is not JSON', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 503,
        statusText: 'Unavailable',
        json: vi.fn().mockRejectedValueOnce(new Error('not json')),
      });
      await expect(fetchQualityMetrics()).rejects.toThrow(
        /HTTP 503|Quality metrics fetch failed/,
      );
    });

    it('falls back when quality-metrics detail error body is not JSON', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: vi.fn().mockRejectedValueOnce(new Error('not json')),
      });
      await expect(fetchQualityMetricsDetail({ stem: 'missing' })).rejects.toThrow(
        /HTTP 404|Quality metrics detail failed/,
      );
    });

    it('falls back when lint-issue-catalog error body is not JSON', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 502,
        statusText: 'Bad Gateway',
        json: vi.fn().mockRejectedValueOnce(new Error('not json')),
      });
      await expect(fetchLintIssueCatalog({ product: 'taf' })).rejects.toThrow(
        /HTTP 502|Bad Gateway/,
      );
    });

    it('falls back when decode-tac error body is not JSON', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Server Error',
        json: vi.fn().mockRejectedValueOnce(new Error('not json')),
      });
      await expect(
        decodeTac({ manualText: 'METAR', product: 'METAR' }),
      ).rejects.toThrow(/HTTP 500|Server Error/);
    });

    it('uses nested detail.message on decode-tac failure', async () => {
      mockFetchResponse({ detail: { message: 'decode rejected' } }, false, 422);
      await expect(
        decodeTac({ manualText: 'METAR', product: 'METAR' }),
      ).rejects.toThrow('decode rejected');
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

    it('uses string detail and message fallbacks for convert-bulletin errors', async () => {
      mockFetchResponse({ detail: 'plain bulletin failure' }, false, 400);
      await expect(convertBulletin({ product: 'metar' })).rejects.toThrow(
        'plain bulletin failure',
      );

      mockFetchResponse({ message: 'missing bulletin body' }, false, 422);
      await expect(convertBulletin({ product: 'metar' })).rejects.toThrow(
        'missing bulletin body',
      );
    });

    it('uses bulletin defaults and stringifies a non-string detail error', async () => {
      mockFetchResponse(
        { detail: { code: 'invalid_bulletin' }, message: '' },
        false,
        422,
      );
      await expect(convertBulletin({ product: 'metar' })).rejects.toThrow(
        JSON.stringify({ code: 'invalid_bulletin' }),
      );

      mockFetchResponse({
        bulletin_meta: {
          ahl: null,
          report_count: 0,
          tt: null,
          aa: null,
          cccc: null,
          yygggg: null,
          bbb: null,
        },
        results: [],
      });
      await convertBulletin({ product: 'taf' });
      const [, options] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls.at(-1)!;
      const body = options.body as FormData;
      expect(body.get('manual_text')).toBeNull();
      expect(body.get('profile')).toBe('annex3');
      expect(body.get('lint')).toBe('true');
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

    it('uses COLLECT placeholder defaults when the 501 body has no details', async () => {
      mockFetchResponse({}, false, 501);
      await expect(ingestCollect({ manualText: '<collect/>' })).rejects.toMatchObject({
        message: 'COLLECT / FTBP ingest is not implemented yet (placeholder).',
        status: 501,
        code: 'not_implemented',
      });
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

    it('uses configured validation layers and false stop-on-error', async () => {
      mockFetchResponse({
        is_valid: false,
        version: '2025-2',
        profile: 'annex3',
        layers_run: ['XSD'],
        layers_passed: [],
        layers_failed: ['XSD'],
        total_issues: 1,
        issues: [],
        issues_by_layer: {},
        package_ok: false,
        package_issues: [],
      });

      await validateIwxxm({
        xmlContent: ' <iwxxm:METAR/> ',
        iwxxmVersion: '2023-1',
        layers: ['XSD', 'SCHEMATRON'],
        stopOnError: false,
      });
      const [, options] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls.at(-1)!;
      const body = options.body as FormData;
      expect(body.get('xml_content')).toBe('<iwxxm:METAR/>');
      expect(body.get('iwxxm_version')).toBe('2023-1');
      expect(body.get('stop_on_error')).toBe('false');
      expect(body.getAll('layers')).toEqual(['XSD', 'SCHEMATRON']);
    });

    it('throws on ingest-collect non-501 failure', async () => {
      mockFetchResponse({ detail: { message: 'bad upload' } }, false, 400);
      await expect(ingestCollect({ manualText: 'x' })).rejects.toThrow('bad upload');
    });

    it('falls back to top-level message for ingest-collect failures', async () => {
      mockFetchResponse({ message: 'collect payload invalid' }, false, 400);
      await expect(ingestCollect({ manualText: 'x' })).rejects.toThrow(
        'collect payload invalid',
      );
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

    it('uses default conversion fields when optional values are omitted', async () => {
      mockFetchResponse({
        results: [],
        errors: [],
        total_processed: 0,
        successful: 0,
        failed: 0,
      });
      await convertMetarToIwxxm({ manualText: '   ' });
      const [, options] = (global.fetch as ReturnType<typeof vi.fn>).mock.calls.at(-1)!;
      const body = options.body as FormData;
      expect(body.get('manual_text')).toBeNull();
      expect(body.get('product')).toBe('METAR');
      expect(body.get('profile')).toBe('annex3');
      expect(body.get('validate_output')).toBe('false');
      expect(body.get('include_nil_reasons')).toBe('true');
      expect(body.get('preview')).toBeNull();
    });
  });

  describe('massIngestFiles (F33 / EV-042)', () => {
    it('requires access token and at least one file', async () => {
      await expect(
        massIngestFiles({ files: [new File(['x'], 'a.tac')], accessToken: '  ' }),
      ).rejects.toThrow(/Sign in required/);
      await expect(massIngestFiles({ files: [], accessToken: 'tok' })).rejects.toThrow(
        /At least one file/,
      );
    });

    it('posts multipart to /ingest/mass and returns results', async () => {
      mockFetchResponse({
        accepted_count: 1,
        rejected_count: 0,
        results: [
          {
            name: 'a.tac',
            accepted: true,
            reason: null,
            size_bytes: 10,
            content: 'METAR',
          },
        ],
      });
      const file = new File(['METAR'], 'a.tac', { type: 'text/plain' });
      const result = await massIngestFiles({
        files: [file],
        accessToken: 'jwt-f33',
      });
      expect(result.accepted_count).toBe(1);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/ingest/mass'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            Authorization: 'Bearer jwt-f33',
          }),
        }),
      );
    });

    it('throws on mass ingest HTTP error', async () => {
      mockFetchResponse({ detail: { message: 'too many files' } }, false, 413);
      await expect(
        massIngestFiles({
          files: [new File(['x'], 'a.tac')],
          accessToken: 'tok',
        }),
      ).rejects.toThrow(/too many files/);
    });

    it('throws when mass ingest error body is not JSON', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Server Error',
        json: vi.fn().mockRejectedValueOnce(new Error('not json')),
      });
      await expect(
        massIngestFiles({
          files: [new File(['x'], 'a.tac')],
          accessToken: 'tok',
        }),
      ).rejects.toThrow(/HTTP 500|Mass ingest failed|Server Error/);
    });
  });

  describe('fetchSchemaStatus', () => {
    it('returns profile pin payload on success', async () => {
      mockFetchResponse({
        profile_pins: {
          ca_eccc: { extension_bundle_available: true, iwxxm_version: '3.0.0' },
        },
      });
      await expect(fetchSchemaStatus()).resolves.toEqual({
        profile_pins: {
          ca_eccc: { extension_bundle_available: true, iwxxm_version: '3.0.0' },
        },
      });
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/schema-status'),
      );
    });

    it('throws on HTTP error', async () => {
      mockFetchResponse({ detail: 'unavailable' }, false, 503);
      await expect(fetchSchemaStatus()).rejects.toThrow(/Schema status request failed/);
    });
  });
});
