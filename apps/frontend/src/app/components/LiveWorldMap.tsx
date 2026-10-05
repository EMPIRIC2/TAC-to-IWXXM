/**
 * World map of cached TAC reports.
 */

import { useEffect, useRef, useState } from 'react';
import { flushSync } from 'react-dom';
import { createRoot, type Root } from 'react-dom/client';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import {
  DECODE_VISUALS_BETA,
  DECODE_VISUALS_FEEDBACK,
  DECODE_VISUALS_FEEDBACK_URL,
} from '@/utils/decodeVisualsCopy';
import { airports } from '@/utils/airportsData';
import { decodeTac } from '@/utils/api';
import {
  boundsOf,
  fetchLivePlaces,
  formatObservedAt,
  LIVE_MAP_CANVAS,
  LIVE_MAP_DECODE,
  LIVE_MAP_ERROR,
  LIVE_MAP_IWXXM,
  LIVE_MAP_LATEST,
  LIVE_MAP_LAYERS_OFF,
  LIVE_MAP_NOTICE,
  LIVE_MAP_PENDING,
  LIVE_MAP_REFRESH_MS,
  LIVE_MAP_SPACE,
  LIVE_MAP_TAC,
  LIVE_MAP_VIEWS,
  LIVE_MAP_ZOOM_HINT,
  pinColor,
  placeTitle,
  popupWidth,
  productLabel,
  selectedLayerQuery,
  viewStatus,
  windFromTac,
  type LivePlace,
  type MapBounds,
} from '@/utils/liveMap';

const EMPTY_PLACES: LivePlace[] = [];
const POPUP_CLOSE_MS = 400;
let closeTimer = 0;

/**
 * Whether a mouse can rest on a popup. A phone tap should not arm the close timer.
 *
 * @returns True when the pointer can hover
 * @example
 * const _ = true;
 */
function pointerCanHover(): boolean {
  return window.matchMedia?.('(hover: hover)').matches ?? true;
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
  const kind = place.geometry?.kind ?? 'point';
  const coordinates = place.geometry?.coordinates;
  if (
    (kind === 'polygon' || kind === 'line') &&
    coordinates &&
    coordinates.length >= 2
  ) {
    const shape = kind === 'polygon' ? L.polygon(coordinates) : L.polyline(coordinates);
    return shape.addTo(map);
  }
  if (kind === 'circle' && place.geometry?.radius_m) {
    return L.circle(pointOf(place), { radius: place.geometry.radius_m }).addTo(map);
  }
  const color = pinColor(place.product);
  return L.marker(pointOf(place), {
    title: `${place.place_key} ${productLabel(place.product)}`,
    icon: L.divIcon({
      className: '',
      html: `<span style="display:flex;width:44px;height:44px;align-items:center;justify-content:center"><span style="display:block;width:12px;height:12px;border-radius:9999px;background:${color};border:2px solid #fff"></span></span>`,
      iconSize: [44, 44],
      iconAnchor: [22, 22],
    }),
  }).addTo(map);
}

/**
 * Station text inside the map popup.
 *
 * @param place - Cached place
 * @example
 * const _ = true;
 */
