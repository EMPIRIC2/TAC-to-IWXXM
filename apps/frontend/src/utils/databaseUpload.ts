import { projectId } from '/utils/supabase/info';

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
  accessToken: string;
  options: DatabaseUploadOptions;
}

/**
 * Upload converted METAR/IWXXM files to the Supabase database edge function.
 *
 * @param params.files - Converted file payloads from the converter UI
 * @param params.accessToken - Supabase JWT for authorization
 * @param params.options - Storage format, destination, and include-original flag
 * @returns Parsed JSON response from the upload endpoint
 * @throws Error when the request fails or the server returns a non-OK status
 */
export async function uploadConvertedFiles({
  files,
  accessToken,
  options,
}: UploadConvertedFilesParams): Promise<{ message?: string }> {
  const response = await fetch(
    `https://${projectId}.supabase.co/functions/v1/make-server-2e3cda33/database/upload`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        files,
        options,
      }),
    },
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Failed to upload to database');
  }

  return data;
}
