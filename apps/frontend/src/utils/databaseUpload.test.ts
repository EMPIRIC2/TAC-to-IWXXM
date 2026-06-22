import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  CONVERT_AND_SEND_UPLOAD_OPTIONS,
  uploadConvertedFiles,
} from './databaseUpload';

vi.mock('/utils/supabase/info', () => ({
  projectId: 'test-project',
}));

const mockFetch = vi.fn();

describe('databaseUpload', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal('fetch', mockFetch);
  });

  it('exports fixed defaults for Convert&Send', () => {
    expect(CONVERT_AND_SEND_UPLOAD_OPTIONS).toEqual({
      format: 'iwxxm',
      destination: 'primary',
      includeOriginal: false,
    });
  });

  it('uploads converted files with bearer token', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Files uploaded successfully' }),
    });

    const files = [
      {
        id: '1',
        originalName: 'test.tac',
        originalContent: 'METAR',
        convertedContent: '<iwxxm/>',
        timestamp: 1,
      },
    ];

    const result = await uploadConvertedFiles({
      files,
      accessToken: 'test-token',
      options: CONVERT_AND_SEND_UPLOAD_OPTIONS,
    });

    expect(result.message).toBe('Files uploaded successfully');
    expect(mockFetch).toHaveBeenCalledWith(
      'https://test-project.supabase.co/functions/v1/make-server-2e3cda33/database/upload',
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify({
          files,
          options: CONVERT_AND_SEND_UPLOAD_OPTIONS,
        }),
      }),
    );
  });

  it('throws when upload response is not ok', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'Upload rejected' }),
    });

    await expect(
      uploadConvertedFiles({
        files: [],
        accessToken: 'test-token',
        options: CONVERT_AND_SEND_UPLOAD_OPTIONS,
      }),
    ).rejects.toThrow('Upload rejected');
  });
});