export function StationPopup({ place }: { place: LivePlace }) {
  const [reportIndex, setReportIndex] = useState(0);
  const [decodedFor, setDecodedFor] = useState<{ tac: string; text: string } | null>(
    null,
  );
  const report = place.reports[reportIndex] ?? place.reports[0];
  const decoded =
    report && decodedFor && decodedFor.tac === report.tac ? decodedFor.text : '';
  useEffect(() => {
    if (!report) {
      return undefined;
    }
    const controller = new AbortController();
    const tac = report.tac;
    decodeTac({
      manualText: tac,
      product: place.product,
      signal: controller.signal,
    })
      .then((result) => {
        setDecodedFor({ tac, text: result.summary });
      })
      .catch(() => {
        setDecodedFor({ tac, text: '' });
      });
    return () => {
      controller.abort();
    };
  }, [place.product, report]);
  if (!report) {
    return null;
  }
  const placeName = placeTitle(
    place.place_key,
    airports.findWhere({ icao: place.place_key })?.name,
  );
  return (
    <div
      data-testid="live-map-detail"
      tabIndex={-1}
      className="flex max-h-[70vh] flex-col gap-2 overflow-y-auto text-sm text-gray-900"
    >
      <p className="text-base font-semibold">{placeName}</p>
      <p>{productLabel(place.product)}</p>
      <p data-testid="live-map-wind">{windFromTac(report.tac)}</p>
      <div className="flex flex-wrap gap-2">
        {place.reports.map((item, index) => (
          <button
            key={`${item.observed_at}-${index}`}
            type="button"
            aria-pressed={index === reportIndex}
            data-testid={`live-map-report-${index}`}
            className={
              index === reportIndex
                ? 'min-h-9 rounded border px-2 py-1 text-xs font-semibold'
                : 'min-h-9 rounded border px-2 py-1 text-xs'
            }
            onClick={() => {
              setReportIndex(index);
            }}
          >
            {index === 0
              ? `${LIVE_MAP_LATEST} ${formatObservedAt(item.observed_at)}`
              : formatObservedAt(item.observed_at)}
          </button>
        ))}
      </div>
      <div>
        <p className="text-xs font-medium">{LIVE_MAP_TAC}</p>
        <pre
          className="max-h-40 overflow-y-auto whitespace-pre-wrap font-mono text-xs"
          data-testid="live-map-tac"
        >
          {report.tac}
        </pre>
      </div>
      <div>
        <p className="text-xs font-medium">{LIVE_MAP_DECODE}</p>
        <pre
          className="max-h-40 overflow-y-auto whitespace-pre-wrap text-xs"
          data-testid="live-map-decode"
        >
          {decoded}
        </pre>
      </div>
      {report.iwxxm ? (
        <div>
          <p className="text-xs font-medium">{LIVE_MAP_IWXXM}</p>
          <pre
            className="max-h-40 overflow-y-auto whitespace-pre-wrap font-mono text-xs"
            data-testid="live-map-xml"
          >
            {report.iwxxm}
          </pre>
        </div>
      ) : null}
      {report.issues && report.issues.length > 0 ? (
        <p data-testid="live-map-issues">{report.issues.join(' ')}</p>
      ) : null}
      {!report.iwxxm && (!report.issues || report.issues.length === 0) ? (
        <p data-testid="live-map-pending">{LIVE_MAP_PENDING}</p>
      ) : null}
      <p>{LIVE_MAP_NOTICE}</p>
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
  const node = document.createElement('div');
  const root = createRoot(node);
  flushSync(() => {
    root.render(<StationPopup place={place} />);
  });
  roots.push(root);
  map.eachLayer((item) => {
    if (item !== layer) {
      item.closePopup();
    }
  });
  const width = popupWidth(map.getSize().x);
  layer.bindPopup(node, {
    maxWidth: width,
    minWidth: Math.min(280, width),
    autoPan: false,
    keepInView: false,
    autoClose: false,
    closeOnClick: false,
    className: 'live-map-popup',
  });
  layer.openPopup();
  const popup = layer.getPopup();
  popup?.update();
  const element = popup?.getElement() ?? null;
  const container = map.getContainer();
  if (element) {
    container.querySelectorAll('.leaflet-popup').forEach((popupNode) => {
      if (!popupNode.contains(element)) {
        popupNode.remove();
      }
    });
    element.addEventListener('mouseenter', () => {
      window.clearTimeout(closeTimer);
    });
    element.addEventListener('mouseleave', () => {
      layer.closePopup();
    });
  }
}

/**
 * Pannable map. Every layer starts on.
 * @example
 * const _ = true;
 */
export function LiveWorldMap({ focusStation = '' }: { focusStation?: string }) {
  const host = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
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
      const open = () => {
        window.clearTimeout(closeTimer);
        showPopup(layer, place, roots, map);
      };
      layer.on('mouseover', open);
      layer.on('click', open);
      layer.on('keydown', (event) => {
        openOnKey(event, open);
      });
      layer.on('mouseout', () => {
        if (!pointerCanHover()) {
          return;
        }
        closeTimer = window.setTimeout(() => {
          layer.closePopup();
        }, POPUP_CLOSE_MS);
      });
      nameLayer(layer, `${place.place_key} ${productLabel(place.product)}`);
      if (!focused && focusStation && place.place_key === focusStation) {
        focused = true;
        open();
      }
      layers.push(layer);
    });
    return () => {
      window.clearTimeout(closeTimer);
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
    const map = L.map(node, { scrollWheelZoom: true }).setView([20, 0], 2);
    mapRef.current = map;
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap',
      maxZoom: 16,
    }).addTo(map);
    const publish = () => {
      setBounds(boundsOf(map));
    };
    map.on('moveend', publish);
    map.on('zoomend', publish);
    publish();
    return () => {
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
        setPlaces(next);
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
