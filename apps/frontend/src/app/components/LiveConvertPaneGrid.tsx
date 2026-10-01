/**
 * Three Convert panes with optional resize handles on a wide screen.
 */

import { Children, useEffect, useRef, type ReactNode } from 'react';
import { resizePanePair } from '/utils/liveConvertLayout';

/**
 * Type `LiveConvertPaneGridProps`.
 * @example
 * const _ = true;
 */
export interface LiveConvertPaneGridProps {
  wide: boolean;
  widths: [number, number, number];
  onWidthsChange: (widths: [number, number, number]) => void;
  children: ReactNode;
}

const LABELS = [
  'Resize TAC and decode panes',
  'Resize decode and IWXXM panes',
] as const;

/**
 * Lay out TAC, decode, and IWXXM. Wide screens can drag the boundaries.
 *
 * @param props.wide - Side-by-side layout
 * @param props.widths - Pane shares
 * @param props.children - The three panes
 * @example
 * const _ = true;
 */
export function LiveConvertPaneGrid({
  wide,
  widths,
  onWidthsChange,
  children,
}: LiveConvertPaneGridProps) {
  const gridRef = useRef<HTMLDivElement>(null);
  const dragCleanup = useRef<(() => void) | null>(null);

  useEffect(() => () => dragCleanup.current?.(), []);

  const startDrag = (boundary: 0 | 1, event: React.PointerEvent<HTMLButtonElement>) => {
    const startX = event.clientX;
    const startWidths = widths;
    const host = gridRef.current as HTMLDivElement;
    const measured = host.getBoundingClientRect().width;
    const width = measured > 0 ? measured : 1;
    const move = (ev: PointerEvent) => {
      const deltaPercent = ((ev.clientX - startX) / width) * 100;
      onWidthsChange(resizePanePair(startWidths, boundary, deltaPercent));
    };
    const stop = () => {
      window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', stop);
      dragCleanup.current = null;
    };
    dragCleanup.current = stop;
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', stop);
  };

  const nudge = (boundary: 0 | 1, key: string) => {
    const delta = key === 'ArrowRight' ? 2 : key === 'ArrowLeft' ? -2 : 0;
    if (delta === 0) {
      return;
    }
    onWidthsChange(resizePanePair(widths, boundary, delta));
  };

  const panes = Children.toArray(children);

  if (!wide) {
    return (
      <div
        className="grid grid-cols-1 gap-3 xl:grid-cols-3 xl:items-stretch"
        data-testid="live-convert-panes"
      >
        {children}
      </div>
    );
  }

  return (
    <div
      ref={gridRef}
      className="grid items-stretch gap-3"
      data-testid="live-convert-panes"
      style={{
        gridTemplateColumns: `${widths[0]}fr 0.5rem ${widths[1]}fr 0.5rem ${widths[2]}fr`,
      }}
    >
      {panes[0]}
      <button
        type="button"
        role="separator"
        aria-orientation="vertical"
        aria-label={LABELS[0]}
        className="cursor-col-resize rounded bg-gray-200 dark:bg-gray-700"
        onPointerDown={(event) => startDrag(0, event)}
        onKeyDown={(event) => nudge(0, event.key)}
      />
      {panes[1]}
      <button
        type="button"
        role="separator"
        aria-orientation="vertical"
        aria-label={LABELS[1]}
        className="cursor-col-resize rounded bg-gray-200 dark:bg-gray-700"
        onPointerDown={(event) => startDrag(1, event)}
        onKeyDown={(event) => nudge(1, event.key)}
      />
      {panes[2]}
    </div>
  );
}
