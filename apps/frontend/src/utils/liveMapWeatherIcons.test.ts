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

  it('renders a rotated wind arrow sized by magnitude and temperature badges in C/F', () => {
    expect(windVectorIconHtml(180)).toContain('rotate(180deg)');
    expect(windVectorIconHtml(90, 36)).toContain('width:36px');
    expect(temperatureIconHtml(-5, 'C')).toContain('-5°C');
    expect(temperatureIconHtml(0, 'F')).toContain('32°F');
  });
});
