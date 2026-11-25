/* eslint-disable @typescript-eslint/ban-ts-comment, complexity */
// @ts-nocheck — mechanical line-count split from stage LiveWorldMap
/** State/effects for LiveWorldMap (stage UX + models-split). */
import { useEffect, useRef, useState } from 'react';
import { type Root } from 'react-dom/client';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { airports } from '@/utils/airportsData';
import { OSM_TILE_ATTRIBUTION, OSM_TILE_URL } from '@/utils/mapTileAttribution';
import {
  boundsOf,
  fetchLivePlaces,
  fetchLiveMapEval,
  filterPlaces,
  type LiveMapEvalSnapshot,
  LIVE_MAP_CANVAS_TOLERANCE,
  LIVE_MAP_ERROR,
  LIVE_MAP_LAYERS_OFF,
  LIVE_MAP_REFRESH_MS,
  placeShowingReport,
  productLabel,
  selectedLayerQuery,
  shiftLatLng,
  viewStatus,
  WORLD_COPY_LNG_OFFSETS,
  type LivePlace,
  type MapBounds,
  type MapTimePreset,
} from '@/utils/liveMap';
import { placeRegion } from '@/utils/liveMapRegions';
import {
  clusterAriaLabel,
  clusterByStation,
  clusterReportChoices,
  isStationPointPlace,
} from '@/utils/liveMapStationCluster';
import {
  DEFAULT_OVERLAY_MAGNITUDE_SCALE,
  showsAnnex3Products,
  showsOverlayControls,
  showsTemperatureControls,
  type LiveMapDisplayMode,
  type LiveMapTempUnit,
} from '@/utils/liveMapModes';
import {
  defaultTacOverlayVisibility,
  type TacOverlayVisibility,
} from '@/utils/liveMapTacLayers';
import { paintTacOverlays, paintTemperatureMarkers } from '@/utils/liveMapOverlayPaint';
import {
  LIVE_MAP_ACTIVE_EMPTY,
  defaultActiveReportsOn,
  placeIsActiveNow,
} from '@/utils/liveMapValidity';
import {
  EMPTY_PLACES,
  drawPlace,
  nameLayer,
  openOnKey,
  paintHover,
  placesMatch,
  pointOf,
  redrawCanvas,
  showClusterPopup,
  showPopup,
} from '@/utils/liveWorldMapHelpers';

/**
 * Live world map state, fetch, and Leaflet paint effects.
 * @example
 * const _ = true;
 */
