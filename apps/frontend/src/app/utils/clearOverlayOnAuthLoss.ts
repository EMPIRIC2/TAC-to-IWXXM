/**
 * Clear a signed overlay selection when the operator loses auth (guest / logout).
 *
 * @param prev - Current conversion params
 * @returns Params with ``overlayId`` cleared when it was set
 */
export function clearOverlayOnAuthLoss<T extends { overlayId: string }>(prev: T): T {
  return prev.overlayId ? { ...prev, overlayId: '' } : prev;
}
