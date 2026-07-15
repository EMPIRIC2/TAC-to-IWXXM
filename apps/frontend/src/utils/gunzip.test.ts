import { describe, expect, it, vi, afterEach } from 'vitest';
import { inflateGzipToText, isGzipFileName } from './gunzip';

describe('gunzip', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('detects gzip file names', () => {
    expect(isGzipFileName('a.tac.gz')).toBe(true);
    expect(isGzipFileName('a.GZIP')).toBe(true);
    expect(isGzipFileName('a.tac')).toBe(false);
  });

  it('throws when DecompressionStream is unavailable', async () => {
    vi.stubGlobal('DecompressionStream', undefined);
    await expect(inflateGzipToText(new Blob([new Uint8Array([1, 2])]))).rejects.toThrow(
      /not supported/i,
    );
  });
});
