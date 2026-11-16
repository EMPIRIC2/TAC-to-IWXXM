/* eslint-disable @typescript-eslint/ban-ts-comment, @typescript-eslint/no-explicit-any */
// @ts-nocheck — mechanical line-count split from stage LiveWorldMap
import {
  DECODE_VISUALS_BETA,
  DECODE_VISUALS_FEEDBACK,
  DECODE_VISUALS_FEEDBACK_URL,
} from '@/utils/decodeVisualsCopy';
import {
  LIVE_MAP_ALL_COUNTRIES,
  LIVE_MAP_ALL_REGIONS,
  LIVE_MAP_CANVAS,
  LIVE_MAP_FILTER_COUNTRY,
  LIVE_MAP_FILTER_PHENOMENON,
  LIVE_MAP_FILTER_REGION,
  LIVE_MAP_FILTER_TIME,
  LIVE_MAP_FULL_WINDOW,
  LIVE_MAP_LAST_12_HOURS,
  LIVE_MAP_LAST_3_HOURS,
  LIVE_MAP_LAST_6_HOURS,
  LIVE_MAP_LAST_HOUR,
  LIVE_MAP_NOTICE,
  LIVE_MAP_PHENOMENA,
  LIVE_MAP_SPACE,
  LIVE_MAP_VIEWS,
  LIVE_MAP_ZOOM_HINT,
  pinColor,
} from '@/utils/liveMap';
import { regionFilterNames } from '@/utils/liveMapRegions';
import {
  LIVE_MAP_DISPLAY_MODES,
  LIVE_MAP_MODE_GROUP,
  LIVE_MAP_OVERLAY_SCALE,
  LIVE_MAP_SHOW_LATEST,
  LIVE_MAP_TEMP_C,
  LIVE_MAP_TEMP_F,
  LIVE_MAP_TEMP_UNIT,
  clampOverlayMagnitudeScale,
  selectLiveMapMode,
  selectTempUnit,
} from '@/utils/liveMapModes';
import { toggleTacOverlay } from '@/utils/liveMapTacLayers';
import { LIVE_MAP_FILTER_ACTIVE } from '@/utils/liveMapValidity';
import { LiveMapTacOverlayToggles } from '@/app/components/LiveMapTacOverlayToggles';

const filterSelect =
  'h-9 min-w-[10rem] rounded-lg border border-gray-200 bg-white px-2.5 text-sm font-medium text-gray-900 shadow-sm outline-none focus:ring-2 focus:ring-sky-500 dark:border-gray-700 dark:bg-gray-900 dark:text-white';

/**
 * Presentational controls and canvas for the live world map.
 */
