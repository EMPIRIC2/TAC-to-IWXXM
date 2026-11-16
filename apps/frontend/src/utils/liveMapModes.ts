/**
 * Live map display modes: Annex 3 products, TAC overlays, or temperatures.
 * Modes are mutually exclusive; time-frame is shared. [Corpus: product §F37]
 */

/**
 * Mutually exclusive Live map chrome modes.
 * @example
 * const _ = true;
 */
export type LiveMapDisplayMode = 'annex3' | 'overlays' | 'temperatures';

/**
 * Operator temperature unit for the Temperatures mode.
 * @example
 * const _ = true;
 */
export type LiveMapTempUnit = 'C' | 'F';

export const LIVE_MAP_MODE_ANNEX3 = 'Annex 3 products';
export const LIVE_MAP_MODE_OVERLAYS = 'Overlays';
export const LIVE_MAP_MODE_TEMPERATURES = 'Temperatures';
export const LIVE_MAP_MODE_GROUP = 'Map mode';
export const LIVE_MAP_OVERLAY_SCALE = 'Vector size';
export const LIVE_MAP_TEMP_UNIT = 'Temperature unit';
export const LIVE_MAP_TEMP_C = '°C';
export const LIVE_MAP_TEMP_F = '°F';
export const LIVE_MAP_SHOW_LATEST = 'Show latest';

export const LIVE_MAP_DISPLAY_MODES = [
  { id: 'annex3' as const, label: LIVE_MAP_MODE_ANNEX3 },
  { id: 'overlays' as const, label: LIVE_MAP_MODE_OVERLAYS },
  { id: 'temperatures' as const, label: LIVE_MAP_MODE_TEMPERATURES },
] as const;

/** Default magnitude scale for overlay wind vectors (1 = natural size). */
export const DEFAULT_OVERLAY_MAGNITUDE_SCALE = 1;

/** Inclusive clamp for the overlay vector-size slider. */
export const OVERLAY_MAGNITUDE_SCALE_MIN = 0.5;
export const OVERLAY_MAGNITUDE_SCALE_MAX = 2;

/**
 * Whether the mode id is a known Live map display mode.
 *
 * @param value - Candidate mode
 * @returns True when value is annex3, overlays, or temperatures
 * @example
 * const _ = true;
 */
export function isLiveMapDisplayMode(value: string): value is LiveMapDisplayMode {
  return value === 'annex3' || value === 'overlays' || value === 'temperatures';
}

/**
 * Select a Live map mode. Replacing the active mode clears the others
 * (mutual exclusivity).
 *
 * @param _current - Previously active mode (unused; exclusivity is total)
 * @param next - Mode to activate
 * @returns The single active mode
 * @example
 * const _ = true;
 */
export function selectLiveMapMode(
  _current: LiveMapDisplayMode,
  next: LiveMapDisplayMode,
): LiveMapDisplayMode {
  if (!isLiveMapDisplayMode(next)) {
    throw new Error('Unknown Live map mode');
  }
  return next;
}

/**
 * Reject unknown temperature units.
 *
 * @param value - Candidate unit
 * @returns True when C or F
 * @example
 * const _ = true;
 */
export function isLiveMapTempUnit(value: string): value is LiveMapTempUnit {
  return value === 'C' || value === 'F';
}

/**
 * Toggle or set the temperature display unit.
 *
 * @param current - Current unit
 * @param next - Requested unit
 * @returns Next unit
 * @example
 * const _ = true;
 */
export function selectTempUnit(
  current: LiveMapTempUnit,
  next: string,
): LiveMapTempUnit {
  if (!isLiveMapTempUnit(next)) {
    throw new Error('Temperature unit must be C or F');
  }
  return next === current ? next : next;
}

/**
 * Convert Celsius to the operator unit.
 *
 * @param celsius - Degrees Celsius
 * @param unit - Display unit
 * @returns Numeric display value (rounded to nearest integer for F)
 * @example
 * const _ = true;
 */
export function temperatureInUnit(celsius: number, unit: LiveMapTempUnit): number {
  if (unit === 'C') {
    return celsius;
  }
  return Math.round((celsius * 9) / 5 + 32);
}

/**
 * Format a temperature for map badges.
 *
 * @param celsius - Degrees Celsius from TAC
 * @param unit - Display unit
 * @returns Operator-visible label such as ``12°C``
 * @example
 * const _ = true;
 */
export function formatTemperatureLabel(celsius: number, unit: LiveMapTempUnit): string {
  const value = temperatureInUnit(celsius, unit);
  return `${value}${unit === 'C' ? '°C' : '°F'}`;
}

/**
 * Clamp overlay magnitude scale for the vector-size slider.
 *
 * @param raw - Slider value
 * @returns Clamped scale in [0.5, 2]
 * @example
 * const _ = true;
 */
export function clampOverlayMagnitudeScale(raw: number): number {
  if (!Number.isFinite(raw)) {
    throw new Error('Overlay magnitude scale must be a finite number');
  }
  if (raw < OVERLAY_MAGNITUDE_SCALE_MIN) {
    return OVERLAY_MAGNITUDE_SCALE_MIN;
  }
  if (raw > OVERLAY_MAGNITUDE_SCALE_MAX) {
    return OVERLAY_MAGNITUDE_SCALE_MAX;
  }
  return raw;
}

/**
 * Pixel size for a wind vector icon: direction is separate; size tracks speed.
 *
 * @param speedKt - Wind speed in knots
 * @param scale - Slider magnitude scale
 * @returns Icon box size in pixels (even integer, 16–40)
 * @example
 * const _ = true;
 */
export function windVectorSizePx(speedKt: number, scale: number): number {
  const safeSpeed = Number.isFinite(speedKt) && speedKt > 0 ? speedKt : 0;
  const clamped = clampOverlayMagnitudeScale(scale);
  const base = 16 + Math.min(safeSpeed, 40) * 0.4;
  const sized = Math.round(base * clamped);
  const even = sized % 2 === 0 ? sized : sized + 1;
  return Math.min(40, Math.max(16, even));
}

/**
 * Whether Annex 3 product layer checkboxes should render.
 *
 * @param mode - Active mode
 * @returns True only in annex3 mode
 * @example
 * const _ = true;
 */
export function showsAnnex3Products(mode: LiveMapDisplayMode): boolean {
  return mode === 'annex3';
}

/**
 * Whether TAC overlay toggles and magnitude slider should render.
 *
 * @param mode - Active mode
 * @returns True only in overlays mode
 * @example
 * const _ = true;
 */
export function showsOverlayControls(mode: LiveMapDisplayMode): boolean {
  return mode === 'overlays';
}

/**
 * Whether temperature unit toggle should render.
 *
 * @param mode - Active mode
 * @returns True only in temperatures mode
 * @example
 * const _ = true;
 */
export function showsTemperatureControls(mode: LiveMapDisplayMode): boolean {
  return mode === 'temperatures';
}
