/**
 * World map of cached TAC reports.
 */

import { useEffect, useRef, useState } from 'react';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import {
  DECODE_VISUALS_BETA,
  DECODE_VISUALS_FEEDBACK,
  DECODE_VISUALS_FEEDBACK_URL,
} from '@/utils/decodeVisualsCopy';
import { airports } from '@/utils/airportsData';
import {
  boundsOf,
  fetchLivePlaces,
  LIVE_MAP_PRODUCTS,
  selectedLayerQuery,
  windFromTac,
  type LivePlace,
  type MapBounds,
} from '@/utils/liveMap';

const EMPTY_PLACES: LivePlace[] = [];

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
  return L.marker(pointOf(place)).addTo(map);
}

/**
 * Pannable map. Every layer starts on.
 * @example
 * const _ = true;
 */
export function LiveWorldMap() {
  const host = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const [off, setOff] = useState<ReadonlySet<string>>(new Set());
  const [bounds, setBounds] = useState<MapBounds | null>(null);
  const [places, setPlaces] = useState<LivePlace[]>([]);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState<LivePlace | null>(null);
  const [reportIndex, setReportIndex] = useState(0);
  const products = selectedLayerQuery(off);
  const visible = bounds && products ? places : EMPTY_PLACES;
  const message = products ? error : '';
  const report = selected?.reports[reportIndex];
  const placeName =
    selected && /^[A-Z][A-Z0-9]{3}$/.test(selected.place_key)
      ? (airports.findWhere({ icao: selected.place_key })?.name ?? selected.place_key)
      : selected?.place_key;

  useEffect(() => {
    const node = host.current as HTMLDivElement;
    const map = L.map(node, { scrollWheelZoom: true }).setView([20, 0], 2);
    mapRef.current = map;
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap',
      maxZoom: 16,
    }).addTo(map);
    const publish = () => setBounds(boundsOf(map));
    map.on('moveend', publish);
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
      })
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === 'AbortError') {
          return;
        }
        setError('The live map could not be loaded.');
        setPlaces([]);
      });
    return () => controller.abort();
  }, [bounds, products]);

  useEffect(() => {
    const map = mapRef.current as L.Map;
    const markers = visible.map((place) => {
      const marker = drawPlace(map, place);
      marker.on('click', () => {
        setSelected(place);
        setReportIndex(0);
      });
      return marker;
    });
    return () => {
      markers.forEach((marker) => marker.remove());
    };
  }, [visible]);

  return (
    <div className="flex flex-col gap-3" data-testid="live-world-map">
      <p className="text-sm text-gray-600 dark:text-gray-300">
        <span data-testid="live-map-beta">{DECODE_VISUALS_BETA}</span>
        {'. '}
        <a href={DECODE_VISUALS_FEEDBACK_URL}>{DECODE_VISUALS_FEEDBACK}</a>
      </p>
      <div className="flex flex-wrap gap-3">
        {LIVE_MAP_PRODUCTS.map((product) => (
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
            {product.toUpperCase()}
          </label>
        ))}
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-300">
        Space weather has no map location.
      </p>
      {message ? (
        <p
          className="text-sm text-gray-600 dark:text-gray-300"
          data-testid="live-map-error"
        >
          {message}
        </p>
      ) : null}
      <div
        ref={host}
        className="z-0 h-[min(36rem,calc(100dvh-18rem))] min-h-[20rem] w-full overflow-hidden rounded border border-gray-200 dark:border-gray-700"
        data-testid="live-map-canvas"
      />
      {selected && report ? (
        <div data-testid="live-map-detail" className="flex flex-col gap-2 text-sm">
          <p className="font-medium">{placeName}</p>
          <p data-testid="live-map-wind">{windFromTac(report.tac)}</p>
          <div className="flex flex-wrap gap-2">
            {selected.reports.map((item, index) => (
              <button
                key={item.observed_at}
                type="button"
                data-testid={`live-map-report-${index}`}
                onClick={() => {
                  setReportIndex(index);
                }}
              >
                {item.observed_at}
              </button>
            ))}
          </div>
          <pre className="whitespace-pre-wrap" data-testid="live-map-tac">
            {report.tac}
          </pre>
          {report.iwxxm ? (
            <pre className="whitespace-pre-wrap" data-testid="live-map-xml">
              {report.iwxxm}
            </pre>
          ) : report.issues && report.issues.length > 0 ? (
            <p data-testid="live-map-issues">{report.issues.join(' ')}</p>
          ) : (
            <p data-testid="live-map-pending">Translation is pending.</p>
          )}
        </div>
      ) : null}
    </div>
  );
}
