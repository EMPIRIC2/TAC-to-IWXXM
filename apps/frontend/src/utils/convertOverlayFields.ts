/**
 * Optional signed-overlay fields for POST /api/v1/convert.
 * Bearer is included only when both overlay id and token are present.
 */

export function convertOverlayFields(
  overlayId: string,
  accessToken?: string,
): { overlayId?: string; accessToken?: string } {
  const id = overlayId.trim();
  if (!id) {
    return {};
  }
  const token = (accessToken ?? '').trim();
  if (!token) {
    return { overlayId: id };
  }
  return { overlayId: id, accessToken: token };
}
