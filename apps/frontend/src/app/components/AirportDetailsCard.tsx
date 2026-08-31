/**
 * Airport metadata panel — surfaces F3 airport data in the conversion UI.
 */

import { useEffect, useState } from 'react';
import { fetchAirportRegion } from '../../utils/api';
import { airports } from '../../utils/airportsData';

interface AirportDetailsCardProps {
  icao: string;
}

interface AirportRegionInfo {
  icao_region: string;
  airport_code: string;
}

function AirportDetailsCardContent({ icao }: { icao: string }) {
  const airport = airports.findWhere({ icao });
  const [regionInfo, setRegionInfo] = useState<AirportRegionInfo | null>(null);
  const [regionError, setRegionError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    fetchAirportRegion(icao)
      .then((data) => {
        if (!cancelled) {
          setRegionInfo(data);
          setRegionError(null);
        }
      })
      .catch((err: Error) => {
        if (!cancelled) {
          setRegionInfo(null);
          setRegionError(err.message);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [icao]);

  return (
    <div
      className="col-span-full rounded-md border border-blue-200 bg-blue-50 p-3 text-sm dark:border-blue-800 dark:bg-blue-950/40"
      aria-label="Airport details"
    >
      <p className="font-semibold text-gray-900 dark:text-white">
        {airport?.name ?? icao}
      </p>
      {(airport?.city || airport?.country) && (
        <p className="text-gray-600 dark:text-gray-300">
          {[airport?.city, airport?.country].filter(Boolean).join(', ')}
        </p>
      )}
      <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-600 dark:text-gray-400">
        {airport?.iata && <span>IATA: {airport.iata}</span>}
        {loading && <span>Loading ICAO region…</span>}
        {regionInfo && <span>ICAO region: {regionInfo.icao_region}</span>}
        {regionError && (
          <span className="text-amber-700 dark:text-amber-400">{regionError}</span>
        )}
      </div>
    </div>
  );
}

/**
 * Renders airport metadata and ICAO region lookup for a valid four-letter code.
 *
 * Returns null when the ICAO is missing or not in the local airport catalog.
 */
export function AirportDetailsCard({ icao }: AirportDetailsCardProps) {
  const normalized = icao.trim().toUpperCase();
  const isValidIcao = normalized.length === 4 && airports.isValid(normalized);

  if (!isValidIcao) {
    return null;
  }

  return <AirportDetailsCardContent key={normalized} icao={normalized} />;
}
