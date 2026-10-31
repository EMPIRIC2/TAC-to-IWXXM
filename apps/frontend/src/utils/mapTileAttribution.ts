/**
 * Shared OpenStreetMap tile URL and Leaflet corner attribution.
 *
 * Provider: OpenStreetMap tile server (`tile.openstreetmap.org`).
 * Data license: Open Database License (ODbL) — see
 * https://www.openstreetmap.org/copyright
 */

/** Raster tile template used by live map and station minimap. */
export const OSM_TILE_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';

/**
 * Leaflet attribution HTML for the map corner control.
 *
 * OSM requires credit to OpenStreetMap contributors and a clear ODbL notice;
 * linking the copyright page satisfies the license pointer.
 */
export const OSM_TILE_ATTRIBUTION =
  '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors · Open Database License (ODbL)';
