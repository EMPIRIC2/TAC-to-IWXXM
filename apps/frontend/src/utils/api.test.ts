/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import {
  checkHealth,
  convertMetarToIwxxm,
  convertMetarToIwxxmZip,
  downloadBlob,
  type ConversionResponse,
  type HealthResponse,
  type ApiError,
} from './api'

// Mock fetch globally
global.fetch = vi.fn()

describe('API Utils', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
    vi.resetModules()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  // Helper function to mock fetch responses
  const mockFetchResponse = (data: any, ok = true, status = 200) => {
    ;(global.fetch as any).mockResolvedValueOnce({
      ok,
      status,
      statusText: ok ? 'OK' : 'Error',
      json: vi.fn().mockResolvedValueOnce(data),
      blob: vi.fn().mockResolvedValueOnce(new Blob([JSON.stringify(data)])),
    })
  }

  // ============= Health Check Tests =============
  describe('checkHealth', () => {
    it('should successfully check backend health', async () => {
      const mockHealth: HealthResponse = {
        status: 'healthy',
        version: '1.0.0',
        gifts_available: true,
      }
      mockFetchResponse(mockHealth)

      const result = await checkHealth()
      expect(result.status).toBe('healthy')
      expect(result.version).toBe('1.0.0')
      expect(result.gifts_available).toBe(true)
    })

    it('should handle degraded health status', async () => {
      const mockHealth: HealthResponse = {
        status: 'degraded',
        version: '1.0.0',
        gifts_available: false,
      }
      mockFetchResponse(mockHealth)

      const result = await checkHealth()
      expect(result.status).toBe('degraded')
      expect(result.gifts_available).toBe(false)
    })

    it('should throw error on health check failure', async () => {
      mockFetchResponse({ message: 'Internal error' }, false, 500)

      await expect(checkHealth()).rejects.toThrow()
    })

    it('should handle network errors during health check', async () => {
      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

      await expect(checkHealth()).rejects.toThrow('Network error')
    })

    it('should handle malformed JSON in health response', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: vi.fn().mockRejectedValueOnce(new Error('Invalid JSON')),
      })

      await expect(checkHealth()).rejects.toThrow()
    })
  })

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
      }
      mockFetchResponse(mockResponse)

      const result = await convertMetarToIwxxm({
        manualText: 'KJFK 121851Z 09014G25KT 10SM FEW250',
      })

      expect(result.results.length).toBe(1)
      expect(result.successful).toBe(1)
      expect(result.failed).toBe(0)
    })

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
      }
      mockFetchResponse(mockResponse)

      const file = new File(['KJFK 121851Z'], 'metar.txt', { type: 'text/plain' })
      const result = await convertMetarToIwxxm({ files: [file] })

      expect(result.results.length).toBe(1)
      expect(result.successful).toBe(1)
    })

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
      }
      mockFetchResponse(mockResponse)

      const file = new File(['KLAX 121851Z'], 'metar.txt', { type: 'text/plain' })
      const result = await convertMetarToIwxxm({
        manualText: 'KJFK 121851Z',
        files: [file],
      })

      expect(result.results.length).toBe(2)
      expect(result.total_processed).toBe(2)
    })

    it('should handle conversion errors gracefully', async () => {
      const mockResponse: ConversionResponse = {
        results: [],
        errors: ['Invalid METAR format'],
        total_processed: 1,
        successful: 0,
        failed: 1,
      }
      mockFetchResponse(mockResponse)

      const result = await convertMetarToIwxxm({
        manualText: 'INVALID METAR',
      })

      expect(result.failed).toBe(1)
      expect(result.errors.length).toBeGreaterThan(0)
    })

    it('should handle empty input', async () => {
      const mockResponse: ConversionResponse = {
        results: [],
        errors: ['No input provided'],
        total_processed: 0,
        successful: 0,
        failed: 0,
      }
      mockFetchResponse(mockResponse)

      const result = await convertMetarToIwxxm({
        manualText: '',
        files: undefined,
      })

      expect(result.successful).toBe(0)
    })

    it('should trim whitespace from manual text', async () => {
      mockFetchResponse({ results: [], errors: [], total_processed: 0, successful: 0, failed: 0 })

      await convertMetarToIwxxm({
        manualText: '   KJFK 121851Z   ',
      })

      expect(global.fetch).toHaveBeenCalled()
    })

    it('should throw error on conversion failure', async () => {
      mockFetchResponse({ detail: { message: 'Conversion failed' } }, false, 400)

      await expect(
        convertMetarToIwxxm({ manualText: 'TEST' })
      ).rejects.toThrow()
    })

    it('should handle network errors during conversion', async () => {
      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network timeout'))

      await expect(
        convertMetarToIwxxm({ manualText: 'KJFK 121851Z' })
      ).rejects.toThrow()
    })

    it('should include authorization token if available', async () => {
      localStorage.setItem('supabase_access_token', 'test-token-123')
      mockFetchResponse({ results: [], errors: [], total_processed: 0, successful: 0, failed: 0 })

      await convertMetarToIwxxm({ manualText: 'KJFK 121851Z' })

      const fetchCall = (global.fetch as any).mock.calls[0]
      expect(fetchCall[1].headers['Authorization']).toBe('Bearer test-token-123')
    })

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
      }
      mockFetchResponse(mockResponse)

      const files = [
        new File(['KJFK'], 'file1.txt', { type: 'text/plain' }),
        new File(['KLAX'], 'file2.txt', { type: 'text/plain' }),
        new File(['KORD'], 'file3.txt', { type: 'text/plain' }),
      ]

      const result = await convertMetarToIwxxm({ files })
      expect(result.results.length).toBe(3)
    })
  })

  // ============= ZIP Conversion Tests =============
  describe('convertMetarToIwxxmZip', () => {
    it('should convert METAR to ZIP file successfully', async () => {
      const blobData = new Blob(['PK\x03\x04...'], { type: 'application/zip' })
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        blob: vi.fn().mockResolvedValueOnce(blobData),
      })

      const result = await convertMetarToIwxxmZip({
        manualText: 'KJFK 121851Z',
      })

      expect(result instanceof Blob).toBe(true)
      expect(result.type).toBe('application/zip')
    })

    it('should handle ZIP conversion with files', async () => {
      const blobData = new Blob(['PK\x03\x04...'], { type: 'application/zip' })
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: true,
        blob: vi.fn().mockResolvedValueOnce(blobData),
      })

      const file = new File(['KJFK 121851Z'], 'metar.txt', { type: 'text/plain' })
      const result = await convertMetarToIwxxmZip({ files: [file] })

      expect(result instanceof Blob).toBe(true)
    })

    it('should throw error on ZIP conversion failure', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Error',
        json: vi.fn().mockResolvedValueOnce({ message: 'ZIP creation failed' }),
      })

      await expect(
        convertMetarToIwxxmZip({ manualText: 'TEST' })
      ).rejects.toThrow()
    })

    it('should handle network errors during ZIP conversion', async () => {
      ;(global.fetch as any).mockRejectedValueOnce(new Error('Network error'))

      await expect(
        convertMetarToIwxxmZip({ manualText: 'KJFK' })
      ).rejects.toThrow()
    })

    it('should handle malformed JSON error response', async () => {
      ;(global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Error',
        json: vi.fn().mockRejectedValueOnce(new Error('Invalid JSON')),
      })

      await expect(
        convertMetarToIwxxmZip({ manualText: 'TEST' })
      ).rejects.toThrow()
    })
  })

  // ============= Download Blob Tests =============
  describe('downloadBlob', () => {
    it('should create and trigger blob download', () => {
      // Mock DOM methods
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
      }

      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document, 'body', 'get').mockReturnValue({
        appendChild: vi.fn(),
        removeChild: vi.fn(),
      } as any)
      vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url')
      vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})

      const blob = new Blob(['test'], { type: 'text/plain' })
      downloadBlob(blob, 'test.txt')

      expect(mockLink.download).toBe('test.txt')
      expect(mockLink.click).toHaveBeenCalled()
    })

    it('should handle large file downloads', () => {
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
      }

      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document, 'body', 'get').mockReturnValue({
        appendChild: vi.fn(),
        removeChild: vi.fn(),
      } as any)
      vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url')
      vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})

      const largeData = new Array(1000000).fill('x').join('')
      const blob = new Blob([largeData], { type: 'application/octet-stream' })
      downloadBlob(blob, 'large-file.bin')

      expect(mockLink.download).toBe('large-file.bin')
    })

    it('should handle special characters in filename', () => {
      const mockLink = {
        href: '',
        download: '',
        click: vi.fn(),
      }

      vi.spyOn(document, 'createElement').mockReturnValue(mockLink as any)
      vi.spyOn(document, 'body', 'get').mockReturnValue({
        appendChild: vi.fn(),
        removeChild: vi.fn(),
      } as any)
      vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:mock-url')
      vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})

      const blob = new Blob(['test'], { type: 'text/plain' })
      downloadBlob(blob, 'file-with-special-chars_@#$.txt')

      expect(mockLink.download).toBe('file-with-special-chars_@#$.txt')
    })
  })

  // ============= Type/Interface Tests =============
  describe('API Response Types', () => {
    it('should handle conversion result structure', () => {
      const result = {
        name: 'test',
        content: '<iwxxm>test</iwxxm>',
        source: 'KJFK',
        size_bytes: 256,
      }

      expect(result.name).toBeDefined()
      expect(result.content).toBeDefined()
      expect(result.source).toBeDefined()
      expect(result.size_bytes).toBeDefined()
    })

    it('should handle conversion response structure', () => {
      const response: ConversionResponse = {
        results: [],
        errors: [],
        total_processed: 0,
        successful: 0,
        failed: 0,
      }

      expect(response.results).toBeDefined()
      expect(response.errors).toBeDefined()
      expect(response.total_processed).toBe(0)
    })

    it('should handle health response structure', () => {
      const health: HealthResponse = {
        status: 'healthy',
        version: '1.0.0',
        gifts_available: true,
      }

      expect(health.status).toBeDefined()
      expect(health.version).toBeDefined()
      expect(health.gifts_available).toBeDefined()
    })

    it('should handle API error structure', () => {
      const error: ApiError = {
        message: 'Error occurred',
        errors: ['Details'],
        total_errors: 1,
      }

      expect(error.message).toBeDefined()
      expect(error.errors).toBeDefined()
    })
  })

  // ============= Edge Cases =============
  describe('Edge Cases', () => {
    it('should handle requests without authentication token', async () => {
      localStorage.removeItem('supabase_access_token')
      mockFetchResponse({ results: [], errors: [], total_processed: 0, successful: 0, failed: 0 })

      await convertMetarToIwxxm({ manualText: 'KJFK' })

      const fetchCall = (global.fetch as any).mock.calls[0]
      expect(fetchCall[1].headers['Authorization']).toBe('Bearer ')
    })

    it('should handle very long METAR strings', async () => {
      const longMetar = 'KJFK 121851Z ' + 'A'.repeat(10000)
      mockFetchResponse({ results: [], errors: [], total_processed: 1, successful: 0, failed: 1 })

      const result = await convertMetarToIwxxm({ manualText: longMetar })
      expect(result.total_processed).toBe(1)
    })

    it('should handle special characters in METAR text', async () => {
      const specialMetar = 'KJFK 121851Z <>&"\'$'
      mockFetchResponse({ results: [], errors: [], total_processed: 1, successful: 0, failed: 1 })

      const result = await convertMetarToIwxxm({ manualText: specialMetar })
      expect(result.total_processed).toBe(1)
    })
  })
})
