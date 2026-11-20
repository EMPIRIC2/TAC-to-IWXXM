/**
 * World map of cached TAC reports.
 */
import type { LivePlace } from '@/models/liveMap';
import { LiveWorldMapView } from './LiveWorldMapView';
import { useLiveWorldMap } from '@/hooks/useLiveWorldMap';

export { StationPopup } from './StationPopup';

/**
 * Live world map shell.
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
  const map = useLiveWorldMap({ focusStation, onOpenPlace });
  return <LiveWorldMapView {...map} />;
}
