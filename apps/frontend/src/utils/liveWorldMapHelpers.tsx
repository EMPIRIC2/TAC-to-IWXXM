/* eslint-disable react-refresh/only-export-components */
/** Helpers extracted from LiveWorldMap. */

/**
 * World map of cached TAC reports.
 */

import { flushSync } from 'react-dom';
import { createRoot, type Root } from 'react-dom/client';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { drawForPlace } from '@metar/live-map-geometry';
import {
  cardLayout,
  copyOpacity,
  pointerSlack,
  popupWidth,
  shapePaint,
  shiftLatLng,
  shiftPositions,
  type LivePlace,
} from '@/utils/liveMap';
import {
  clusterReportChoices,
  type StationCluster,
} from '@/utils/liveMapStationCluster';
import { StationClusterPopup } from '@/app/components/StationClusterPopup';
import { StationPopup } from '@/app/components/StationPopup';

export { StationPopup } from '@/app/components/StationPopup';

export const EMPTY_PLACES: LivePlace[] = [];

/**
 * True when two fetches describe the same drawn reports.
 *
 * @param current - Places already on the map
 * @param next - Places just fetched
 * @returns Whether a redraw can be skipped
 * @example
 * const _ = true;
 */
export function placesMatch(current: LivePlace[], next: LivePlace[]): boolean {
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
export function openOnKey(
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
export function nameLayer(layer: L.Layer, label: string) {
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
export function pointOf(place: LivePlace): [number, number] {
  return [place.latitude, place.longitude];
}

type PointerPath = {
  _clickTolerance?: () => number;
  _containsPoint?: (point: L.Point, closed?: boolean) => boolean;
  _point?: L.Point;
  _radius?: number;
};

/**
 * Keep the pointer on the dot or along the edge. [Corpus: product §F37]
 *
 * A wide halo opened the card while the pointer was still on empty map.
 * The inside of a polygon or circle stays free so the map can still be moved.
 *
 * @param layer - Drawn shape
 * @param kind - Point, line, polygon, or circle
 * @example
 * const _ = true;
 */
export function fitPointerTarget(
  layer: L.Layer,
  kind: 'point' | 'polygon' | 'line' | 'circle',
) {
  const path = layer as PointerPath;
  path._clickTolerance = () => pointerSlack(kind);
  if (kind === 'polygon') {
    const stroke = (
      L.Polyline.prototype as unknown as {
        _containsPoint: (point: L.Point, closed?: boolean) => boolean;
      }
    )._containsPoint;
    path._containsPoint = function (point: L.Point) {
      return stroke.call(this, point, true);
    };
    return;
  }
  if (kind === 'circle') {
    path._containsPoint = function (point: L.Point) {
      const shape = this as PointerPath;
      if (!shape._point || shape._radius === undefined) {
        return false;
      }
      return (
        Math.abs(point.distanceTo(shape._point) - shape._radius) <=
        pointerSlack('circle')
      );
    };
  }
}

/**
 * Draw one place as a point, polygon, line, or circle.
 *
 * @param map - Leaflet map
 * @param place - Cached place
 * @param at - Optional nudged station coordinates on the primary copy
 * @param lngOffset - World-copy longitude shift (−360, 0, or 360)
 * @returns The layer that was added
 * @example
 * const _ = true;
 */
export function drawPlace(
  map: L.Map,
  place: LivePlace,
  at?: [number, number],
  lngOffset = 0,
): L.Layer {
  const draw = drawForPlace(place);
  const paint = shapePaint(place.product);
  if (draw.kind === 'polygon') {
    const layer = L.polygon(shiftPositions(draw.positions, lngOffset), paint);
    fitPointerTarget(layer, draw.kind);
    return layer.addTo(map);
  }
  if (draw.kind === 'line') {
    const layer = L.polyline(shiftPositions(draw.positions, lngOffset), {
      color: paint.fillColor,
      weight: 3,
    });
    fitPointerTarget(layer, draw.kind);
    return layer.addTo(map);
  }
  if (draw.kind === 'circle') {
    const layer = L.circle(shiftLatLng(draw.latitude, draw.longitude, lngOffset), {
      ...paint,
      radius: draw.radiusM,
    });
    fitPointerTarget(layer, draw.kind);
    return layer.addTo(map);
  }
  const pointAt = at as [number, number];
  const layer = L.circleMarker(shiftLatLng(pointAt[0], pointAt[1], lngOffset), {
    radius: 6,
    ...paint,
    fillOpacity: copyOpacity(0),
  });
  fitPointerTarget(layer, 'point');
  return layer.addTo(map);
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
export function paintHover(layer: L.Layer, place: LivePlace, on: boolean) {
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
export function redrawCanvas(map: L.Map): void {
  const renderer = map.options.renderer as unknown as {
    _map?: unknown;
    _update: () => void;
  };
  if (renderer._map) {
    renderer._update();
  }
}

/**
 * Open a scrolling popup on a station or same-station cluster.
 *
 * @param layer - Station layer
 * @param cluster - Same-station members
 * @param roots - React roots to unmount with the layer
 * @example
 * const _ = true;
 */
export function showClusterPopup(
  layer: L.Layer,
  cluster: StationCluster,
  roots: Root[],
  map: L.Map,
  onShowing: (tac: string) => void,
  onLoad: (tac: string) => void,
) {
  const choices = clusterReportChoices(cluster);
  if (choices.length === 0) {
    return;
  }
  const stale = roots.splice(0);
  stale.forEach((root) => {
    root.unmount();
  });
  const node = document.createElement('div');
  const root = createRoot(node);
  const layout = cardLayout(map.getSize().x);
  const sole = choices[0];
  flushSync(() => {
    root.render(
      choices.length > 1 || !sole ? (
        <StationClusterPopup
          cluster={cluster}
          layout={layout}
          onShowing={onShowing}
          onLoad={onLoad}
        />
      ) : (
        <StationPopup
          place={sole.place}
          layout={layout}
          onShowing={onShowing}
          onLoad={onLoad}
        />
      ),
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
 * Open a scrolling popup on an area shape (one place).
 *
 * @param layer - Drawn shape
 * @param place - Cached place
 * @param roots - React roots to unmount with the layer
 * @example
 * const _ = true;
 */
export function showPopup(
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
  stale.forEach((root) => {
    root.unmount();
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
