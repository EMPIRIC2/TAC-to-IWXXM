/**
 * Export selection helpers for dissemination drawer multi-file select (F16 / EV-018 / #785).
 *
 * Candidates = current-session conversion outputs + dropped files only (E18-4).
 * Selection count cap ≤20 (E18-6). Sole candidate auto-selected (E18-9).
 */

/** Maximum number of files selectable for one Disseminate / Preflight-only run. */
export const MAX_EXPORT_SELECTION = 20;

/** Where a candidate originated (Finished IndexedDB history is never a source). */
export type ExportCandidateSource = 'session' | 'drop';

/** Raw input used to build a normalized {@link ExportCandidate}. */
export interface ExportCandidateInput {
  id: string;
  name: string;
  source: ExportCandidateSource;
  product?: string;
  sizeBytes?: number;
  status?: string;
  iwxxmXml?: string;
  tacText?: string;
}

/** Eligible export payload shown in the Export selection panel. */
export interface ExportCandidate {
  id: string;
  name: string;
  source: ExportCandidateSource;
  product?: string;
  sizeBytes?: number;
  status?: string;
  iwxxmXml?: string;
  tacText?: string;
}

/** Result of a selection mutation that may hit the ≤20 cap. */
export interface SelectionMutationResult {
  selected: string[];
  error?: string;
}

const CAP_ERROR = `Selection limited to ${MAX_EXPORT_SELECTION} files.`;

/**
 * Whether the candidate has a non-empty IWXXM or TAC body.
 *
 * @param input - Candidate input fields
 * @returns true when at least one payload body is non-empty after trim
 */
function hasPayload(input: ExportCandidateInput): boolean {
  return Boolean(input.iwxxmXml?.trim() || input.tacText?.trim());
}

/**
 * Normalize an input row into an {@link ExportCandidate}.
 *
 * @param input - Raw candidate fields
 * @returns Normalized candidate
 */
function toCandidate(input: ExportCandidateInput): ExportCandidate {
  return {
    id: input.id,
    name: input.name,
    source: input.source,
    product: input.product,
    sizeBytes: input.sizeBytes,
    status: input.status,
    iwxxmXml: input.iwxxmXml,
    tacText: input.tacText,
  };
}

/**
 * Build eligible export candidates from session outputs and drops only.
 *
 * Finished IndexedDB history (`finishedHistory`) is accepted only so callers can
 * pass it safely — it is never included (E18-4).
 *
 * @param sources.sessionOutputs - Current-session conversion results
 * @param sources.droppedFiles - Files dropped into the drawer
 * @param sources.finishedHistory - Ignored (must not appear as candidates)
 * @returns Eligible candidates with payload bodies
 */
export function buildExportCandidates(sources: {
  sessionOutputs?: readonly ExportCandidateInput[];
  droppedFiles?: readonly ExportCandidateInput[];
  finishedHistory?: readonly ExportCandidateInput[];
}): ExportCandidate[] {
  const session = sources.sessionOutputs ?? [];
  const drops = sources.droppedFiles ?? [];
  // finishedHistory intentionally unused — E18-4 out of scope for v1.
  void sources.finishedHistory;

  const out: ExportCandidate[] = [];
  for (const row of [...session, ...drops]) {
    if (row.source !== 'session' && row.source !== 'drop') continue;
    if (!hasPayload(row)) continue;
    out.push(toCandidate(row));
  }
  return out;
}

/**
 * Initial selection for a candidate list (E18-9).
 *
 * @param candidates - Eligible candidates
 * @returns Sole id when exactly one candidate; otherwise empty
 */
export function initialSelectedIds(candidates: readonly ExportCandidate[]): string[] {
  if (candidates.length === 1) {
    return [candidates[0]!.id];
  }
  return [];
}

/**
 * Toggle one id in the selection, enforcing the ≤20 cap.
 *
 * @param selected - Current selected ids
 * @param id - Candidate id to toggle
 * @param max - Cap (default {@link MAX_EXPORT_SELECTION})
 * @returns New selection and optional cap error
 */
export function toggleSelection(
  selected: readonly string[],
  id: string,
  max: number = MAX_EXPORT_SELECTION,
): SelectionMutationResult {
  const set = new Set(selected);
  if (set.has(id)) {
    set.delete(id);
    return { selected: [...set] };
  }
  if (set.size >= max) {
    return { selected: [...selected], error: CAP_ERROR };
  }
  set.add(id);
  return { selected: [...set] };
}

/**
 * Select all candidates up to the ≤20 cap.
 *
 * @param candidates - Eligible candidates
 * @param max - Cap (default {@link MAX_EXPORT_SELECTION})
 * @returns Selected ids (truncated) and error when truncated
 */
export function selectAll(
  candidates: readonly ExportCandidate[],
  max: number = MAX_EXPORT_SELECTION,
): SelectionMutationResult {
  const ids = candidates.map((c) => c.id);
  if (ids.length <= max) {
    return { selected: ids };
  }
  return {
    selected: ids.slice(0, max),
    error: CAP_ERROR,
  };
}

/**
 * Clear the current selection.
 *
 * @param _selected - Prior selection (ignored)
 * @returns Empty selection
 */
export function clearSelection(_selected?: readonly string[]): string[] {
  return [];
}

/**
 * Whether Disseminate / Preflight-only may run for the selection.
 *
 * @param selected - Selected candidate ids
 * @param max - Cap (default {@link MAX_EXPORT_SELECTION})
 * @returns true when 1..max ids are selected
 */
export function canActOnSelection(
  selected: readonly string[],
  max: number = MAX_EXPORT_SELECTION,
): boolean {
  const n = selected.length;
  return n > 0 && n <= max;
}
