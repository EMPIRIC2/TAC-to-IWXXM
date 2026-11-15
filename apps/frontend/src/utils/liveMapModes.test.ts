/**
 * Live map mode exclusivity, temp units, and overlay scale matrix.
 */

import { describe, expect, it } from 'vitest';
import {
  DEFAULT_OVERLAY_MAGNITUDE_SCALE,
  LIVE_MAP_DISPLAY_MODES,
  clampOverlayMagnitudeScale,
  formatTemperatureLabel,
  isLiveMapDisplayMode,
  isLiveMapTempUnit,
  selectLiveMapMode,
  selectTempUnit,
  showsAnnex3Products,
  showsOverlayControls,
  showsTemperatureControls,
  temperatureInUnit,
  windVectorSizePx,
  type LiveMapDisplayMode,
} from '@/utils/liveMapModes';

describe('liveMapModes matrix', () => {
  it('lists exactly three mutually exclusive modes (read success)', () => {
    expect(LIVE_MAP_DISPLAY_MODES.map((row) => row.id)).toEqual([
      'annex3',
      'overlays',
      'temperatures',
    ]);
    expect(isLiveMapDisplayMode('annex3')).toBe(true);
    expect(isLiveMapDisplayMode('bogus')).toBe(false);
  });

  it.each([
    ['annex3', 'overlays'],
    ['overlays', 'temperatures'],
    ['temperatures', 'annex3'],
  ] as const)(
    'mutation: switching from %s to %s leaves a single active mode',
    (from, to) => {
      const next = selectLiveMapMode(from, to);
      expect(next).toBe(to);
      expect(showsAnnex3Products(next)).toBe(next === 'annex3');
      expect(showsOverlayControls(next)).toBe(next === 'overlays');
      expect(showsTemperatureControls(next)).toBe(next === 'temperatures');
      const activeCount = [
        showsAnnex3Products(next),
        showsOverlayControls(next),
        showsTemperatureControls(next),
      ].filter(Boolean).length;
      expect(activeCount).toBe(1);
    },
  );

  it('failure: reject unknown mode selection', () => {
    expect(() => selectLiveMapMode('annex3', 'wind' as LiveMapDisplayMode)).toThrow(
      /Unknown Live map mode/,
    );
  });

  it('validation success: accept C and F units', () => {
    expect(isLiveMapTempUnit('C')).toBe(true);
    expect(isLiveMapTempUnit('F')).toBe(true);
    expect(selectTempUnit('C', 'F')).toBe('F');
    expect(selectTempUnit('F', 'C')).toBe('C');
  });

  it('validation failure: reject invalid temperature unit', () => {
    expect(isLiveMapTempUnit('K')).toBe(false);
    expect(() => selectTempUnit('C', 'K')).toThrow(/C or F/);
  });

  it('success: convert and label temperatures in C and F', () => {
    expect(temperatureInUnit(0, 'C')).toBe(0);
    expect(temperatureInUnit(0, 'F')).toBe(32);
    expect(temperatureInUnit(20, 'F')).toBe(68);
    expect(formatTemperatureLabel(-5, 'C')).toBe('-5°C');
    expect(formatTemperatureLabel(-5, 'F')).toBe('23°F');
  });

  it('validation success: clamp overlay magnitude within range', () => {
    expect(clampOverlayMagnitudeScale(DEFAULT_OVERLAY_MAGNITUDE_SCALE)).toBe(1);
    expect(clampOverlayMagnitudeScale(0.25)).toBe(0.5);
    expect(clampOverlayMagnitudeScale(9)).toBe(2);
  });

  it('validation failure: reject non-finite overlay magnitude', () => {
    expect(() => clampOverlayMagnitudeScale(Number.NaN)).toThrow(/finite/);
    expect(() => clampOverlayMagnitudeScale(Number.POSITIVE_INFINITY)).toThrow(
      /finite/,
    );
  });

  it('success: vector size grows with speed and scale (direction separate)', () => {
    const calm = windVectorSizePx(2, 1);
    const gale = windVectorSizePx(40, 1);
    const galeScaled = windVectorSizePx(40, 2);
    expect(gale).toBeGreaterThan(calm);
    expect(galeScaled).toBeGreaterThan(gale);
    expect(windVectorSizePx(10, 1) % 2).toBe(0);
  });

  it('mutation delete-equivalent: leaving overlays mode hides overlay chrome', () => {
    expect(showsOverlayControls(selectLiveMapMode('overlays', 'annex3'))).toBe(false);
    expect(
      showsTemperatureControls(selectLiveMapMode('temperatures', 'overlays')),
    ).toBe(false);
  });
});