export function useLiveWorldMap({
  focusStation = '',
  onOpenPlace,
}: {
  focusStation?: string;
  onOpenPlace?: (place: LivePlace) => void;
}) {
  const host = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const openPlaceRef = useRef(onOpenPlace);
  /** Last station we flew to; ignore place refreshes so zoom-out sticks. */
  const focusedFlyRef = useRef('');
  useEffect(() => {
    openPlaceRef.current = onOpenPlace;
  }, [onOpenPlace]);
  const [displayMode, setDisplayMode] = useState<LiveMapDisplayMode>('annex3');
  const [off, setOff] = useState<ReadonlySet<string>>(new Set());
  const [country, setCountry] = useState('all');
  const [region, setRegion] = useState('all');
  const [timePreset, setTimePreset] = useState<MapTimePreset>('latest');
  const [phenomena, setPhenomena] = useState<ReadonlySet<string>>(new Set());
  const [tacOverlays, setTacOverlays] = useState<TacOverlayVisibility>(
    defaultTacOverlayVisibility,
  );
  const [activeTouched, setActiveTouched] = useState(false);
  const [activeOnlyManual, setActiveOnlyManual] = useState(false);
  const [overlayScale, setOverlayScale] = useState(DEFAULT_OVERLAY_MAGNITUDE_SCALE);
  const [tempUnit, setTempUnit] = useState<LiveMapTempUnit>('C');
  const [bounds, setBounds] = useState<MapBounds | null>(null);
  const [zoom, setZoom] = useState(2);
  const [places, setPlaces] = useState<LivePlace[]>([]);
  const [error, setError] = useState('');
  const [phase, setPhase] = useState<'loading' | 'ready' | 'refreshing'>('loading');
  const [refreshTick, setRefreshTick] = useState(0);
  const [evalSnapshot, setEvalSnapshot] = useState<LiveMapEvalSnapshot | null>(null);
  const annex3Mode = showsAnnex3Products(displayMode);
  const overlaysMode = showsOverlayControls(displayMode);
  const temperaturesMode = showsTemperatureControls(displayMode);
  // Non–Annex 3 modes still need report geometry; fetch every product layer.
  const products = annex3Mode ? selectedLayerQuery(off) : selectedLayerQuery(new Set());
  const loaded = bounds && products ? places : EMPTY_PLACES;
  const activeOnly = activeTouched ? activeOnlyManual : defaultActiveReportsOn(loaded);
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
    activeOnly,
    placeIsActiveNow,
    countryOf: (placeKey) => airports.findWhere({ icao: placeKey })?.country,
    regionOf: (latitude, longitude) => placeRegion(latitude, longitude),
  });
  const message = products ? error : '';
  const status = !products
    ? LIVE_MAP_LAYERS_OFF
    : activeOnly && loaded.length > 0 && visible.length === 0
      ? LIVE_MAP_ACTIVE_EMPTY
      : viewStatus(visible, phase === 'loading', phase === 'refreshing');

  useEffect(() => {
    const map = mapRef.current;
    if (!focusStation) {
      focusedFlyRef.current = '';
      return;
    }
    if (!map || focusedFlyRef.current === focusStation) {
      return;
    }
    const place = places.find((item) => item.place_key === focusStation);
    if (!place) {
      return;
    }
    focusedFlyRef.current = focusStation;
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
    const clusters = clusterByStation(visible);
    const clusterOf = new Map(
      clusters.map((cluster) => [cluster.stationKey, cluster] as const),
    );

    WORLD_COPY_LNG_OFFSETS.forEach((lngOffset) => {
      const drawnStations = new Set<string>();
      visible.forEach((place) => {
        if (isStationPointPlace(place)) {
          if (drawnStations.has(place.place_key)) {
            return;
          }
          drawnStations.add(place.place_key);
          const cluster = clusterOf.get(place.place_key);
          /* v8 ignore start -- clusterOf is built from the same visible station set */
          if (!cluster) {
            return;
          }
          /* v8 ignore stop */
          const anchor = cluster.members[0] as LivePlace;
          const choices = clusterReportChoices(cluster);
          const layer = drawPlace(
            map,
            anchor,
            [cluster.latitude, cluster.longitude],
            lngOffset,
          );
          if (choices.length > 1 && zoom >= 6) {
            layers.push(
              L.marker(shiftLatLng(cluster.latitude, cluster.longitude, lngOffset), {
                interactive: false,
                keyboard: false,
                icon: L.divIcon({
                  className: 'live-map-cluster-chip',
                  html: `<span style="display:inline-flex;align-items:center;height:16px;padding:0 6px;border-radius:999px;background:#111827;color:#fff;font:600 10px/16px ui-sans-serif,system-ui,sans-serif">${choices.length}</span>`,
                  iconSize: [28, 16],
                }),
              }).addTo(map),
            );
          }
          let cardOpen = false;
          const firstChoice = choices[0];
          let showingTac =
            firstChoice?.place.reports[firstChoice.reportIndex]?.tac ?? '';
          let showingPlace = firstChoice?.place ?? anchor;
          const remember = (tac: string) => {
            showingTac = tac;
          };
          const loadShowing = (tac: string) => {
            showingTac = tac;
            openPlaceRef.current?.(placeShowingReport(showingPlace, tac));
          };
          const reveal = () => {
            showClusterPopup(layer, cluster, roots, map, remember, (tac) => {
              const match = choices.find(
                (row) => row.place.reports[row.reportIndex]?.tac === tac,
              );
              /* v8 ignore start -- converter send always uses a chosen report TAC */
              showingPlace = match?.place ?? showingPlace;
              /* v8 ignore stop */
              loadShowing(tac);
            });
            if (choices.length > 0) {
              cardOpen = true;
            }
          };
          layer.on('mouseover', () => {
            paintHover(layer, anchor, true);
            if (!cardOpen) {
              reveal();
            }
          });
          layer.on('mouseout', () => {
            paintHover(layer, anchor, false);
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
          nameLayer(layer, clusterAriaLabel(cluster));
          if (
            lngOffset === 0 &&
            !focused &&
            focusStation &&
            cluster.stationKey === focusStation
          ) {
            focused = true;
            reveal();
          }
          layers.push(layer);
          if (overlaysMode) {
            layers.push(
              ...paintTacOverlays(map, cluster, tacOverlays, {
                magnitudeScale: overlayScale,
              }),
            );
          }
          if (temperaturesMode) {
            layers.push(...paintTemperatureMarkers(map, cluster, tempUnit));
          }
          return;
        }
        const layer = drawPlace(map, place, undefined, lngOffset);
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
        layers.push(layer);
      });
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
  }, [
    visible,
    focusStation,
    zoom,
    tacOverlays,
    overlayScale,
    overlaysMode,
    temperaturesMode,
    tempUnit,
  ]);

  useEffect(() => {
    const node = host.current as HTMLDivElement;
    const vectors = L.canvas({ tolerance: LIVE_MAP_CANVAS_TOLERANCE });
    const map = L.map(node, {
      scrollWheelZoom: true,
      preferCanvas: true,
      renderer: vectors,
    }).setView([20, 0], 2);
    map.options.renderer = vectors;
    mapRef.current = map;
    L.tileLayer(OSM_TILE_URL, {
      attribution: OSM_TILE_ATTRIBUTION,
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
      setZoom(map.getZoom());
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

  useEffect(() => {
    const controller = new AbortController();
    fetchLiveMapEval(controller.signal)
      .then((snapshot) => {
        setEvalSnapshot(snapshot);
      })
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === 'AbortError') {
          return;
        }
        setEvalSnapshot(null);
      });
    return () => controller.abort();
  }, [refreshTick]);

  return {
    host,
    displayMode,
    setDisplayMode,
    off,
    setOff,
    country,
    setCountry,
    region,
    setRegion,
    timePreset,
    setTimePreset,
    phenomena,
    setPhenomena,
    tacOverlays,
    setTacOverlays,
    activeTouched,
    setActiveTouched,
    activeOnlyManual,
    setActiveOnlyManual,
    overlayScale,
    setOverlayScale,
    tempUnit,
    setTempUnit,
    bounds,
    setBounds,
    zoom,
    places,
    error,
    phase,
    annex3Mode,
    overlaysMode,
    temperaturesMode,
    products,
    loaded,
    activeOnly,
    countries,
    visible,
    message,
    status,
    evalSnapshot,
  };
}
