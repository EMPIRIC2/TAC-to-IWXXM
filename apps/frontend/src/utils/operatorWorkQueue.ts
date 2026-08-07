/**
 * Operator work-queue focus/selection helpers (F7 deepen / EV-042 / UJ-052).
 *
 * [Corpus: product §F7] [Corpus: journeys §UJ-052]
 */

/**
 * Clamp a queue focus index into ``[0, length)`` (or ``0`` when empty).
 *
 * @param index - Candidate focus index
 * @param length - Queue length
 * @returns Safe index
 */
export function clampQueueIndex(index: number, length: number): number {
  if (length <= 0) return 0;
  return Math.max(0, Math.min(index, length - 1));
}

/**
 * Move focus to the next queue item (stops at end).
 *
 * @param index - Current focus index
 * @param length - Queue length
 * @returns Next index
 */
export function nextQueueIndex(index: number, length: number): number {
  return clampQueueIndex(index + 1, length);
}

/**
 * Move focus to the previous queue item (stops at start).
 *
 * @param index - Current focus index
 * @param length - Queue length
 * @returns Previous index
 */
export function prevQueueIndex(index: number, length: number): number {
  return clampQueueIndex(index - 1, length);
}

/**
 * Toggle an id in a selection set (immutable).
 *
 * @param selected - Current selection
 * @param id - Item id to toggle
 * @returns New selection set
 */
export function toggleQueueSelection(
  selected: ReadonlySet<string>,
  id: string,
): Set<string> {
  const next = new Set(selected);
  if (next.has(id)) {
    next.delete(id);
  } else {
    next.add(id);
  }
  return next;
}
