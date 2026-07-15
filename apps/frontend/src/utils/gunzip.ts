/**
 * Gunzip helpers for operator uploads (.gz TAC / bulletin / COLLECT).
 */

/**
 * Inflate a gzip ``Blob``/``File`` to UTF-8 text.
 *
 * Uses the browser ``DecompressionStream`` when available.
 *
 * @param blob - Gzip-compressed bytes
 * @returns Decoded text
 * @throws When gzip inflate is unavailable or fails
 */
export async function inflateGzipToText(blob: Blob): Promise<string> {
  if (typeof DecompressionStream === 'undefined') {
    throw new Error(
      'Gzip decompress is not supported in this browser. Upload uncompressed .txt/.tac/.xml, or use an API that accepts .gz.',
    );
  }
  const stream = blob.stream().pipeThrough(new DecompressionStream('gzip'));
  const inflated = await new Response(stream).arrayBuffer();
  return new TextDecoder('utf-8', { fatal: false }).decode(inflated);
}

/**
 * True when the file name looks gzip-compressed.
 *
 * @param fileName - Original file name
 */
export function isGzipFileName(fileName: string): boolean {
  const lower = fileName.toLowerCase();
  return lower.endsWith('.gz') || lower.endsWith('.gzip');
}
