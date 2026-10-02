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
