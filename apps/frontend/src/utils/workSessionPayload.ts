/**
 * Build F5 work-session API payloads from converter UI state.
 */

import type { WorkSessionStatus, WorkSessionUpsertPayload } from '@metar/shared';

export interface ConverterSnapshot {
  manualInput: string;
  pendingFiles: { name: string; content: string }[];
  convertedFiles: {
    originalName: string;
    originalContent: string;
    convertedContent: string;
  }[];
  conversionLog: { errors: string[]; issues: Record<string, unknown>[] } | null;
  conversionParams: Record<string, unknown>;
}

const ICAO_RE = /\b(?:METAR|SPECI)\s+(?:COR\s+)?([A-Z]{4})\b/;

export function extractSessionTitle(manualInput: string): string {
  const match = manualInput.match(ICAO_RE);
  const icao = match?.[1] ?? 'METAR';
  const stamp = new Date().toISOString().slice(0, 16).replace('T', ' ');
  return `${icao} · ${stamp}`;
}

export function hasConverterContent(snapshot: ConverterSnapshot): boolean {
  return (
    !!snapshot.manualInput.trim() ||
    snapshot.pendingFiles.length > 0 ||
    snapshot.convertedFiles.length > 0
  );
}

export function buildWorkSessionPayload(
  snapshot: ConverterSnapshot,
  options?: { status?: WorkSessionStatus; kvUploadKey?: string },
): WorkSessionUpsertPayload {
  const payload: WorkSessionUpsertPayload = {
    title: extractSessionTitle(snapshot.manualInput),
    manual_tac: snapshot.manualInput,
    pending_files: snapshot.pendingFiles.map((file) => ({
      name: file.name,
      content: file.content,
    })),
    converted_results: snapshot.convertedFiles.map((file) => ({
      name: file.originalName,
      tac_input: file.originalContent,
      iwxxm_xml: file.convertedContent,
    })),
    errors: snapshot.conversionLog?.errors ?? [],
    issues: snapshot.conversionLog?.issues ?? [],
    conversion_params: snapshot.conversionParams,
  };
  if (options?.status) {
    payload.status = options.status;
  }
  if (options?.kvUploadKey) {
    payload.kv_upload_key = options.kvUploadKey;
  }
  return payload;
}
