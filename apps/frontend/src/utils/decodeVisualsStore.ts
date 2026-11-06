/**
 * Last station and decode rows shared by Convert and Decode visuals.
 */

/**
 * Type `DecodeVisualsSnapshot`.
 * @example
 * const _ = true;
 */
export type DecodeVisualsSnapshot = {
  station: string;
  segments: { code: string; explanation: string }[];
};

const EMPTY: DecodeVisualsSnapshot = { station: '', segments: [] };
let snapshot: DecodeVisualsSnapshot = EMPTY;
const listeners = new Set<() => void>();

/** Station typed on Decode visuals. Survives leaving the tab. */
let stationDraft: string | null = null;
const draftListeners = new Set<() => void>();

/**
 * Current decode visuals snapshot.
 *
 * @returns Station and decode rows
 * @example
 * const _ = true;
 */
export function readDecodeVisuals(): DecodeVisualsSnapshot {
  return snapshot;
}

/**
 * Replace the snapshot and notify subscribers.
 *
 * @param next - Station and decode rows
 * @example
 * const _ = true;
 */
export function publishDecodeVisuals(next: DecodeVisualsSnapshot): void {
  snapshot = next;
  listeners.forEach((listener) => listener());
}

/**
 * Subscribe to snapshot changes.
 *
 * @param listener - Called after each publish
 * @returns Unsubscribe
 * @example
 * const _ = true;
 */
export function subscribeDecodeVisuals(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

/**
 * Station typed on Decode visuals, or null when the published station is showing.
 *
 * @returns Draft station text
 * @example
 * const _ = true;
 */
export function readStationDraft(): string | null {
  return stationDraft;
}

/**
 * Remember a station typed on Decode visuals.
 *
 * @param next - Draft text, or null to follow the published station
 * @example
 * const _ = true;
 */
export function writeStationDraft(next: string | null): void {
  stationDraft = next;
  draftListeners.forEach((listener) => listener());
}

/**
 * Subscribe to the typed station.
 *
 * @param listener - Called after each draft change
 * @returns Unsubscribe
 * @example
 * const _ = true;
 */
export function subscribeStationDraft(listener: () => void): () => void {
  draftListeners.add(listener);
  return () => {
    draftListeners.delete(listener);
  };
}
