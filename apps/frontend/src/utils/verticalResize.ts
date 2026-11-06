/**
 * Clamp a dragged panel height for Convert TAC / IWXXM panes.
 *
 * [Corpus: product §F7]
 */

/** Minimum panel height in pixels. */
export const VERTICAL_RESIZE_MIN_PX = 160;

/** Maximum panel height in pixels. */
export const VERTICAL_RESIZE_MAX_PX = 720;

/**
 * Apply a pointer delta to a starting height and clamp.
 *
 * @param startHeight - Height when the drag began
 * @param deltaY - Pointer movement in pixels (positive grows downward)
 * @returns Clamped height
 * @example
 * const _ = true;
 */
export function clampVerticalResizeHeight(startHeight: number, deltaY: number): number {
  const next = startHeight + deltaY;
  return Math.min(VERTICAL_RESIZE_MAX_PX, Math.max(VERTICAL_RESIZE_MIN_PX, next));
}
