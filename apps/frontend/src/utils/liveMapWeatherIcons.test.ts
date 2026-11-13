/**
 * Inline SVG helpers for TAC weather overlays.
 */

import { describe, expect, it } from 'vitest';
import {
  ICE_SVG,
  PRECIP_SVG,
  THUNDER_SVG,
  temperatureIconHtml,
  weatherIconHtml,
  windVectorIconHtml,
} from '@/utils/liveMapWeatherIcons';

describe('liveMapWeatherIcons', () => {
  it('wraps weather SVG glyphs for DivIcon html', () => {
    expect(THUNDER_SVG).toContain('<svg');
    expect(ICE_SVG).toContain('<svg');
    expect(PRECIP_SVG).toContain('<svg');
    expect(weatherIconHtml(THUNDER_SVG)).toContain(THUNDER_SVG);
    expect(weatherIconHtml(ICE_SVG)).toContain('inline-flex');
  });

  it('renders a rotated wind arrow and a temperature badge', () => {
    expect(windVectorIconHtml(180)).toContain('rotate(180deg)');
    expect(temperatureIconHtml(-5)).toContain('-5°');
    expect(temperatureIconHtml(12)).toContain('12°');
  });
});
