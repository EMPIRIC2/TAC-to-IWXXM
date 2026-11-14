/**
 * Live local + UTC clock under the Live decode heading.
 *
 * [Corpus: product §F9] [Corpus: product §F10] [Corpus: ui-style]
 */

import { useEffect, useState } from 'react';
import {
  formatLiveDecodeCurrentTime,
  readShowLiveDecodeCurrentTime,
  writeShowLiveDecodeCurrentTime,
} from '../../utils/liveDecodeCurrentTime';

const TICK_MS = 1000;

/**
 * Props for {@link LiveDecodeCurrentTime}.
 */
export interface LiveDecodeCurrentTimeProps {
  /** Optional IANA zone override (tests). */
  timeZone?: string;
  /** Injectable clock (tests). */
  now?: () => Date;
}

/**
 * Compact Now clock with optional Show current time toggle (default ON).
 *
 * @param props - optional zone / now injection for tests
 * @returns current-time row for pinned Live decode
 */
export function LiveDecodeCurrentTime({
  timeZone,
  now = () => new Date(),
}: LiveDecodeCurrentTimeProps) {
  const [show, setShow] = useState(() => readShowLiveDecodeCurrentTime());
  const [label, setLabel] = useState(
    () => formatLiveDecodeCurrentTime(now(), timeZone).label,
  );

  useEffect(() => {
    if (!show) {
      return;
    }
    const tick = () => {
      setLabel(formatLiveDecodeCurrentTime(now(), timeZone).label);
    };
    tick();
    const id = window.setInterval(tick, TICK_MS);
    return () => window.clearInterval(id);
  }, [show, timeZone, now]);

  const onToggle = (checked: boolean) => {
    setShow(checked);
    writeShowLiveDecodeCurrentTime(checked);
  };

  return (
    <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1">
      <label className="inline-flex items-center gap-1.5 text-xs text-gray-600 dark:text-gray-300">
        <input
          type="checkbox"
          className="h-3.5 w-3.5 rounded border-gray-300 text-sky-700 focus:ring-sky-600 dark:border-gray-600"
          checked={show}
          data-testid="live-decode-current-time-toggle"
          aria-label="Show current time"
          onChange={(event) => onToggle(event.target.checked)}
        />
        Show current time
      </label>
      {show ? (
        <p
          className="font-mono text-xs text-gray-700 dark:text-gray-200"
          data-testid="live-decode-current-time"
          aria-live="polite"
        >
          {label}
        </p>
      ) : null}
    </div>
  );
}