export function LiveWorldMapView(props: any) {
  const {
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
    activeOnly,
    setActiveTouched,
    setActiveOnlyManual,
    overlayScale,
    setOverlayScale,
    tempUnit,
    setTempUnit,
    annex3Mode,
    overlaysMode,
    temperaturesMode,
    countries,
    visible,
    message,
    status,
  } = props;
  return (
    <div className="flex flex-col gap-3" data-testid="live-world-map">
      <div className="rounded-2xl border border-gray-200 bg-white p-3 shadow-sm dark:border-gray-800 dark:bg-gray-950">
        <p className="mb-3 text-xs text-gray-500 dark:text-gray-400">
          <span data-testid="live-map-beta">{DECODE_VISUALS_BETA}</span>
          {'. '}
          <a className="underline" href={DECODE_VISUALS_FEEDBACK_URL}>
            {DECODE_VISUALS_FEEDBACK}
          </a>
        </p>
        <div
          className="mb-3 flex flex-wrap items-center gap-2"
          role="radiogroup"
          aria-label={LIVE_MAP_MODE_GROUP}
          data-testid="live-map-mode-group"
        >
          <span className="text-[11px] font-semibold tracking-wide text-gray-400 uppercase">
            {LIVE_MAP_MODE_GROUP}
          </span>
          {LIVE_MAP_DISPLAY_MODES.map((mode) => {
            const on = displayMode === mode.id;
            return (
              <label
                key={mode.id}
                className={`inline-flex cursor-pointer items-center rounded-full border px-3 py-1 text-sm font-medium transition ${
                  on
                    ? 'border-gray-900 bg-gray-900 text-white dark:border-white dark:bg-white dark:text-gray-900'
                    : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300'
                }`}
              >
                <input
                  type="radio"
                  className="sr-only"
                  name="live-map-display-mode"
                  checked={on}
                  data-testid={`live-map-mode-${mode.id}`}
                  onChange={() => {
                    setDisplayMode((current) => selectLiveMapMode(current, mode.id));
                  }}
                />
                {mode.label}
              </label>
            );
          })}
        </div>
        {annex3Mode ? (
          <div className="flex flex-col gap-2" data-testid="live-map-annex3-products">
            {LIVE_MAP_VIEWS.map((view) => (
              <div key={view.id} className="flex flex-wrap items-center gap-2">
                <span className="w-24 text-[11px] font-semibold tracking-wide text-gray-400 uppercase">
                  {view.label}
                </span>
                {view.products.map((product) => {
                  const on = !off.has(product);
                  const color = pinColor(product);
                  return (
                    <label
                      key={product}
                      className={`inline-flex cursor-pointer items-center gap-2 rounded-full border px-3 py-1 text-sm font-medium transition ${
                        on
                          ? 'border-transparent text-white shadow-sm'
                          : 'border-gray-200 bg-gray-50 text-gray-500 hover:border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-400'
                      }`}
                      style={on ? { backgroundColor: color } : undefined}
                    >
                      <input
                        type="checkbox"
                        className="sr-only"
                        checked={on}
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
                        className={`inline-block h-2 w-2 rounded-full ${on ? 'bg-white' : ''}`}
                        style={on ? undefined : { backgroundColor: color }}
                      />
                      {productLabel(product)}
                    </label>
                  );
                })}
              </div>
            ))}
          </div>
        ) : null}
        <div className="mt-3 flex flex-wrap items-end gap-2 border-t border-gray-100 pt-3 dark:border-gray-800">
          <label className="flex flex-col gap-1 text-[11px] font-semibold tracking-wide text-gray-400 uppercase">
            {LIVE_MAP_FILTER_COUNTRY}
            <select
              className={filterSelect}
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
          <label className="flex flex-col gap-1 text-[11px] font-semibold tracking-wide text-gray-400 uppercase">
            {LIVE_MAP_FILTER_REGION}
            <select
              className={filterSelect}
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
          <label className="flex flex-col gap-1 text-[11px] font-semibold tracking-wide text-gray-400 uppercase">
            {LIVE_MAP_FILTER_TIME}
            <select
              className={filterSelect}
              value={timePreset}
              data-testid="live-map-time"
              onChange={(event) => {
                setTimePreset(event.target.value as MapTimePreset);
              }}
            >
              <option value="latest">{LIVE_MAP_SHOW_LATEST}</option>
              <option value="1h">{LIVE_MAP_LAST_HOUR}</option>
              <option value="3h">{LIVE_MAP_LAST_3_HOURS}</option>
              <option value="6h">{LIVE_MAP_LAST_6_HOURS}</option>
              <option value="12h">{LIVE_MAP_LAST_12_HOURS}</option>
              <option value="full">{LIVE_MAP_FULL_WINDOW}</option>
            </select>
          </label>
        </div>
        <div className="mt-3 flex flex-wrap items-center gap-2 border-t border-gray-100 pt-3 dark:border-gray-800">
          <label
            className={`inline-flex cursor-pointer items-center gap-2 rounded-full border px-3 py-1 text-sm font-medium transition ${
              activeOnly
                ? 'border-gray-900 bg-gray-900 text-white dark:border-white dark:bg-white dark:text-gray-900'
                : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300'
            }`}
          >
            <input
              type="checkbox"
              role="switch"
              className="sr-only"
              checked={activeOnly}
              aria-checked={activeOnly}
              aria-label={LIVE_MAP_FILTER_ACTIVE}
              data-testid="live-map-filter-active-reports"
              onChange={() => {
                setActiveTouched(true);
                setActiveOnlyManual(!activeOnly);
              }}
            />
            {LIVE_MAP_FILTER_ACTIVE}
          </label>
        </div>
        {annex3Mode ? (
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <span className="text-[11px] font-semibold tracking-wide text-gray-400 uppercase">
              {LIVE_MAP_FILTER_PHENOMENON}
            </span>
            {LIVE_MAP_PHENOMENA.map((item) => {
              const on = phenomena.has(item.id);
              return (
                <label
                  key={item.id}
                  className={`inline-flex cursor-pointer items-center rounded-full border px-3 py-1 text-sm font-medium transition ${
                    on
                      ? 'border-gray-900 bg-gray-900 text-white dark:border-white dark:bg-white dark:text-gray-900'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300'
                  }`}
                >
                  <input
                    type="checkbox"
                    className="sr-only"
                    checked={on}
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
              );
            })}
          </div>
        ) : null}
        {overlaysMode ? (
          <>
            <LiveMapTacOverlayToggles
              visibility={tacOverlays}
              places={visible}
              onToggle={(id) => {
                setTacOverlays((current) => toggleTacOverlay(current, id));
              }}
            />
            <label
              className="mt-2 flex flex-col gap-1 text-[11px] font-semibold tracking-wide text-gray-400 uppercase"
              data-testid="live-map-overlay-scale"
            >
              {LIVE_MAP_OVERLAY_SCALE}
              <input
                type="range"
                min={0.5}
                max={2}
                step={0.1}
                value={overlayScale}
                data-testid="live-map-overlay-scale-slider"
                onChange={(event) => {
                  setOverlayScale(
                    clampOverlayMagnitudeScale(Number(event.target.value)),
                  );
                }}
              />
            </label>
          </>
        ) : null}
        {temperaturesMode ? (
          <div
            className="mt-3 flex flex-wrap items-center gap-2 border-t border-gray-100 pt-3 dark:border-gray-800"
            role="radiogroup"
            aria-label={LIVE_MAP_TEMP_UNIT}
            data-testid="live-map-temp-unit-group"
          >
            <span className="text-[11px] font-semibold tracking-wide text-gray-400 uppercase">
              {LIVE_MAP_TEMP_UNIT}
            </span>
            {(
              [
                ['C', LIVE_MAP_TEMP_C],
                ['F', LIVE_MAP_TEMP_F],
              ] as const
            ).map(([unit, label]) => {
              const on = tempUnit === unit;
              return (
                <label
                  key={unit}
                  className={`inline-flex cursor-pointer items-center rounded-full border px-3 py-1 text-sm font-medium transition ${
                    on
                      ? 'border-orange-800 bg-orange-800 text-white'
                      : 'border-gray-200 bg-white text-gray-600 hover:border-gray-300 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    className="sr-only"
                    name="live-map-temp-unit"
                    checked={on}
                    data-testid={`live-map-temp-unit-${unit}`}
                    onChange={() => {
                      setTempUnit((current) => selectTempUnit(current, unit));
                    }}
                  />
                  {label}
                </label>
              );
            })}
          </div>
        ) : null}
      </div>
      <div className="flex flex-wrap items-center justify-between gap-2 px-1">
        <p
          className="text-xs text-gray-500 dark:text-gray-400"
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
          <p
            className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700 dark:bg-gray-800 dark:text-gray-200"
            data-testid="live-map-status"
          >
            {status}
          </p>
        )}
      </div>
      <p
        id="live-map-notice"
        className="px-1 text-xs text-gray-400 dark:text-gray-500"
        data-testid="live-map-notice"
      >
        {LIVE_MAP_NOTICE}
      </p>
      <p className="px-1 text-xs text-gray-400">{LIVE_MAP_ZOOM_HINT}</p>
      <div
        ref={host}
        role="region"
        aria-label={LIVE_MAP_CANVAS}
        aria-describedby="live-map-notice"
        className="z-0 h-[min(70dvh,44rem)] min-h-[24rem] w-full overflow-hidden rounded-2xl border border-gray-200 shadow-sm dark:border-gray-800"
        data-testid="live-map-canvas"
      />
    </div>
  );
}
