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

  it('inflates gzip bytes when DecompressionStream is available', async () => {
    const plaintext = new TextEncoder().encode('METAR KJFK=');

    vi.stubGlobal(
      'DecompressionStream',
      class {
        readable: ReadableStream<Uint8Array>;
        writable: WritableStream<Uint8Array>;
        constructor(format: string) {
          expect(format).toBe('gzip');
          let outCtrl: ReadableStreamDefaultController<Uint8Array> | undefined;
          this.readable = new ReadableStream<Uint8Array>({
            start(controller) {
              outCtrl = controller;
            },
          });
          this.writable = new WritableStream<Uint8Array>({
            write() {
              /* consume compressed bytes */
            },
            close() {
              outCtrl?.enqueue(plaintext);
              outCtrl?.close();
            },
          });
        }
      },
    );

    const compressed = new Uint8Array([0x1f, 0x8b, 0x08, 0x00]);
    const blob = {
      stream() {
        return new ReadableStream<Uint8Array>({
          start(controller) {
            controller.enqueue(compressed);
            controller.close();
          },
        });
      },
    } as Blob;

    await expect(inflateGzipToText(blob)).resolves.toBe('METAR KJFK=');
  });
});
