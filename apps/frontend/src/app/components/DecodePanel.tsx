/**
 * Collapsible Code | Explanation decode panel (UJ-015 / #702).
 */

import { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';

export interface DecodeSegmentView {
  start: number;
  end: number;
  code: string;
  explanation: string;
}

export interface DecodeResidualView {
  start: number;
  end: number;
  text: string;
}

export interface DecodePanelProps {
  segments: DecodeSegmentView[];
  residuals: DecodeResidualView[];
  product?: string;
  loading?: boolean;
  error?: string | null;
  defaultOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
}

/**
 * Renders ordered decode segments and explicit residuals.
 *
 * @param props.segments - Annotated TAC spans
 * @param props.residuals - Undecoded spans (G4)
 */
export function DecodePanel({
  segments,
  residuals,
  product,
  loading = false,
  error = null,
  defaultOpen = false,
  onOpenChange,
}: DecodePanelProps) {
  const [open, setOpen] = useState(defaultOpen);

  const toggle = () => {
    setOpen((prev) => {
      const next = !prev;
      onOpenChange?.(next);
      return next;
    });
  };

  return (
    <section
      className="mt-3 rounded-md border border-gray-200 dark:border-gray-700"
      aria-label="TAC decode panel"
      data-testid="decode-panel"
    >
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

      {open ? (
        <div className="border-t border-gray-200 px-3 py-3 dark:border-gray-700">
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
              <div className="mb-2 grid grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)] gap-2 text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                <div>Code</div>
                <div>Explanation</div>
              </div>
              {segments.length === 0 && residuals.length === 0 ? (
                <p className="text-sm text-gray-500">No decode segments yet.</p>
              ) : (
                <ul className="space-y-1" data-testid="decode-segments">
                  {segments.map((seg) => (
                    <li
                      key={`seg-${seg.start}-${seg.end}-${seg.code}`}
                      className="grid grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)] gap-2 rounded px-1 py-1 text-sm hover:bg-gray-50 dark:hover:bg-gray-800/80"
                      data-start={seg.start}
                      data-end={seg.end}
                    >
                      <code className="truncate font-mono text-gray-900 dark:text-gray-100">
                        {seg.code}
                      </code>
                      <span className="text-gray-700 dark:text-gray-300">
                        {seg.explanation}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
              {residuals.length > 0 ? (
                <div className="mt-3" data-testid="decode-residuals">
                  <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-amber-700 dark:text-amber-300">
                    Residuals
                  </h3>
                  <ul className="space-y-1">
                    {residuals.map((r) => (
                      <li
                        key={`res-${r.start}-${r.end}`}
                        className="rounded bg-amber-50 px-2 py-1 font-mono text-xs text-amber-950 dark:bg-amber-950/40 dark:text-amber-100"
                        data-start={r.start}
                        data-end={r.end}
                      >
                        {r.text}
                      </li>
                    ))}
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
