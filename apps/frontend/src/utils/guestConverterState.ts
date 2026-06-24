/**
 * Ephemeral guest converter state — persisted until login (F5-R33).
 */

import type { ConverterSnapshot } from './workSessionPayload';

const STORAGE_KEY = 'metar_guest_converter_state';

export function saveGuestConverterState(snapshot: ConverterSnapshot): void {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
  } catch {
    // sessionStorage may be unavailable in private mode
  }
}

export function readGuestConverterState(): ConverterSnapshot | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return null;
    }
    return JSON.parse(raw) as ConverterSnapshot;
  } catch {
    return null;
  }
}

export function clearGuestConverterState(): void {
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}
