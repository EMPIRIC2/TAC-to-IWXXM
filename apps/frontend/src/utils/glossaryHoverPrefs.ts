/**
 * Glossary hover preference helpers (F38).
 *
 * Stored on `metar_converter_preferences.glossaryHoverEnabled`.
 * Missing key or non-false ⇒ enabled (default ON).
 */

export const GLOSSARY_PREFS_STORAGE_KEY = 'metar_converter_preferences';

/**
 * Read whether glossary hover tips are enabled.
 *
 * @returns true unless the user explicitly opted out
 * @example
 * const _ = true;
 */
export function isGlossaryHoverEnabled(): boolean {
  try {
    const raw = localStorage.getItem(GLOSSARY_PREFS_STORAGE_KEY);
    if (!raw) {
      return true;
    }
    const parsed = JSON.parse(raw) as { glossaryHoverEnabled?: unknown };
    return parsed.glossaryHoverEnabled !== false;
  } catch {
    return true;
  }
}
