/**
 * World map of cached TAC reports.
 */

import { useEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { createRoot, type Root } from 'react-dom/client';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { drawForPlace } from '@metar/live-map-geometry';
import {
  DECODE_VISUALS_BETA,
  DECODE_VISUALS_FEEDBACK,
  DECODE_VISUALS_FEEDBACK_URL,
} from '@/utils/decodeVisualsCopy';
import { airports } from '@/utils/airportsData';
import {
  boundsOf,
  cardLayout,
  copyOpacity,
  fetchLivePlaces,
  filterPlaces,
  formatObservedAt,
  LIVE_MAP_ALL_COUNTRIES,
  LIVE_MAP_ALL_REGIONS,
  LIVE_MAP_ALL_TIMES,
  LIVE_MAP_CANVAS,
  LIVE_MAP_EARLIER,
  LIVE_MAP_ERROR,
  LIVE_MAP_FILTER_COUNTRY,
  LIVE_MAP_FILTER_PHENOMENON,
  LIVE_MAP_FILTER_REGION,
  LIVE_MAP_FILTER_TIME,
  LIVE_MAP_LAST_24_HOURS,
  LIVE_MAP_LAST_6_HOURS,
  LIVE_MAP_LAST_HOUR,
  LIVE_MAP_LAYERS_OFF,
  LIVE_MAP_NEWER,
  LIVE_MAP_NOTICE,
  LIVE_MAP_PHENOMENA,
  LIVE_MAP_REFRESH_MS,
  LIVE_MAP_SPACE,
  LIVE_MAP_TAC,
  LIVE_MAP_VIEWS,
  LIVE_MAP_ZOOM_HINT,
  pinColor,
  placeShowingReport,
  placeTitle,
  pointNudge,
  popupWidth,
  productLabel,
  selectedLayerQuery,
  shapePaint,
  spaceWeatherListColor,
  viewStatus,
  type LivePlace,
  type MapBounds,
  type MapTimePreset,
} from '@/utils/liveMap';
import { placeRegion, regionFilterNames } from '@/utils/liveMapRegions';

const EMPTY_PLACES: LivePlace[] = [];

/**
 * True when two fetches describe the same drawn reports.
 *
 * @param current - Places already on the map
 * @param next - Places just fetched
 * @returns Whether a redraw can be skipped
 * @example
 * const _ = true;
 */
function placesMatch(current: LivePlace[], next: LivePlace[]): boolean {
  return JSON.stringify(current) === JSON.stringify(next);
}

/**
 * Open a marker from the keyboard.
 *
 * @param event - Leaflet keyboard event
 * @param open - Opens the popup or zooms
 * @example
 * const _ = true;
 */
function openOnKey(
  event: { originalEvent?: { key?: string; preventDefault?: () => void } },
  open: () => void,
) {
  const key = event.originalEvent?.key;
  if (key === 'Enter' || key === ' ') {
    event.originalEvent?.preventDefault?.();
    open();
  }
}

/**
 * Give a drawn shape a name for the keyboard.
 *
 * @param layer - Leaflet layer
 * @param label - Accessible name
 * @example
 * const _ = true;
 */
function nameLayer(layer: L.Layer, label: string) {
  const readable = layer as { getElement?: () => HTMLElement | undefined };
  const element = readable.getElement?.() ?? null;
  if (!element) {
    return;
  }
  element.setAttribute('role', 'button');
  element.tabIndex = 0;
  element.setAttribute('aria-label', label);
}

/**
 * Pin position from the stored report coordinate.
 *
 * @param place - Cached place
 * @returns Latitude and longitude
 * @example
 * const _ = true;
 */
function pointOf(place: LivePlace): [number, number] {
  return [place.latitude, place.longitude];
}

/**
 * Draw one place as a point, polygon, line, or circle.
 *
 * @param map - Leaflet map
 * @param place - Cached place
 * @returns The layer that was added
 * @example
 * const _ = true;
 */
function drawPlace(map: L.Map, place: LivePlace, at?: [number, number]): L.Layer {
  const draw = drawForPlace(place);
  const paint = shapePaint(place.product);
  if (draw.kind === 'polygon') {
    return L.polygon(draw.positions, paint).addTo(map);
  }
  if (draw.kind === 'line') {
    return L.polyline(draw.positions, { color: paint.fillColor, weight: 3 }).addTo(map);
  }
  if (draw.kind === 'circle') {
    return L.circle([draw.latitude, draw.longitude], {
      ...paint,
      radius: draw.radiusM,
    }).addTo(map);
  }
  const [latitude, longitude] = at ?? [draw.latitude, draw.longitude];
  return L.circleMarker([latitude, longitude], {
    radius: 6,
    ...paint,
    fillOpacity: copyOpacity(0),
  }).addTo(map);
}

/**
 * Brighten a shape under the pointer, then put the resting paint back.
 *
 * @param layer - Drawn shape
 * @param place - Cached place
 * @param on - True while the pointer is over the shape
 * @example
 * const _ = true;
 */
function paintHover(layer: L.Layer, place: LivePlace, on: boolean) {
  const path = layer as unknown as { setStyle: (style: L.PathOptions) => void };
  const paint = shapePaint(place.product);
  const point = drawForPlace(place).kind === 'point';
  const resting = point ? { ...paint, fillOpacity: copyOpacity(0) } : paint;
  path.setStyle(on ? { ...resting, weight: resting.weight + 2 } : resting);
}

/**
 * Paint vectors again after a full replace. Leaflet 1.9.4 can leave the canvas blank.
 *
 * @param map - Leaflet map
 * @example
 * const _ = true;
 */
function redrawCanvas(map: L.Map): void {
  const renderer = map.options.renderer as unknown as {
    _map?: unknown;
    _update: () => void;
  };
  if (renderer._map) {
    renderer._update();
  }
}

/**
 * Station text inside the map card.
 *
 * @param place - Cached place
 * @param layout - Side by side on a wide map, stacked on a narrow one
 * @param onShowing - Remembers the copy on the card
 * @param onLoad - Loads that copy into the converter
 * @example
 * const _ = true;
 */
export function StationPopup({
  place,
  layout = 'side',
  onShowing,
  onLoad,
}: {
  place: LivePlace;
  layout?: 'side' | 'stack';
  onShowing?: (tac: string) => void;
  onLoad?: (tac: string) => void;
}) {
  const [index, setIndex] = useState(0);
  const report = place.reports[index];
  useEffect(() => {
    if (report) {
      onShowing?.(report.tac);
    }
  }, [onShowing, report]);
  if (!report) {
    return null;
  }
  const airportName = airports.findWhere({ icao: place.place_key })?.name;
  const station = placeTitle(place.place_key, airportName);
  return (
    <div
      data-testid="live-map-detail"
      className="max-h-48 overflow-y-auto text-sm text-gray-900"
    >
      <div
        data-testid="live-map-card"
        data-layout={layout}
        className={
          layout === 'side' ? 'flex flex-row items-start gap-3' : 'flex flex-col gap-2'
        }
        onClick={(event) => {
          event.stopPropagation();
          onLoad?.(report.tac);
        }}
      >
        <div className="flex min-w-0 flex-1 flex-col gap-1">
          <p className="text-base font-semibold" data-testid="live-map-product">
            {productLabel(place.product)}
          </p>
          <p data-testid="live-map-issued">{formatObservedAt(report.observed_at)}</p>
          <p className="font-medium" data-testid="live-map-station">
            {station}
          </p>
          {place.reports.length > 1 ? (
            <div className="flex gap-2">
              <button
                type="button"
                className="text-xs underline"
                data-testid="live-map-newer"
                onClick={(event) => {
                  event.stopPropagation();
                  setIndex((current) => Math.max(0, current - 1));
                }}
              >
                {LIVE_MAP_NEWER}
              </button>
              <button
                type="button"
                className="text-xs underline"
                data-testid="live-map-earlier"
                onClick={(event) => {
                  event.stopPropagation();
                  setIndex((current) =>
                    Math.min(place.reports.length - 1, current + 1),
                  );
                }}
              >
                {LIVE_MAP_EARLIER}
              </button>
            </div>
          ) : null}
        </div>
        <div className="flex min-w-0 flex-1 flex-col gap-1">
          <p className="text-xs font-medium">{LIVE_MAP_TAC}</p>
          <pre
            className="max-h-32 overflow-y-auto whitespace-pre-wrap font-mono text-xs"
            data-testid="live-map-tac"
          >
            {report.tac}
          </pre>
        </div>
      </div>
    </div>
  );
}

/**
 * Open a scrolling popup on a station. A cluster does not use this.
 *
 * @param layer - Station layer
 * @param place - Cached place
 * @param roots - React roots to unmount with the layer
 * @example
 * const _ = true;
 */
function showPopup(
  layer: L.Layer,
  place: LivePlace,
  roots: Root[],
  map: L.Map,
  onShowing: (tac: string) => void,
  onLoad: (tac: string) => void,
) {
  if (place.reports.length === 0) {
    return;
  }
  const stale = roots.splice(0);
  queueMicrotask(() => {
    stale.forEach((root) => {
      root.unmount();
    });
  });
  const node = document.createElement('div');
  const root = createRoot(node);
  flushSync(() => {
    root.render(
      <StationPopup
        place={place}
        layout={cardLayout(map.getSize().x)}
        onShowing={onShowing}
        onLoad={onLoad}
      />,
    );
  });
  roots.push(root);
  const width = popupWidth(map.getSize().x);
  layer.bindPopup(node, {
    maxWidth: width,
    minWidth: Math.min(280, width),
    autoPan: false,
    keepInView: false,
    autoClose: true,
    closeOnClick: true,
    className: 'live-map-popup',
  });
  layer.openPopup();
  layer.getPopup()?.update();
}

/**
 * Pannable map. Every layer starts on.
 * @example
 * const _ = true;
 */
export function LiveWorldMap({
  focusStation = '',
  onOpenPlace,
}: {
  focusStation?: string;
  /** Load the clicked report into the converter above the map. */
  onOpenPlace?: (place: LivePlace) => void;
}) {
  const host = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const openPlaceRef = useRef(onOpenPlace);
  useEffect(() => {
    openPlaceRef.current = onOpenPlace;
  }, [onOpenPlace]);
  const [off, setOff] = useState<ReadonlySet<string>>(new Set());
  const [country, setCountry] = useState('all');
  const [region, setRegion] = useState('all');
  const [timePreset, setTimePreset] = useState<MapTimePreset>('all');
  const [phenomena, setPhenomena] = useState<ReadonlySet<string>>(new Set());
  const [bounds, setBounds] = useState<MapBounds | null>(null);
  const [places, setPlaces] = useState<LivePlace[]>([]);
  const [error, setError] = useState('');
  const [phase, setPhase] = useState<'loading' | 'ready' | 'refreshing'>('loading');
  const [refreshTick, setRefreshTick] = useState(0);
  const products = selectedLayerQuery(off);
  const loaded = bounds && products ? places : EMPTY_PLACES;
  const countries = [
    ...new Set(
      loaded
        .map((place) => airports.findWhere({ icao: place.place_key })?.country)
        .filter((name): name is string => Boolean(name)),
    ),
  ].sort((left, right) => left.localeCompare(right));
  const visible = filterPlaces(loaded, {
    country,
    region,
    time: timePreset,
    phenomena,
    countryOf: (placeKey) => airports.findWhere({ icao: placeKey })?.country,
    regionOf: (latitude, longitude) => placeRegion(latitude, longitude),
  });
  const message = products ? error : '';
  const status = !products
    ? LIVE_MAP_LAYERS_OFF
    : viewStatus(visible, phase === 'loading', phase === 'refreshing');

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !focusStation) {
      return;
    }
    const place = places.find((item) => item.place_key === focusStation);
    if (!place) {
      return;
    }
    map.flyTo(pointOf(place), 8);
  }, [focusStation, places]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) {
      return undefined;
    }
    const roots: Root[] = [];
    const layers: L.Layer[] = [];
    let focused = false;
    const cohorts = new Map<string, LivePlace[]>();
    visible.forEach((place) => {
      if (drawForPlace(place).kind !== 'point') {
        return;
      }
      const key = `${place.latitude.toFixed(3)},${place.longitude.toFixed(3)}`;
      const group = cohorts.get(key) ?? [];
      group.push(place);
      cohorts.set(key, group);
    });
    visible.forEach((place) => {
      const draw = drawForPlace(place);
      const key = `${place.latitude.toFixed(3)},${place.longitude.toFixed(3)}`;
      const group = cohorts.get(key) ?? [];
      const slot = Math.max(0, group.indexOf(place));
      const nudge = pointNudge(slot, group.length);
      const moved = nudge.latitude !== 0 || nudge.longitude !== 0;
      const at: [number, number] | undefined =
        draw.kind === 'point' && (moved || place.reports.length > 1 || group.length > 1)
          ? [draw.latitude + nudge.latitude, draw.longitude + nudge.longitude]
          : undefined;
      const layer = drawPlace(map, place, at);
      if (at && place.reports.length > 1) {
        place.reports.slice(1).forEach((_, reportIndex) => {
          layers.push(
            L.circleMarker(at, {
              radius: 4,
              ...shapePaint(place.product),
              fillOpacity: copyOpacity(reportIndex + 1),
            }).addTo(map),
          );
        });
      }
      if (at && group.length > 1) {
        layers.push(
          L.marker(at, {
            interactive: false,
            keyboard: false,
            icon: L.divIcon({
              className: 'live-map-type-chip',
              html: productLabel(place.product),
              iconSize: [72, 18],
            }),
          }).addTo(map),
        );
      }
      let cardOpen = false;
      let showingTac = place.reports[0]?.tac ?? '';
      const remember = (tac: string) => {
        showingTac = tac;
      };
      const loadShowing = (tac: string) => {
        showingTac = tac;
        openPlaceRef.current?.(placeShowingReport(place, tac));
      };
      const reveal = () => {
        showPopup(layer, place, roots, map, remember, loadShowing);
        if (place.reports.length > 0) {
          cardOpen = true;
        }
      };
      layer.on('mouseover', () => {
        paintHover(layer, place, true);
        if (!cardOpen) {
          reveal();
        }
      });
      layer.on('mouseout', () => {
        paintHover(layer, place, false);
      });
      layer.on('click', () => {
        if (cardOpen) {
          loadShowing(showingTac);
        } else {
          reveal();
        }
      });
      layer.on('keydown', (event) => {
        openOnKey(event, () => {
          if (cardOpen) {
            loadShowing(showingTac);
          } else {
            reveal();
          }
        });
      });
      nameLayer(layer, `${place.place_key} ${productLabel(place.product)}`);
      if (!focused && focusStation && place.place_key === focusStation) {
        focused = true;
        reveal();
      }
      layers.push(layer);
    });
    redrawCanvas(map);
    return () => {
      layers.forEach((layer) => layer.remove());
      const pending = roots.splice(0);
      queueMicrotask(() => {
        pending.forEach((root) => {
          root.unmount();
        });
      });
    };
  }, [visible, focusStation]);

  useEffect(() => {
    const node = host.current as HTMLDivElement;
    const vectors = L.canvas({ tolerance: 18 });
    const map = L.map(node, {
      scrollWheelZoom: true,
      preferCanvas: true,
      renderer: vectors,
    }).setView([20, 0], 2);
    map.options.renderer = vectors;
    mapRef.current = map;
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap',
      maxZoom: 16,
    }).addTo(map);
    const fit = () => {
      map.invalidateSize();
    };
    fit();
    const observer = new ResizeObserver(fit);
    observer.observe(node);
    const publish = () => {
      setBounds(boundsOf(map));
    };
    map.on('moveend', publish);
    map.on('zoomend', publish);
    publish();
    return () => {
      observer.disconnect();
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!bounds || !products) {
      return undefined;
    }
    const controller = new AbortController();
    fetchLivePlaces(bounds, products, controller.signal)
      .then((next) => {
        setError('');
        setPlaces((current) => (placesMatch(current, next) ? current : next));
        setPhase('ready');
      })
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === 'AbortError') {
          return;
        }
        setError(LIVE_MAP_ERROR);
        setPlaces([]);
        setPhase('ready');
      });
    return () => controller.abort();
  }, [bounds, products, refreshTick]);

  useEffect(() => {
    if (!bounds || !products) {
      return undefined;
    }
    const timer = window.setInterval(() => {
      setPhase('refreshing');
      setRefreshTick((tick) => tick + 1);
    }, LIVE_MAP_REFRESH_MS);
    return () => window.clearInterval(timer);
  }, [bounds, products]);

  return (
    <div className="flex flex-col gap-3" data-testid="live-world-map">
      <p className="text-sm text-gray-600 dark:text-gray-300">
        <span data-testid="live-map-beta">{DECODE_VISUALS_BETA}</span>
        {'. '}
        <a href={DECODE_VISUALS_FEEDBACK_URL}>{DECODE_VISUALS_FEEDBACK}</a>
      </p>
      <p
        id="live-map-notice"
        className="text-sm text-gray-600 dark:text-gray-300"
        data-testid="live-map-notice"
      >
        {LIVE_MAP_NOTICE}
      </p>
      {LIVE_MAP_VIEWS.map((view) => (
        <div key={view.id} className="flex flex-wrap items-center gap-3">
          <span className="text-sm font-medium">{view.label}</span>
          {view.products.map((product) => (
            <label key={product} className="flex items-center gap-1 text-sm">
              <input
                type="checkbox"
                checked={!off.has(product)}
                data-testid={`layer-${product}`}
                onChange={() => {
                  const next = new Set(off);
                  if (next.has(product)) {
                    next.delete(product);
                  } else {
                    next.add(product);
                  }
                  setOff(next);
                }}
              />
              <span
                aria-hidden="true"
                data-testid={`swatch-${product}`}
                className="inline-block h-3 w-3 rounded-sm border border-white"
                style={{ backgroundColor: pinColor(product) }}
              />
              {productLabel(product)}
            </label>
          ))}
        </div>
      ))}
      <div className="flex flex-wrap items-center gap-3">
        <label className="flex items-center gap-1 text-sm">
          {LIVE_MAP_FILTER_COUNTRY}
          <select
            value={country}
            data-testid="live-map-country"
            onChange={(event) => {
              setCountry(event.target.value);
            }}
          >
            <option value="all">{LIVE_MAP_ALL_COUNTRIES}</option>
            {countries.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-1 text-sm">
          {LIVE_MAP_FILTER_REGION}
          <select
            value={region}
            data-testid="live-map-region"
            onChange={(event) => {
              setRegion(event.target.value);
            }}
          >
            <option value="all">{LIVE_MAP_ALL_REGIONS}</option>
            {regionFilterNames().map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </select>
        </label>
        <label className="flex items-center gap-1 text-sm">
          {LIVE_MAP_FILTER_TIME}
          <select
            value={timePreset}
            data-testid="live-map-time"
            onChange={(event) => {
              setTimePreset(event.target.value as MapTimePreset);
            }}
          >
            <option value="all">{LIVE_MAP_ALL_TIMES}</option>
            <option value="1h">{LIVE_MAP_LAST_HOUR}</option>
            <option value="6h">{LIVE_MAP_LAST_6_HOURS}</option>
            <option value="24h">{LIVE_MAP_LAST_24_HOURS}</option>
          </select>
        </label>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-sm font-medium">{LIVE_MAP_FILTER_PHENOMENON}</span>
        {LIVE_MAP_PHENOMENA.map((item) => (
          <label key={item.id} className="flex items-center gap-1 text-sm">
            <input
              type="checkbox"
              checked={phenomena.has(item.id)}
              data-testid={`phenomenon-${item.id}`}
              onChange={() => {
                const next = new Set(phenomena);
                if (next.has(item.id)) {
                  next.delete(item.id);
                } else {
                  next.add(item.id);
                }
                setPhenomena(next);
              }}
            />
            {item.label}
          </label>
        ))}
      </div>
      <p
        className="text-xs text-gray-600 dark:text-gray-300"
        data-testid="live-map-space"
        style={{ color: spaceWeatherListColor(0) }}
      >
        {LIVE_MAP_SPACE}
      </p>
      {message ? (
        <p
          className="text-sm text-gray-600 dark:text-gray-300"
          data-testid="live-map-error"
        >
          {message}
        </p>
      ) : (
        <p className="text-sm font-medium" data-testid="live-map-status">
          {status}
        </p>
      )}
      <p className="text-xs text-gray-500 dark:text-gray-400">{LIVE_MAP_ZOOM_HINT}</p>
      <div
        ref={host}
        role="region"
        aria-label={LIVE_MAP_CANVAS}
        aria-describedby="live-map-notice"
        className="z-0 h-[100dvh] min-h-[100dvh] w-full overflow-hidden rounded border border-gray-200 dark:border-gray-700"
        data-testid="live-map-canvas"
      />
    </div>
  );
}
