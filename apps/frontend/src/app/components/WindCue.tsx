/**
 * Wind direction cue for a decoded report (F7 / F9).
 */

import {
  windCueEmptyLabel,
  windCueFromSegments,
  type WindCueModel,
} from '@/utils/decodeVisuals';

/**
 * Type `WindCueProps`.
 * @example
 * const _ = true;
 */
type WindCueProps = {
  segments: { code: string; explanation: string }[];
};

/**
 * Arrow for a numeric wind direction, or a sentence when direction is missing.
 *
 * @param props.segments - Decode rows
 * @example
 * const _ = true;
 */
export function WindCue({ segments }: WindCueProps) {
  const cue: WindCueModel | null = windCueFromSegments(segments);
  const label = cue?.label ?? windCueEmptyLabel();
  const degrees = cue?.degrees;
  return (
    <div data-testid="wind-cue" className="flex items-center gap-3">
      {typeof degrees === 'number' ? (
        <svg
          viewBox="0 0 48 48"
          role="img"
          aria-label={label}
          className="h-12 w-12"
          data-testid="wind-cue-arrow"
        >
          <circle cx="24" cy="24" r="20" fill="none" stroke="#64748b" />
          <line
            x1="24"
            y1="24"
            x2="24"
            y2="8"
            stroke="#0369a1"
            strokeWidth="3"
            transform={`rotate(${degrees} 24 24)`}
          />
        </svg>
      ) : null}
      <p className="text-sm text-gray-800 dark:text-gray-100">{label}</p>
    </div>
  );
}
