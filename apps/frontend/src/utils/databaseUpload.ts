import { edgeFunctionUrl } from './supabase/info';

export type DatabaseFormat = 'iwxxm' | 'json' | 'both';
export type UploadDestination = 'primary' | 'archive' | 'both';

export interface ConvertedFileUpload {
  id: string;
  originalName: string;
  originalContent: string;
  convertedContent: string;
  timestamp: number;
}

export interface DatabaseUploadOptions {
  format: DatabaseFormat;
  destination: UploadDestination;
  includeOriginal: boolean;
}

/** Defaults for one-click Convert&Send (evolve EV-001 / GitHub #656). */
export const CONVERT_AND_SEND_UPLOAD_OPTIONS: DatabaseUploadOptions = {
  format: 'iwxxm',
  destination: 'primary',
  includeOriginal: false,
};

export interface UploadConvertedFilesParams {
  files: ConvertedFileUpload[];
  /** @deprecated F21 public — ignored when present */
  accessToken?: string;
  options: DatabaseUploadOptions;
}

export const DATABASE_UPLOAD_SUBPATH = 'database/upload';

function parseUploadResponseBody(raw: string): Record<string, unknown> {
  if (!raw) {
    return {};
  }
  try {
    const data = JSON.parse(raw) as unknown;
    return typeof data === 'object' && data !== null
      ? (data as Record<string, unknown>)
      : {};
  } catch {
    return {};
  }
}

function uploadErrorMessage(
  raw: string,
  data: Record<string, unknown>,
  status: number,
): string {
  if (typeof data.error === 'string' && data.error) {
    return data.error;
  }
  if (typeof data.message === 'string' && data.message) {
    return data.message;
  }
  if (raw) {
    return raw;
  }
  return `Failed to upload to database (${status})`;
}

/**
 * Upload converted METAR/IWXXM files to the Supabase database edge function.
 *
 * @param params.files - Converted file payloads from the converter UI
 * @param params.options - Storage format, destination, and include-original flag
 * @returns Parsed JSON response from the upload endpoint
 * @throws Error when the request fails or the server returns a non-OK status
 */
export async function uploadConvertedFiles({
  files,
  options,
}: UploadConvertedFilesParams): Promise<{ message?: string }> {
  const response = await fetch(edgeFunctionUrl(DATABASE_UPLOAD_SUBPATH), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      files,
      options,
    }),
  });

  const raw = await response.text();
  const data = parseUploadResponseBody(raw);

  if (!response.ok) {
    throw new Error(uploadErrorMessage(raw, data, response.status));
  }

  return data as { message?: string };
}
