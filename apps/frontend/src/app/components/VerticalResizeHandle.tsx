/**
 * Drag handle to grow or shrink a Convert panel vertically.
 *
 * [Corpus: product §F7]
 */

import { useEffect, useRef } from 'react';

import { clampVerticalResizeHeight } from '/utils/verticalResize';

/**
 * Props for {@link VerticalResizeHandle}.
 * @example
 * const _ = true;
 */
export interface VerticalResizeHandleProps {
  height: number;
  onHeightChange: (height: number) => void;
  label: string;
  testId?: string;
}

/**
 * Horizontal separator the operator can drag to resize a pane.
 *
 * @param props.height - Current pane height in pixels
 * @param props.onHeightChange - Height setter
 * @param props.label - Accessible name for the separator
 * @returns Resize handle button
 * @example
 * const _ = true;
 */
export function VerticalResizeHandle({
  height,
  onHeightChange,
  label,
  testId = 'vertical-resize-handle',
}: VerticalResizeHandleProps) {
  const dragCleanup = useRef<(() => void) | null>(null);

  useEffect(() => () => dragCleanup.current?.(), []);

  const startDrag = (event: React.PointerEvent<HTMLButtonElement>) => {
    const startY = event.clientY;
    const startHeight = height;
    const move = (ev: PointerEvent) => {
      onHeightChange(clampVerticalResizeHeight(startHeight, ev.clientY - startY));
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

  const nudge = (key: string) => {
    if (key === 'ArrowDown') {
      onHeightChange(clampVerticalResizeHeight(height, 16));
      return;
    }
    if (key === 'ArrowUp') {
      onHeightChange(clampVerticalResizeHeight(height, -16));
    }
  };

  return (
    <button
      type="button"
      role="separator"
      aria-orientation="horizontal"
      aria-label={label}
      aria-valuenow={Math.round(height)}
      data-testid={testId}
      className="mt-1 flex h-2 w-full cursor-row-resize items-center justify-center rounded bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600"
      onPointerDown={startDrag}
      onKeyDown={(event) => nudge(event.key)}
    >
      <span
        className="h-0.5 w-8 rounded bg-gray-400 dark:bg-gray-500"
        aria-hidden="true"
      />
    </button>
  );
}
