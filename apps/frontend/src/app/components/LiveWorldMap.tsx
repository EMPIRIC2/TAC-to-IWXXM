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
  fetchLivePlaces,
  LIVE_MAP_CANVAS,
  LIVE_MAP_ERROR,
  LIVE_MAP_LAYERS_OFF,
  LIVE_MAP_NOTICE,
  LIVE_MAP_REFRESH_MS,
  LIVE_MAP_SPACE,
  LIVE_MAP_TAC,
  LIVE_MAP_VIEWS,
  LIVE_MAP_ZOOM_HINT,
  pinColor,
  popupWidth,
  productLabel,
  selectedLayerQuery,
  viewStatus,
  type LivePlace,
  type MapBounds,
} from '@/utils/liveMap';

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
function drawPlace(map: L.Map, place: LivePlace): L.Layer {
  const draw = drawForPlace(place);
  if (draw.kind === 'polygon') {
    return L.polygon(draw.positions).addTo(map);
  }
  if (draw.kind === 'line') {
    return L.polyline(draw.positions).addTo(map);
  }
  if (draw.kind === 'circle') {
    return L.circle([draw.latitude, draw.longitude], { radius: draw.radiusM }).addTo(
      map,
    );
  }
  const color = pinColor(place.product);
  return L.circleMarker([draw.latitude, draw.longitude], {
    radius: 6,
    color: '#ffffff',
    weight: 2,
    fillColor: color,
    fillOpacity: 1,
  }).addTo(map);
}

/**
 * Paint vectors again after a full replace. Leaflet 1.9.4 can leave the canvas blank.
 *
 * @param map - Leaflet map
 * @example
 * const _ = true;
 */
function redrawCanvas(map: L.Map): void {
  (map.options.renderer as unknown as { _update: () => void })._update();
}

/**
 * Station text inside the map popup.
 *
 * @param place - Cached place
 * @example
 * const _ = true;
 */
export function StationPopup({ place }: { place: LivePlace }) {
  const report = place.reports[0];
  if (!report) {
    return null;
  }
  const airportName = airports.findWhere({ icao: place.place_key })?.name;
  return (
    <div
      data-testid="live-map-detail"
      className="flex max-h-40 flex-col gap-1 overflow-y-auto text-sm text-gray-900"
    >
      <p className="text-base font-semibold" data-testid="live-map-station">
        {place.place_key}
      </p>
      {airportName ? <p>{airportName}</p> : null}
      <p className="text-xs font-medium">{LIVE_MAP_TAC}</p>
      <pre
        className="overflow-y-auto whitespace-pre-wrap font-mono text-xs"
        data-testid="live-map-tac"
      >
        {report.tac}
      </pre>
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
function showPopup(layer: L.Layer, place: LivePlace, roots: Root[], map: L.Map) {
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
    root.render(<StationPopup place={place} />);
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
  const [bounds, setBounds] = useState<MapBounds | null>(null);
  const [places, setPlaces] = useState<LivePlace[]>([]);
  const [error, setError] = useState('');
  const [phase, setPhase] = useState<'loading' | 'ready' | 'refreshing'>('loading');
  const [refreshTick, setRefreshTick] = useState(0);
  const products = selectedLayerQuery(off);
  const visible = bounds && products ? places : EMPTY_PLACES;
  const message = products ? error : '';
  const status = !products
    ? LIVE_MAP_LAYERS_OFF
    : viewStatus(places, phase === 'loading', phase === 'refreshing');

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
    visible.forEach((place) => {
      const layer = drawPlace(map, place);
      const open = (fromUser: boolean) => {
        showPopup(layer, place, roots, map);
        if (fromUser && place.reports[0]?.tac) {
          openPlaceRef.current?.(place);
        }
      };
      layer.on('click', () => {
        open(true);
      });
      layer.on('keydown', (event) => {
        openOnKey(event, () => {
          open(true);
        });
      });
      nameLayer(layer, `${place.place_key} ${productLabel(place.product)}`);
      if (!focused && focusStation && place.place_key === focusStation) {
        focused = true;
        open(false);
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
              {productLabel(product)}
            </label>
          ))}
        </div>
      ))}
      <p className="text-xs text-gray-600 dark:text-gray-300">{LIVE_MAP_SPACE}</p>
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
