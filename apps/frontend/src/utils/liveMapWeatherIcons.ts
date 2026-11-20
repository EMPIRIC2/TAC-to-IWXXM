/**
 * Inline SVG markers for TAC weather overlays. [Corpus: ui-style]
 */

/** Thunderbolt glyph (24×24). */
export const THUNDER_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path fill="#b45309" d="M13 2 4 14h6l-1 8 9-12h-6l1-8z"/></svg>`;

/** Ice crystal glyph (24×24). */
export const ICE_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path fill="#0284c7" stroke="#0c4a6e" stroke-width="1" d="M12 2v20M4.5 6.5l15 11M4.5 17.5l15-11M12 7l3 2.5L12 12 9 9.5 12 7zm0 5 3 2.5L12 17 9 14.5 12 12z"/></svg>`;

/** Rain / precip drop (24×24). */
export const PRECIP_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path fill="#1d4ed8" d="M12 3c-3 4.5-6 8-6 11a6 6 0 0 0 12 0c0-3-3-6.5-6-11z"/></svg>`;

/**
 * Wind direction arrow HTML: rotation = direction; box size = magnitude.
 *
 * @param degrees - Meteorological from-direction
 * @param sizePx - Icon box size in pixels (magnitude)
 * @returns HTML snippet for a DivIcon
 * @example
 * const _ = true;
 */
export function windVectorIconHtml(degrees: number, sizePx = 28): string {
  const rot = degrees;
  const box = Math.max(16, Math.round(sizePx));
  const glyph = Math.max(12, Math.round(box * 0.78));
  return `<span style="display:inline-flex;width:${box}px;height:${box}px;align-items:center;justify-content:center;transform:rotate(${rot}deg)"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="${glyph}" height="${glyph}" aria-hidden="true"><path fill="#0f766e" d="M12 3l5 9h-3v9h-4V12H7l5-9z"/></svg></span>`;
}

/**
 * Temperature badge HTML.
 *
 * @param celsius - Degrees C from TAC
 * @param unit - Operator display unit (C or F)
 * @returns HTML snippet for a DivIcon
 * @example
 * const _ = true;
 */
export function temperatureIconHtml(celsius: number, unit: 'C' | 'F' = 'C'): string {
  const value = unit === 'C' ? celsius : Math.round((celsius * 9) / 5 + 32);
  const label = `${value}${unit === 'C' ? '°C' : '°F'}`;
  return `<span style="display:inline-flex;align-items:center;justify-content:center;min-width:28px;height:18px;padding:0 4px;border-radius:4px;background:#fff7ed;border:1px solid #c2410c;color:#9a3412;font:600 10px/16px ui-sans-serif,system-ui,sans-serif">${label}</span>`;
}

/**
 * Wrap an SVG string as a Leaflet DivIcon html payload.
 *
 * @param svg - Inline SVG markup
 * @returns HTML
 * @example
 * const _ = true;
 */
export function weatherIconHtml(svg: string): string {
  return `<span style="display:inline-flex;width:24px;height:24px;filter:drop-shadow(0 1px 1px rgba(0,0,0,.35))">${svg}</span>`;
}
