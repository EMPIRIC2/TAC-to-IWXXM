/**
 * Build F5 work-session API payloads from converter UI state.
 */

import type { WorkSessionStatus, WorkSessionUpsertPayload } from '@metar/shared';

export interface ConvertedFileSnapshot {
  originalName: string;
  originalContent: string;
  convertedContent: string;
  /** 1-based index when manual input had multiple lines (#655 / EV-007). */
  manualLineIndex?: number;
  /** Total manual lines in the batch. */
  manualLineTotal?: number;
}

export interface ConverterSnapshot {
  manualInput: string;
  pendingFiles: { name: string; content: string }[];
  convertedFiles: ConvertedFileSnapshot[];
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
      ...(file.manualLineIndex != null && file.manualLineTotal != null
        ? {
            manual_line_index: file.manualLineIndex,
            manual_line_total: file.manualLineTotal,
          }
        : {}),
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

/**
 * Restore multi-line manual chip metadata from a persisted converted result.
 *
 * Prefers explicit ``manual_line_index`` / ``manual_line_total`` fields; falls
 * back to inferring from ``manual_input_N.txt`` style download names.
 */
export function resolveManualLineMetaFromResult(
  name: string,
  result: Record<string, unknown>,
  allNames: string[],
): { manualLineIndex?: number; manualLineTotal?: number } {
  const storedIndex = result.manual_line_index;
  const storedTotal = result.manual_line_total;
  if (typeof storedIndex === 'number' && typeof storedTotal === 'number') {
    return { manualLineIndex: storedIndex, manualLineTotal: storedTotal };
  }

  const match = name.match(/^(.+)_(\d+)\.txt$/i);
  if (!match) {
    return {};
  }
  const prefix = match[1];
  const indexedPeers = allNames
    .map((peer) => peer.match(/^(.+)_(\d+)\.txt$/i))
    .filter(
      (peerMatch): peerMatch is RegExpMatchArray =>
        !!peerMatch && peerMatch[1] === prefix,
    )
    .map((peerMatch) => Number.parseInt(peerMatch[2], 10))
    .sort((a, b) => a - b);
  if (indexedPeers.length <= 1) {
    return {};
  }
  return {
    manualLineIndex: Number.parseInt(match[2], 10),
    manualLineTotal: indexedPeers.length,
  };
}
