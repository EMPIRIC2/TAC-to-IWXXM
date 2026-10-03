/**
 * World map of cached TAC reports.
 */

import { useEffect, useRef, useState } from 'react';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import {
  boundsOf,
  fetchLivePlaces,
  iwxxmForReport,
  layerQuery,
  LIVE_MAP_VIEWS,
  viewById,
  windFromTac,
  type LivePlace,
  type MapBounds,
} from '@/utils/liveMap';

const EMPTY_PLACES: LivePlace[] = [];

/**
 * Pannable map. Observations starts with METAR and SPECI on.
 * @example
 * const _ = true;
 */
export function LiveWorldMap() {
  const host = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const [view, setView] =
    useState<(typeof LIVE_MAP_VIEWS)[number]['id']>('observations');
  const [off, setOff] = useState<ReadonlySet<string>>(new Set());
  const [bounds, setBounds] = useState<MapBounds | null>(null);
  const [places, setPlaces] = useState<LivePlace[]>([]);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState<LivePlace | null>(null);
  const [reportIndex, setReportIndex] = useState(0);
  const [iwxxm, setIwxxm] = useState('');
  const products = layerQuery(view, off);
  const currentView = viewById(view);
  const visible = bounds && products ? places : EMPTY_PLACES;
  const message = products ? error : '';
  const report = selected?.reports[reportIndex];

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
      const marker = L.marker([place.latitude, place.longitude]).addTo(map);
      marker.on('click', () => {
        setSelected(place);
        setReportIndex(0);
        setIwxxm('');
      });
      return marker;
    });
    return () => {
      markers.forEach((marker) => marker.remove());
    };
  }, [visible]);

  return (
    <div className="flex flex-col gap-3" data-testid="live-world-map">
      <div className="flex flex-wrap gap-2" role="tablist" aria-label="Map views">
        {LIVE_MAP_VIEWS.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={item.id === view}
            data-testid={`view-${item.id}`}
            className="rounded border border-gray-300 px-3 py-1 text-sm dark:border-gray-600"
            onClick={() => {
              setView(item.id);
              setOff(new Set());
              setSelected(null);
            }}
          >
            {item.label}
          </button>
        ))}
      </div>
      <div className="flex flex-wrap gap-3">
        {currentView.products.map((product) => (
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
          <p className="font-medium">{selected.place_key}</p>
          <p data-testid="live-map-wind">{windFromTac(report.tac)}</p>
          <div className="flex flex-wrap gap-2">
            {selected.reports.map((item, index) => (
              <button
                key={item.observed_at}
                type="button"
                data-testid={`live-map-report-${index}`}
                onClick={() => {
                  setReportIndex(index);
                  setIwxxm('');
                }}
              >
                {item.observed_at}
              </button>
            ))}
          </div>
          <pre className="whitespace-pre-wrap" data-testid="live-map-tac">
            {report.tac}
          </pre>
          <button
            type="button"
            data-testid="live-map-iwxxm"
            onClick={() => {
              const controller = new AbortController();
              iwxxmForReport(report.tac, selected.product, controller.signal)
                .then(setIwxxm)
                .catch(() => setIwxxm('IWXXM is not available for this report.'));
            }}
          >
            Show IWXXM
          </button>
          {iwxxm ? (
            <pre className="whitespace-pre-wrap" data-testid="live-map-xml">
              {iwxxm}
            </pre>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
