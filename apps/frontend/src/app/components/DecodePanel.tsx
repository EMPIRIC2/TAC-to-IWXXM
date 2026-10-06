/**
 * Collapsible Code | Explanation decode panel (UJ-015 / #702).
 */

import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

/**
 * Type `DecodeSegmentView`.
 * @example
 * const _ = true;
 */
export interface DecodeSegmentView {
  start: number;
  end: number;
  code: string;
  explanation: string;
}

/**
 * Type `DecodeResidualView`.
 * @example
 * const _ = true;
 */
export interface DecodeResidualView {
  start: number;
  end: number;
  text: string;
}

/**
 * Type `DecodePanelProps`.
 * @example
 * const _ = true;
 */
export interface DecodePanelProps {
  segments: DecodeSegmentView[];
  residuals: DecodeResidualView[];
  /** Deterministic plain-language paragraph from decode-tac (F9 / ADR-025). */
  summary?: string;
  product?: string;
  loading?: boolean;
  error?: string | null;
  defaultOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  /** Keep the reading visible. The live Convert screen uses this. */
  pinned?: boolean;
  /** Decoding profile that produced these rows. */
  decodingProfile?: string;
  selectedStart?: number;
  selectedEnd?: number;
  onSelect?: (target: { start: number; end: number; code: string }) => void;
  /** Detailed shows the explanation. Compact shows the TAC group only. */
  density?: 'detailed' | 'compact';
}

/**
 * Renders ordered decode segments and explicit residuals.
 *
 * @param props.segments - Annotated TAC spans
 * @param props.residuals - Undecoded spans (G4)
 * @param props.summary - Optional plain-language report summary (F9)
 * @example
 * const _ = true;
 */
export function DecodePanel({
  segments,
  residuals,
  summary = '',
  product,
  loading = false,
  error = null,
  defaultOpen = false,
  onOpenChange,
  pinned = false,
  decodingProfile,
  selectedStart,
  selectedEnd,
  onSelect,
  density = 'detailed',
}: DecodePanelProps) {
  const [open, setOpen] = useState(defaultOpen);
  const shown = pinned || open;

  const toggle = () => {
    setOpen((prev) => {
      const next = !prev;
      onOpenChange?.(next);
      return next;
    });
  };

  return (
    <section
      className={
        pinned
          ? 'flex max-h-80 min-h-0 min-w-0 flex-col overflow-auto rounded-md border border-gray-200 dark:border-gray-700'
          : 'mt-3 rounded-md border border-gray-200 dark:border-gray-700'
      }
      aria-label="TAC decode panel"
      data-testid="decode-panel"
    >
      {pinned ? (
        <h3 className="px-3 py-2 text-sm font-medium text-gray-900 dark:text-white">
          Live decode
          {product ? (
            <span className="ml-1 font-normal text-gray-500 dark:text-gray-400">
              ({product})
            </span>
          ) : null}
        </h3>
      ) : (
        <button
          type="button"
          className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm font-medium text-gray-900 dark:text-white"
          aria-expanded={open}
          onClick={toggle}
        >
          {open ? (
            <ChevronDown className="h-4 w-4 shrink-0" aria-hidden />
          ) : (
            <ChevronRight className="h-4 w-4 shrink-0" aria-hidden />
          )}
          Decode
          {product ? (
            <span className="ml-1 font-normal text-gray-500 dark:text-gray-400">
              ({product})
            </span>
          ) : null}
        </button>
      )}

      {shown ? (
        <div
          className={
            pinned
              ? 'min-h-0 flex-1 overflow-auto border-t border-gray-200 px-3 py-3 dark:border-gray-700'
              : 'border-t border-gray-200 px-3 py-3 dark:border-gray-700'
          }
        >
          {loading ? (
            <p className="text-sm text-gray-500" role="status">
              Decoding…
            </p>
          ) : null}
          {error ? (
            <p className="text-sm text-red-600 dark:text-red-400" role="alert">
              {error}
            </p>
          ) : null}
          {!loading && !error ? (
            <>
              {decodingProfile ? (
                <p
                  className="mb-2 text-xs text-gray-600 dark:text-gray-300"
                  data-testid="decode-profile-label"
                >
                  Decoding profile: {decodingProfile}
                </p>
              ) : null}
              {density === 'detailed' && summary.trim() ? (
                <div
                  className="mb-3 rounded-md bg-sky-50 px-3 py-2 text-sm text-sky-950 dark:bg-sky-950/40 dark:text-sky-100"
                  data-testid="decode-plain-language"
                >
                  <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-sky-800 dark:text-sky-200">
                    Plain language
                  </h3>
                  <p>{summary}</p>
                </div>
              ) : null}
              <div className="mb-2 grid grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)] gap-2 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                <div>Code</div>
                {density === 'detailed' ? <div>Explanation</div> : null}
              </div>
              {segments.length === 0 && residuals.length === 0 ? (
                <p className="text-sm text-gray-500">No decode segments yet.</p>
              ) : (
                <ul className="space-y-1" data-testid="decode-segments">
                  {segments.map((seg) => {
                    const selected =
                      selectedStart === seg.start && selectedEnd === seg.end;
                    return (
                      <li
                        key={`seg-${seg.start}-${seg.end}-${seg.code}`}
                        data-start={seg.start}
                        data-end={seg.end}
                      >
                        <button
                          type="button"
                          aria-pressed={selected}
                          className={`grid w-full gap-2 rounded px-1 py-1 text-left text-sm hover:bg-gray-50 dark:hover:bg-gray-800/80 ${
                            density === 'detailed'
                              ? 'grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]'
                              : 'grid-cols-1'
                          } ${
                            selected
                              ? 'bg-sky-100 ring-1 ring-sky-700 dark:bg-sky-950 dark:ring-sky-300'
                              : ''
                          }`}
                          onClick={() =>
                            onSelect?.({
                              start: seg.start,
                              end: seg.end,
                              code: seg.code,
                            })
                          }
                        >
                          <code className="truncate font-mono text-gray-900 dark:text-gray-100">
                            {seg.code}
                          </code>
                          {density === 'detailed' ? (
                            <span className="text-gray-700 dark:text-gray-300">
                              {seg.explanation}
                            </span>
                          ) : null}
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}
              {residuals.length > 0 ? (
                <div className="mt-3" data-testid="decode-residuals">
                  <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-amber-700 dark:text-amber-300">
                    Residuals
                  </h3>
                  <ul className="space-y-1">
                    {residuals.map((r) => {
                      const selected =
                        selectedStart === r.start && selectedEnd === r.end;
                      return (
                        <li key={`res-${r.start}-${r.end}`}>
                          <button
                            type="button"
                            aria-pressed={selected}
                            data-start={r.start}
                            data-end={r.end}
                            className={`w-full rounded px-2 py-1 text-left font-mono text-xs ${
                              selected
                                ? 'bg-sky-100 text-sky-950 ring-1 ring-sky-700 dark:bg-sky-950 dark:text-sky-100 dark:ring-sky-300'
                                : 'bg-amber-50 text-amber-950 dark:bg-amber-950/40 dark:text-amber-100'
                            }`}
                            onClick={() =>
                              onSelect?.({
                                start: r.start,
                                end: r.end,
                                code: r.text,
                              })
                            }
                          >
                            <span className="mr-2 font-sans font-semibold">Error</span>
                            {r.text}
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ) : null}
            </>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
